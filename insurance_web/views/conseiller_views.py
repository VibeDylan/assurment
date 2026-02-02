from django.views.generic import TemplateView, FormView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse
from datetime import datetime, timedelta
from calendar import monthrange

from ..models import User, Appointment, Prediction, ConseillerUnavailability
from ..forms import PredictionForm, AppointmentForm, UnavailabilityForm
from ..services import (
    calculate_insurance_premium,
    create_prediction,
    get_profile_initial_data,
)
from ..services.appointment_service import (
    accept_appointment,
    reject_appointment,
    create_appointment,
    check_appointment_conflict,
    get_week_calendar_data,
)
from ..services.notification_service import (
    get_user_notifications,
    get_unread_notifications_count,
    mark_notification_as_read,
    mark_all_notifications_as_read
)
from ..utils.mixins import ConseillerRequiredMixin, UserProfileMixin
from ..exceptions import (
    PredictionError,
    InvalidPredictionDataError,
    ModelNotFoundError,
    AppointmentError,
    AppointmentConflictError,
)


class ConseillerDashboardView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        if conseiller.profile.is_admin():
            total_appointments = Appointment.objects.exclude(status='cancelled').count()
            upcoming_appointments = Appointment.objects.filter(
                date_time__gte=timezone.now()
            ).exclude(status='cancelled').count()
            next_appointments = Appointment.objects.filter(
                date_time__gte=timezone.now()
            ).exclude(status='cancelled').order_by('date_time')[:5]
            pending_appointments = Appointment.objects.filter(
                status='pending',
                date_time__gte=timezone.now()
            ).order_by('date_time')[:10]
        else:
            total_appointments = Appointment.objects.filter(conseiller=conseiller).exclude(status='cancelled').count()
            upcoming_appointments = Appointment.objects.filter(
                conseiller=conseiller,
                date_time__gte=timezone.now()
            ).exclude(status='cancelled').count()
            next_appointments = Appointment.objects.filter(
                conseiller=conseiller,
                date_time__gte=timezone.now()
            ).exclude(status='cancelled').order_by('date_time')[:5]
            pending_appointments = Appointment.objects.filter(
                conseiller=conseiller,
                status='pending',
                date_time__gte=timezone.now()
            ).order_by('date_time')[:10]
        
        # Compter les notifications non lues
        unread_notifications_count = get_unread_notifications_count(conseiller)
        
        context.update({
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'next_appointments': next_appointments,
            'pending_appointments': pending_appointments,
            'unread_notifications_count': unread_notifications_count,
        })
        return context


class ConseillerPredictView(ConseillerRequiredMixin, UserProfileMixin, FormView):
    form_class = PredictionForm
    template_name = 'conseiller/predict_for_client.html'
    
    def dispatch(self, request, *args, **kwargs):
        if 'client_id' in kwargs:
            self.client = get_object_or_404(User, id=kwargs['client_id'])
        else:
            # Si aucun client_id dans l'URL, essayer de le récupérer depuis POST
            self.client = None
        return super().dispatch(request, *args, **kwargs)
    
    def get_available_clients(self):
        """Récupère la liste des clients disponibles pour ce conseiller"""
        conseiller = self.request.user
        if conseiller.profile.is_admin():
            # Les admins peuvent prédire pour tous les utilisateurs sauf les conseillers et admins
            return User.objects.exclude(id=conseiller.id).exclude(
                profile__role__in=['conseiller', 'admin']
            ).order_by('first_name', 'last_name', 'email')
        else:
            # Les conseillers ne peuvent prédire que pour leurs clients (ceux avec qui ils ont des rendez-vous)
            # Utiliser values_list pour éviter les doublons, puis récupérer les utilisateurs
            client_ids = Appointment.objects.filter(
                conseiller=conseiller
            ).values_list('client_id', flat=True).distinct()
            
            return User.objects.filter(id__in=client_ids).order_by('first_name', 'last_name', 'email')
    
    def get_initial(self):
        initial = {}
        if self.client and self.client.profile:
            initial = get_profile_initial_data(self.client.profile)
        return initial
    
    def calculate_bmi(self, weight, height):
        """Calcule le BMI à partir du poids et de la taille"""
        return weight / (height ** 2)
    
    def form_valid(self, form):
        form_data = form.cleaned_data.copy()
        
        # Récupérer le client sélectionné depuis le formulaire ou l'URL
        client_id = self.request.POST.get('client_id') or (self.client.id if self.client else None)
        
        if not client_id:
            messages.error(self.request, _('Please select a client.'))
            return self.form_invalid(form)
        
        try:
            selected_client = User.objects.get(id=client_id)
        except User.DoesNotExist:
            messages.error(self.request, _('Selected client does not exist.'))
            return self.form_invalid(form)
        
        # Calculer le BMI à partir de height et weight
        height = form_data['height']
        weight = form_data['weight']
        bmi = self.calculate_bmi(weight, height)
        form_data['bmi'] = bmi
        
        # Supprimer height et weight car le service attend seulement bmi
        del form_data['height']
        del form_data['weight']
        
        try:
            predicted_amount = calculate_insurance_premium(form_data)
            
            create_prediction(
                user=selected_client,
                created_by=self.request.user,
                form_data=form_data,
                predicted_amount=predicted_amount
            )
            
            creator_name = self.request.user.get_full_name() or self.request.user.email
            client_name = selected_client.get_full_name() or selected_client.email
            messages.success(
                self.request, 
                _('Prediction created successfully for %(client)s. Estimated premium: %(amount).2f € per year. (Predicted by %(creator)s)') % {
                    'client': client_name,
                    'amount': predicted_amount,
                    'creator': creator_name
                }
            )
            
            # Afficher immédiatement le résultat sur la page (sans redirection)
            context = self.get_context_data()
            context['predicted_amount'] = predicted_amount
            context['client'] = selected_client
            context['form'] = self.form_class(initial=get_profile_initial_data(selected_client.profile))
            return self.render_to_response(context)
        except InvalidPredictionDataError as e:
            messages.error(self.request, _('Invalid data: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
        except ModelNotFoundError:
            messages.error(self.request, _('Prediction service is temporarily unavailable. Please try again later.'))
            return self.form_invalid(form)
        except PredictionError as e:
            messages.error(self.request, _('An error occurred: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client
        context['available_clients'] = self.get_available_clients()
        
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                try:
                    form_data = form.cleaned_data.copy()
                    # Calculer le BMI à partir de height et weight
                    height = form_data['height']
                    weight = form_data['weight']
                    bmi = self.calculate_bmi(weight, height)
                    form_data['bmi'] = bmi
                    # Supprimer height et weight car le service attend seulement bmi
                    del form_data['height']
                    del form_data['weight']
                    context['predicted_amount'] = calculate_insurance_premium(form_data)
                except (PredictionError, InvalidPredictionDataError, ModelNotFoundError):
                    pass
        return context


def _get_calendar_clients(conseiller):
    """Clients avec lesquels le conseiller peut créer un RDV (pour le calendrier)."""
    if conseiller.profile.is_admin():
        return User.objects.exclude(id=conseiller.id).exclude(
            profile__role__in=('conseiller', 'admin')
        ).order_by('first_name', 'last_name', 'email')
    client_ids = Appointment.objects.filter(conseiller=conseiller).values_list('client_id', flat=True).distinct()
    return User.objects.filter(id__in=client_ids).order_by('first_name', 'last_name', 'email')


class ConseillerCalendarView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        today = datetime.now().date()
        week_start_str = self.request.GET.get('week_start')
        if week_start_str:
            try:
                week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
            except ValueError:
                week_start = today - timedelta(days=today.weekday())
        else:
            week_start = today - timedelta(days=today.weekday())
        week_data = get_week_calendar_data(conseiller, week_start)
        context.update({
            'week_dates': week_data['week_dates'],
            'hours': week_data['hours'],
            'slot_events': week_data['slot_events'],
            'slots_grid': week_data['slots_grid'],
            'week_start': week_data['week_start'],
            'prev_week': week_start - timedelta(days=7),
            'next_week': week_start + timedelta(days=7),
            'today': today,
            'calendar_clients': _get_calendar_clients(conseiller),
        })
        return context


def _calendar_redirect(week_start=None):
    url = reverse('insurance_web:conseiller_calendar')
    if week_start:
        url += f'?week_start={week_start}'
    return redirect(url)


class ConseillerCalendarCreateAppointmentView(ConseillerRequiredMixin, UserProfileMixin, View):
    """Création d'un rendez-vous depuis le calendrier (POST : client, date, heure, durée, notes)."""
    def post(self, request):
        client_id = request.POST.get('client_id')
        date_str = request.POST.get('date')  # YYYY-MM-DD
        time_str = request.POST.get('time')  # HH:MM
        duration_minutes = request.POST.get('duration_minutes')
        notes = (request.POST.get('notes') or '').strip()
        week_start = request.POST.get('week_start')

        if not client_id:
            messages.error(request, _('Please select a client.'))
            return _calendar_redirect(week_start=week_start)
        client = get_object_or_404(User, id=client_id)
        conseiller = request.user
        if hasattr(client, 'profile') and getattr(client.profile, 'role', None) in ('conseiller', 'admin'):
            messages.error(request, _('You cannot create an appointment with another advisor or admin.'))
            return _calendar_redirect(week_start=week_start)
        if not conseiller.profile.is_admin():
            if not Appointment.objects.filter(conseiller=conseiller, client=client).exists():
                messages.error(request, _('You can only create appointments with your existing clients.'))
                return _calendar_redirect(week_start=week_start)

        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
            t = datetime.strptime(time_str, '%H:%M').time()
        except (ValueError, TypeError):
            messages.error(request, _('Invalid date or time.'))
            return _calendar_redirect(week_start=week_start)
        date_time_naive = datetime.combine(d, t)
        date_time = timezone.make_aware(date_time_naive, timezone.get_current_timezone())

        try:
            dur = int(duration_minutes)
            if dur < 15 or dur > 240:
                raise ValueError('duration')
        except (ValueError, TypeError):
            messages.error(request, _('Duration must be between 15 and 240 minutes.'))
            return _calendar_redirect(week_start=week_start)

        try:
            has_conflict, error_message = check_appointment_conflict(conseiller, date_time, dur)
            if has_conflict:
                messages.error(request, error_message)
                return _calendar_redirect(week_start=week_start)
            appointment = create_appointment(
                conseiller=conseiller,
                client=client,
                date_time=date_time,
                duration_minutes=dur,
                notes=notes,
                created_by_conseiller=True
            )
            messages.success(
                request,
                _('Rendez-vous créé avec %(name)s le %(date)s.') % {
                    'name': client.get_full_name() or client.email,
                    'date': date_time.strftime('%d/%m/%Y à %H:%M')
                }
            )
            return redirect('insurance_web:appointment_detail', appointment_id=appointment.id)
        except AppointmentConflictError as e:
            messages.error(request, str(e))
            return _calendar_redirect(week_start=week_start)
        except AppointmentError as e:
            messages.error(request, _('Erreur : %(error)s') % {'error': str(e)})
            return _calendar_redirect(week_start=week_start)


class AddUnavailabilityView(ConseillerRequiredMixin, UserProfileMixin, FormView):
    """Ajout d'une période d'indisponibilité (vacances, maladie, etc.)."""
    form_class = UnavailabilityForm
    template_name = 'conseiller/add_unavailability.html'

    def form_valid(self, form):
        start = form.cleaned_data['start_datetime']
        end = form.cleaned_data['end_datetime']
        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.get_current_timezone())
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.get_current_timezone())
        if end <= start:
            messages.error(self.request, _('End must be after start.'))
            return self.form_invalid(form)
        ConseillerUnavailability.objects.create(
            conseiller=self.request.user,
            start_datetime=start,
            end_datetime=end,
            reason='other',
            notes=form.cleaned_data.get('notes') or '',
        )
        week_start = (start.date() - timedelta(days=start.date().weekday())).strftime('%Y-%m-%d')
        messages.success(self.request, _('Unavailability period added.'))
        return _calendar_redirect(week_start=week_start)


class DeleteUnavailabilityView(ConseillerRequiredMixin, View):
    """Suppression d'une période d'indisponibilité."""
    def post(self, request, unavailability_id):
        unav = get_object_or_404(ConseillerUnavailability, id=unavailability_id)
        if unav.conseiller != request.user:
            messages.error(request, _('You cannot delete this unavailability.'))
            return redirect('insurance_web:conseiller_calendar')
        week_start = request.POST.get('week_start') or request.GET.get('week_start')
        unav.delete()
        messages.success(request, _('Unavailability removed.'))
        return _calendar_redirect(week_start=week_start)


class ConseillerClientsListView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/clients_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        if conseiller.profile.is_admin():
            # Les admins voient tous les clients avec rendez-vous et tous les utilisateurs
            clients_with_appointments = User.objects.filter(
                appointments_as_client__isnull=False
            ).distinct()
            all_users = User.objects.exclude(id=conseiller.id).exclude(profile__role='conseiller')
            context.update({
                'clients': clients_with_appointments,
                'all_users': all_users,
            })
        else:
            # Les conseillers ne voient que leurs clients (ceux avec qui ils ont des rendez-vous)
            client_ids = Appointment.objects.filter(
                conseiller=conseiller
            ).values_list('client_id', flat=True).distinct()
            
            clients_with_appointments = User.objects.filter(id__in=client_ids).order_by('first_name', 'last_name', 'email')
            context.update({
                'clients': clients_with_appointments,
                'all_users': None,  # Pas de liste "tous les utilisateurs" pour les conseillers
            })
        
        return context


class ConseillerClientDetailView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    """Vue pour afficher les détails d'un client avec ses prédictions"""
    template_name = 'conseiller/client_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(User, id=kwargs['client_id'])
        conseiller = request.user
        
        # Vérifier que le conseiller a bien des rendez-vous avec ce client
        if not conseiller.profile.is_admin():
            has_appointment = Appointment.objects.filter(
                conseiller=conseiller,
                client=self.client
            ).exists()
            if not has_appointment:
                messages.error(request, _('You do not have access to this client.'))
                return redirect('insurance_web:conseiller_clients')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        # Récupérer les prédictions faites par ce conseiller pour ce client
        predictions = Prediction.objects.filter(
            user=self.client,
            created_by=conseiller
        ).order_by('-created_at')
        
        # Récupérer les rendez-vous avec ce client
        appointments = Appointment.objects.filter(
            conseiller=conseiller,
            client=self.client
        ).order_by('-date_time')
        
        context.update({
            'client': self.client,
            'predictions': predictions,
            'appointments': appointments,
        })
        return context


class ConseillerCreateAppointmentView(ConseillerRequiredMixin, UserProfileMixin, FormView):
    """Permet au conseiller de créer un rendez-vous avec un de ses clients."""
    form_class = AppointmentForm
    template_name = 'conseiller/create_appointment.html'

    def dispatch(self, request, *args, **kwargs):
        self.client = get_object_or_404(User, id=kwargs['client_id'])
        conseiller = request.user
        # Le client ne doit pas être conseiller ni admin
        if hasattr(self.client, 'profile') and self.client.profile.role in ('conseiller', 'admin'):
            messages.error(request, _('You cannot create an appointment with another advisor or admin.'))
            return redirect('insurance_web:conseiller_clients')
        if not conseiller.profile.is_admin():
            has_appointment = Appointment.objects.filter(
                conseiller=conseiller,
                client=self.client
            ).exists()
            if not has_appointment:
                messages.error(request, _('You can only create appointments with your existing clients.'))
                return redirect('insurance_web:conseiller_clients')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        date_time = form.cleaned_data['date_time']
        if timezone.is_naive(date_time):
            date_time = timezone.make_aware(date_time, timezone.get_current_timezone())
        duration_minutes = form.cleaned_data['duration_minutes']
        notes = form.cleaned_data.get('notes', '')
        try:
            has_conflict, error_message = check_appointment_conflict(
                self.request.user,
                date_time,
                duration_minutes
            )
            if has_conflict:
                messages.error(self.request, error_message)
                return self.form_invalid(form)
            appointment = create_appointment(
                conseiller=self.request.user,
                client=self.client,
                date_time=date_time,
                duration_minutes=duration_minutes,
                notes=notes,
                created_by_conseiller=True
            )
            messages.success(
                self.request,
                _('Rendez-vous créé avec %(name)s le %(date)s.') % {
                    'name': self.client.get_full_name() or self.client.email,
                    'date': date_time.strftime('%d/%m/%Y à %H:%M')
                }
            )
            return redirect('insurance_web:appointment_detail', appointment_id=appointment.id)
        except AppointmentConflictError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except AppointmentError as e:
            messages.error(self.request, _('Erreur : %(error)s') % {'error': str(e)})
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client
        return context


class DeletePredictionView(ConseillerRequiredMixin, View):
    """Supprime une prédiction"""
    
    def post(self, request, prediction_id):
        try:
            prediction = get_object_or_404(Prediction, id=prediction_id)
            
            # Vérifier que le conseiller a bien créé cette prédiction
            if prediction.created_by != request.user:
                messages.error(request, _('You do not have permission to delete this prediction.'))
                return redirect('insurance_web:conseiller_clients')
            
            client_id = prediction.user.id
            prediction.delete()
            messages.success(request, _('Prediction deleted successfully.'))
            return redirect('insurance_web:conseiller_client_detail', client_id=client_id)
        except Exception as e:
            messages.error(request, _('An error occurred while deleting the prediction: %(error)s') % {'error': e})
            return redirect('insurance_web:conseiller_clients')


class RemoveClientView(ConseillerRequiredMixin, View):
    """Supprime un client en annulant tous les rendez-vous avec lui"""
    
    def post(self, request, client_id):
        try:
            client = get_object_or_404(User, id=client_id)
            conseiller = request.user
            
            # Vérifier que le conseiller a bien des rendez-vous avec ce client
            if not conseiller.profile.is_admin():
                appointments = Appointment.objects.filter(
                    conseiller=conseiller,
                    client=client
                )
                if not appointments.exists():
                    messages.error(request, _('You do not have access to this client.'))
                    return redirect('insurance_web:conseiller_clients')
                
                # Annuler tous les rendez-vous futurs
                future_appointments = appointments.filter(
                    date_time__gte=timezone.now()
                )
                count = future_appointments.count()
                future_appointments.update(status='cancelled')
                
                messages.success(
                    request, 
                    _('Client removed successfully. %(count)s future appointment(s) cancelled.') % {'count': count}
                )
            else:
                # Pour les admins, on peut supprimer tous les rendez-vous
                appointments = Appointment.objects.filter(client=client)
                count = appointments.count()
                appointments.update(status='cancelled')
                messages.success(
                    request,
                    _('Client removed successfully. %(count)s appointment(s) cancelled.') % {'count': count}
                )
            
            return redirect('insurance_web:conseiller_clients')
        except Exception as e:
            messages.error(request, _('An error occurred while removing the client: %(error)s') % {'error': e})
            return redirect('insurance_web:conseiller_clients')


class NotificationListView(UserProfileMixin, TemplateView):
    template_name = 'notifications/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer toutes les notifications ou seulement les non lues
        unread_only = self.request.GET.get('unread', 'false').lower() == 'true'
        notifications = get_user_notifications(user, unread_only=unread_only, limit=50)
        
        # Compter les notifications non lues
        unread_count = get_unread_notifications_count(user)
        
        context.update({
            'notifications': notifications,
            'unread_only': unread_only,
            'unread_count': unread_count,
        })
        return context


class MarkNotificationReadView(UserProfileMixin, View):
    """Supprime une notification lorsqu'elle est marquée comme lue (elle ne réapparaît plus)."""
    
    def post(self, request, notification_id):
        try:
            mark_notification_as_read(notification_id, request.user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, _('Notification supprimée.'))
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, _('Impossible de supprimer la notification : %(error)s') % {'error': e})
        
        return redirect('insurance_web:notifications')


class MarkAllNotificationsReadView(UserProfileMixin, View):
    """Supprime toutes les notifications non lues (considérées comme lues)."""
    
    def post(self, request):
        try:
            count = mark_all_notifications_as_read(request.user)
            messages.success(request, _('%(count)s notification(s) supprimée(s).') % {'count': count})
        except Exception as e:
            messages.error(request, _('Impossible de supprimer les notifications : %(error)s') % {'error': e})
        
        return redirect('insurance_web:notifications')


class AcceptAppointmentView(ConseillerRequiredMixin, View):
    """Accepte un rendez-vous en attente"""
    
    def post(self, request, appointment_id):
        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            accept_appointment(appointment_id, request.user)
            messages.success(request, _('Appointment accepted successfully.'))
        except AppointmentError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _('An error occurred: %(error)s') % {'error': e})
        
        return redirect('insurance_web:conseiller_dashboard')


class RejectAppointmentView(ConseillerRequiredMixin, View):
    """Refuse un rendez-vous en attente"""
    
    def post(self, request, appointment_id):
        reason = request.POST.get('reason', '')
        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            reject_appointment(appointment_id, request.user, reason=reason if reason else None)
            messages.success(request, _('Appointment rejected successfully.'))
        except AppointmentError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, _('An error occurred: %(error)s') % {'error': e})
        
        return redirect('insurance_web:conseiller_dashboard')
