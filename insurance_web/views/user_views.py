from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from ..models import User, Appointment, Prediction
from ..forms import PredictionForm, AppointmentForm
from ..services import (
    calculate_insurance_premium,
    create_prediction,
    get_available_slots,
    check_appointment_conflict,
    create_appointment,
    get_profile_initial_data
)
from ..utils.mixins import UserProfileMixin
from ..exceptions import (
    PredictionError,
    InvalidPredictionDataError,
    ModelNotFoundError,
    AppointmentError,
    AppointmentConflictError,
)


class ProfileView(UserProfileMixin, ListView):
    template_name = 'authentification/profile.html'
    context_object_name = 'predictions'
    paginate_by = 10
    
    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class PredictView(UserProfileMixin, FormView):
    form_class = PredictionForm
    template_name = 'predict.html'
    
    def get_initial(self):
        return get_profile_initial_data(self.request.user.profile)
    
    def form_valid(self, form):
        form_data = form.cleaned_data
        try:
            predicted_amount = calculate_insurance_premium(form_data)
            
            create_prediction(
                user=self.request.user,
                created_by=self.request.user,
                form_data=form_data,
                predicted_amount=predicted_amount
            )
            
            messages.success(self.request, f'Your estimated insurance premium is {predicted_amount:.2f} € per year.')
        except InvalidPredictionDataError as e:
            messages.error(self.request, f'Invalid data: {str(e)}')
            return self.form_invalid(form)
        except ModelNotFoundError:
            messages.error(self.request, 'Prediction service is temporarily unavailable. Please try again later.')
            return self.form_invalid(form)
        except PredictionError as e:
            messages.error(self.request, f'An error occurred while processing your prediction: {str(e)}')
            return self.form_invalid(form)
        
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                try:
                    form_data = form.cleaned_data
                    context['predicted_amount'] = calculate_insurance_premium(form_data)
                except (PredictionError, InvalidPredictionDataError, ModelNotFoundError):
                    pass
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
        ).order_by('date_time')
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


class CreateAppointmentView(UserProfileMixin, CreateView):
    form_class = AppointmentForm
    template_name = 'create_appointment.html'
    
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
        except AppointmentConflictError as e:
            messages.error(self.request, str(e))
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
                f'Appointment confirmed with {self.conseiller.get_full_name() or self.conseiller.email} '
                f'on {date_time.strftime("%B %d, %Y at %H:%M")}.'
            )
        except AppointmentConflictError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except AppointmentError as e:
            messages.error(self.request, f'An error occurred while creating the appointment: {str(e)}')
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
        ).order_by('date_time')
        
        context['upcoming_appointments'] = appointments.filter(date_time__gte=timezone.now())
        context['past_appointments'] = appointments.filter(date_time__lt=timezone.now())
        return context
