from django.views.generic import TemplateView, FormView, ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _, gettext_lazy as _lazy
from datetime import datetime

from ..models import User, Appointment, Prediction
from ..forms import PredictionForm, AppointmentForm, ProfileForm
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
            context['form'] = ProfileForm(user=self.request.user)
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
            # Calculer le BMI si taille et poids sont renseignés
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
        # Recalculer le BMI si taille et poids sont renseignés
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
            
            messages.success(self.request, _('Your estimated insurance premium is %(amount).2f € per year.') % {'amount': predicted_amount})
            
            context = self.get_context_data()
            context['predicted_amount'] = predicted_amount
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
