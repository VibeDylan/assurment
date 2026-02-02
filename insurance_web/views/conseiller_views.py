from django.views.generic import TemplateView, FormView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse
from datetime import datetime, timedelta
from calendar import monthrange

from ..models import User, Appointment
from ..forms import PredictionForm
from ..services import (
    calculate_insurance_premium,
    create_prediction,
    get_appointments_for_calendar,
    get_profile_initial_data
)
from ..services.appointment_service import accept_appointment, reject_appointment
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
            self.client = None
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        if self.client and self.client.profile:
            return get_profile_initial_data(self.client.profile)
        return {}
    
    def form_valid(self, form):
        form_data = form.cleaned_data
        try:
            predicted_amount = calculate_insurance_premium(form_data)
            
            create_prediction(
                user=self.client,
                created_by=self.request.user,
                form_data=form_data,
                predicted_amount=predicted_amount
            )
            
            messages.success(self.request, _('Estimated premium: %(amount).2f € per year') % {'amount': predicted_amount})
        except InvalidPredictionDataError as e:
            messages.error(self.request, _('Invalid data: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
        except ModelNotFoundError:
            messages.error(self.request, _('Prediction service is temporarily unavailable. Please try again later.'))
            return self.form_invalid(form)
        except PredictionError as e:
            messages.error(self.request, _('An error occurred: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
        
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                try:
                    form_data = form.cleaned_data
                    context['predicted_amount'] = calculate_insurance_premium(form_data)
                except (PredictionError, InvalidPredictionDataError, ModelNotFoundError):
                    pass
        return context


class ConseillerCalendarView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        appointments_by_date, current_date, first_day, last_day_num, last_day = get_appointments_for_calendar(
            conseiller, year, month
        )
        
        first_weekday = first_day.weekday()
        calendar_days = []
        
        if first_weekday > 0:
            prev_month = first_day - timedelta(days=first_weekday)
            for i in range(first_weekday):
                day = prev_month + timedelta(days=i)
                calendar_days.append({'date': day, 'is_current_month': False, 'appointments': []})
        
        for day_num in range(1, last_day_num + 1):
            day = current_date.replace(day=day_num)
            calendar_days.append({
                'date': day,
                'is_current_month': True,
                'appointments': appointments_by_date.get(day, [])
            })
        
        remaining_days = 42 - len(calendar_days)
        if remaining_days > 0:
            next_month = last_day + timedelta(days=1)
            for i in range(remaining_days):
                day = next_month + timedelta(days=i)
                calendar_days.append({'date': day, 'is_current_month': False, 'appointments': []})
        
        if current_date.month == 1:
            prev_month = current_date.replace(year=current_date.year - 1, month=12)
        else:
            prev_month = current_date.replace(month=current_date.month - 1)
        
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1)
        
        month_names = ['', _('January'), _('February'), _('March'), _('April'), _('May'), _('June'),
                       _('July'), _('August'), _('September'), _('October'), _('November'), _('December')]
        
        all_appointments = []
        for appointments_list in appointments_by_date.values():
            all_appointments.extend(appointments_list)
        
        context.update({
            'calendar_days': calendar_days,
            'current_date': current_date,
            'month_name': month_names[current_date.month],
            'year': current_date.year,
            'prev_month': prev_month,
            'next_month': next_month,
            'today': datetime.now().date(),
            'all_appointments': all_appointments,
        })
        return context


class ConseillerClientsListView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/clients_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        if conseiller.profile.is_admin():
            clients_with_appointments = User.objects.filter(
                appointments_as_client__isnull=False
            ).distinct()
            all_users = User.objects.exclude(id=conseiller.id).exclude(profile__role='conseiller')
        else:
            clients_with_appointments = User.objects.filter(
                appointments_as_client__conseiller=conseiller
            ).distinct()
            all_users = User.objects.exclude(id=conseiller.id).exclude(
                profile__role='conseiller'
            ).exclude(profile__role='admin')
        
        context.update({
            'clients': clients_with_appointments,
            'all_users': all_users,
        })
        return context


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
    """Marque une notification comme lue"""
    
    def post(self, request, notification_id):
        try:
            mark_notification_as_read(notification_id, request.user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            messages.success(request, _('Notification marked as read.'))
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, _('Failed to mark notification as read: %(error)s') % {'error': e})
        
        return redirect('insurance_web:notifications')


class MarkAllNotificationsReadView(UserProfileMixin, View):
    """Marque toutes les notifications comme lues"""
    
    def post(self, request):
        try:
            count = mark_all_notifications_as_read(request.user)
            messages.success(request, _('%(count)s notification(s) marked as read.') % {'count': count})
        except Exception as e:
            messages.error(request, _('Failed to mark all notifications as read: %(error)s') % {'error': e})
        
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
