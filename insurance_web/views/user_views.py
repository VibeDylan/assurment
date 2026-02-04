from django.views.generic import TemplateView, FormView, ListView, View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy as _lazy
from datetime import datetime

from ..models import User, Appointment, Prediction
from ..forms import PredictionForm, AppointmentForm, ProfileForm
from ..services import (
    calculate_insurance_premium,
    create_prediction,
    calculate_monthly_price,
    get_available_slots,
    check_appointment_conflict,
    create_appointment,
    get_profile_initial_data,
    cancel_appointment,
    reschedule_appointment,
)
from ..utils.mixins import UserProfileMixin
from ..exceptions import (
    PredictionError,
    InvalidPredictionDataError,
    ModelNotFoundError,
    AppointmentError,
    AppointmentConflictError,
)


class ProfileView(UserProfileMixin, TemplateView):
    template_name = 'authentification/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile
        context['edit_mode'] = self.request.GET.get('edit', 'false').lower() == 'true'
        
        predictions = Prediction.objects.filter(user=self.request.user).order_by('-created_at')
        
        from django.core.paginator import Paginator
        paginator = Paginator(predictions, 10)
        page_number = self.request.GET.get('page', 1)
        context['predictions'] = paginator.get_page(page_number)
        
        if context['edit_mode']:
            profile = self.request.user.profile
            initial_data = {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'age': profile.age,
                'sex': profile.sex,
                'height': getattr(profile, 'height', None),
                'weight': getattr(profile, 'weight', None),
                'children': profile.children,
                'smoker': profile.smoker,
                'region': profile.region,
                'additional_info': profile.additional_info,
            }
            context['form'] = ProfileForm(initial=initial_data, user=self.request.user)
        else:
            context['form'] = ProfileForm(user=self.request.user)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Gère la soumission du formulaire d'édition"""
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            profile = user.profile
            profile_fields = ['age', 'sex', 'height', 'weight', 'children', 'smoker', 'region', 'additional_info']
            for field in profile_fields:
                if field in form.cleaned_data:
                    value = form.cleaned_data[field]
                    setattr(profile, field, value)
            if profile.height and profile.weight and profile.height > 0:
                from decimal import Decimal
                profile.bmi = Decimal(str(float(profile.weight) / (float(profile.height) ** 2))).quantize(Decimal('0.01'))
            profile.save()
            
            messages.success(self.request, _('Votre profil à été mis à jour avec succès.'))
            return redirect('insurance_web:profile')
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            context['edit_mode'] = True
            return self.render_to_response(context)


class EditProfileView(UserProfileMixin, FormView):
    form_class = ProfileForm
    template_name = 'authentification/edit_profile.html'
    
    def get_initial(self):
        profile = self.request.user.profile
        return {
            'age': profile.age,
            'sex': profile.sex,
            'height': getattr(profile, 'height', None),
            'weight': getattr(profile, 'weight', None),
            'children': profile.children,
            'smoker': profile.smoker,
            'region': profile.region,
            'additional_info': profile.additional_info,
        }
    
    def form_valid(self, form):
        """Sauvegarde les données du formulaire dans le profil"""
        from decimal import Decimal
        profile = self.request.user.profile
        profile_field_names = ['age', 'sex', 'height', 'weight', 'children', 'smoker', 'region', 'additional_info']
        for field in profile_field_names:
            if field in form.cleaned_data:
                setattr(profile, field, form.cleaned_data[field])
        if profile.height and profile.weight and profile.height > 0:
            profile.bmi = Decimal(str(float(profile.weight) / (float(profile.height) ** 2))).quantize(Decimal('0.01'))
        profile.save()
        messages.success(self.request, _('Votre profil à été mis à jour avec succès.'))
        return redirect('insurance_web:profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class PredictView(UserProfileMixin, FormView):
    form_class = PredictionForm
    template_name = 'predict.html'
    
    def get_initial(self):
        return get_profile_initial_data(self.request.user.profile)

    def calculate_bmi(self, weight, height):
        return weight / (height ** 2)
    
    def form_valid(self, form):
        form_data = form.cleaned_data.copy()
        height = form_data['height']
        weight = form_data['weight']
        bmi = self.calculate_bmi(weight, height)
        form_data['bmi'] = bmi
        del form_data['weight']
        del form_data['height']
    
        try:
            predicted_amount = calculate_insurance_premium(form_data)
            
            create_prediction(
                user=self.request.user,
                created_by=self.request.user,
                form_data=form_data,
                predicted_amount=predicted_amount
            )
            
            # Calculer le prix mensuel
            monthly_pricing = calculate_monthly_price(predicted_amount)
            
            messages.success(self.request, _('Your estimated insurance premium is %(amount).2f € per year.') % {'amount': predicted_amount})
            
            context = self.get_context_data()
            context['predicted_amount'] = predicted_amount
            context['monthly_pricing'] = monthly_pricing
            context['form'] = self.form_class(initial=form.cleaned_data)
            return self.render_to_response(context)
        except InvalidPredictionDataError as e:
            messages.error(self.request, _('Invalid data: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
        except ModelNotFoundError:
            messages.error(self.request, _('Prediction service is temporarily unavailable. Please try again later.'))
            return self.form_invalid(form)
        except PredictionError as e:
            messages.error(self.request, _('An error occurred while processing your prediction: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        if 'predicted_amount' in kwargs:
            context['predicted_amount'] = kwargs['predicted_amount']
        return context


class ConseillersListView(UserProfileMixin, ListView):
    template_name = 'conseillers_list.html'
    context_object_name = 'conseillers'
    
    def get_queryset(self):
        return User.objects.filter(profile__role='conseiller')


class ConseillerAvailabilityView(UserProfileMixin, TemplateView):
    template_name = 'conseiller_availability.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = get_object_or_404(User, id=self.kwargs['conseiller_id'], profile__role='conseiller')
        context['conseiller'] = conseiller
        
        existing_appointments = Appointment.objects.filter(
            conseiller=conseiller,
            date_time__gte=timezone.now()
        ).exclude(status='cancelled').order_by('date_time')
        context['existing_appointments'] = existing_appointments
        
        date_filter = self.request.GET.get('date')
        selected_date = None
        
        if date_filter:
            try:
                selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        available_slots = get_available_slots(conseiller, selected_date, existing_appointments)
        
        context['selected_date'] = selected_date
        context['available_slots'] = available_slots
        return context


class CreateAppointmentView(UserProfileMixin, FormView):
    form_class = AppointmentForm
    template_name = 'create_appointment.html'
    success_url = None 
    
    def dispatch(self, request, *args, **kwargs):
        self.conseiller = get_object_or_404(User, id=kwargs['conseiller_id'], profile__role='conseiller')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        initial = {}
        if self.request.GET.get('date_time'):
            initial['date_time'] = self.request.GET.get('date_time')
        return initial
    
    def form_valid(self, form):
        date_time = form.cleaned_data['date_time']
        duration_minutes = form.cleaned_data['duration_minutes']
        notes = form.cleaned_data.get('notes', '')
        
        try:
            has_conflict, error_message = check_appointment_conflict(
                self.conseiller,
                date_time,
                duration_minutes
            )
            
            if has_conflict:
                messages.error(self.request, error_message)
                return self.form_invalid(form)
            
            create_appointment(
                conseiller=self.conseiller,
                client=self.request.user,
                date_time=date_time,
                duration_minutes=duration_minutes,
                notes=notes
            )
            
            messages.success(
                self.request,
                _('Appointment confirmed with %(name)s on %(date)s.') % {
                    'name': self.conseiller.get_full_name() or self.conseiller.email,
                    'date': date_time.strftime("%B %d, %Y at %H:%M")
                }
            )
        except AppointmentConflictError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except AppointmentError as e:
            messages.error(self.request, _('An error occurred while creating the appointment: %(error)s') % {'error': str(e)})
            return self.form_invalid(form)
        
        return redirect('insurance_web:my_appointments')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conseiller'] = self.conseiller
        return context


class MyAppointmentsView(UserProfileMixin, TemplateView):
    template_name = 'my_appointments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(
            client=self.request.user
        ).exclude(status='cancelled').order_by('date_time')
        
        context['upcoming_appointments'] = appointments.filter(date_time__gte=timezone.now())
        context['past_appointments'] = appointments.filter(date_time__lt=timezone.now())
        context['cancelled_appointments'] = Appointment.objects.filter(
            client=self.request.user,
            status='cancelled'
        ).order_by('-date_time')
        return context


class AppointmentDetailView(UserProfileMixin, TemplateView):
    """Affiche le détail d'un rendez-vous (client, conseiller ou admin)."""
    template_name = 'appointment_detail.html'

    def get(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=kwargs['appointment_id'])
        user = request.user
        # Accès : client du rendez-vous, conseiller du rendez-vous, ou admin
        if user != appointment.client and user != appointment.conseiller:
            if not (hasattr(user, 'profile') and user.profile.is_admin()):
                raise Http404()
        self.appointment = appointment
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.appointment
        context['is_client'] = self.request.user == self.appointment.client
        context['is_conseiller'] = self.request.user == self.appointment.conseiller
        context['is_admin'] = hasattr(self.request.user, 'profile') and self.request.user.profile.is_admin()
        return context


class CancelAppointmentView(UserProfileMixin, View):
    """Annule un rendez-vous (client ou conseiller ou admin)."""

    def post(self, request, appointment_id):
        try:
            cancel_appointment(appointment_id, request.user)
            messages.success(request, _('Rendez-vous annulé.'))
        except AppointmentError as e:
            messages.error(request, str(e))
        return redirect('insurance_web:appointment_detail', appointment_id=appointment_id)


class RescheduleAppointmentView(UserProfileMixin, FormView):
    """Reporter un rendez-vous (client ou conseiller ou admin)."""
    form_class = AppointmentForm
    template_name = 'reschedule_appointment.html'

    def dispatch(self, request, *args, **kwargs):
        self.appointment = get_object_or_404(Appointment, pk=kwargs['appointment_id'])
        user = request.user
        if user != self.appointment.client and user != self.appointment.conseiller:
            if not (hasattr(user, 'profile') and user.profile.is_admin()):
                raise Http404()
        if self.appointment.status == 'cancelled':
            messages.error(request, _('Cannot reschedule a cancelled appointment.'))
            return redirect('insurance_web:appointment_detail', appointment_id=self.appointment.id)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        dt = self.appointment.date_time
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return {
            'date_time': dt,
            'duration_minutes': self.appointment.duration_minutes,
            'notes': self.appointment.notes or '',
        }

    def form_valid(self, form):
        new_date_time = form.cleaned_data['date_time']
        if timezone.is_naive(new_date_time):
            new_date_time = timezone.make_aware(new_date_time, timezone.get_current_timezone())
        duration_minutes = form.cleaned_data['duration_minutes']
        notes = form.cleaned_data.get('notes', '')
        try:
            reschedule_appointment(
                self.appointment.id,
                self.request.user,
                new_date_time,
                duration_minutes=duration_minutes,
                notes=notes,
            )
            messages.success(
                self.request,
                _('Rendez-vous reporté au %(date)s.') % {'date': new_date_time.strftime('%d/%m/%Y à %H:%M')},
            )
        except AppointmentConflictError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except AppointmentError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return redirect('insurance_web:appointment_detail', appointment_id=self.appointment.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.appointment
        context['conseiller'] = self.appointment.conseiller
        return context
