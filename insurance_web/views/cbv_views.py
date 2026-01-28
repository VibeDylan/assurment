from django.views.generic import TemplateView, CreateView, FormView, ListView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth import login
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange

from ..models import User, Appointment, Prediction
from ..forms import CustomUserCreationForm, PredictionForm, AppointmentForm, AdminUserManagementForm, AdminUserRoleForm
from ..prediction_service import calculate_insurance_premium
from ..utils.mixins import ConseillerRequiredMixin, AdminRequiredMixin, UserProfileMixin


class HomeView(TemplateView):
    template_name = 'home.html'


class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'authentification/signup.html'
    success_url = reverse_lazy('insurance_web:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Welcome {self.object.get_full_name() or self.object.email}!')
        return response


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('insurance_web:home')


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
        initial = {}
        profile = self.request.user.profile
        if profile.age is not None:
            initial['age'] = profile.age
        if profile.sex:
            initial['sex'] = profile.sex
        if profile.bmi is not None:
            initial['bmi'] = profile.bmi
        if profile.children is not None:
            initial['children'] = profile.children
        if profile.smoker:
            initial['smoker'] = profile.smoker
        if profile.region:
            initial['region'] = profile.region
        return initial
    
    def form_valid(self, form):
        """Calcule la prime et sauvegarde la prédiction"""
        form_data = form.cleaned_data
        predicted_amount = calculate_insurance_premium(form_data)
        
        Prediction.objects.create(
            user=self.request.user,
            created_by=self.request.user,
            predicted_amount=predicted_amount,
            **form_data
        )
        
        profile = self.request.user.profile
        for key, value in form_data.items():
            setattr(profile, key, value)
        profile.save()
        
        messages.success(self.request, f'Your estimated insurance premium is {predicted_amount:.2f} € per year.')
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                form_data = form.cleaned_data
                context['predicted_amount'] = calculate_insurance_premium(form_data)
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
        available_slots = []
        
        if date_filter:
            try:
                selected_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                start_datetime = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
                end_datetime = start_datetime + timedelta(days=1)
                
                booked_slots = set()
                for apt in existing_appointments.filter(
                    date_time__gte=start_datetime,
                    date_time__lt=end_datetime
                ):
                    slot_start = apt.date_time.replace(minute=0, second=0, microsecond=0)
                    for i in range(apt.duration_minutes // 30):
                        booked_slots.add(slot_start + timedelta(minutes=i * 30))
                
                start_hour = 9
                end_hour = 18
                current_slot = start_datetime.replace(hour=start_hour)
                
                while current_slot.hour < end_hour:
                    if current_slot not in booked_slots and current_slot > timezone.now():
                        available_slots.append(current_slot)
                    current_slot += timedelta(minutes=30)
            except ValueError:
                pass
        
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
        """Valide et crée le rendez-vous"""
        date_time = form.cleaned_data['date_time']
        duration_minutes = form.cleaned_data['duration_minutes']
        
        if date_time <= timezone.now():
            messages.error(self.request, 'You cannot book a time slot in the past.')
            return self.form_invalid(form)
        
        conflicting_appointments = Appointment.objects.filter(
            conseiller=self.conseiller,
            date_time__lt=date_time + timedelta(minutes=duration_minutes),
            date_time__gte=date_time - timedelta(minutes=duration_minutes)
        )
        
        if conflicting_appointments.exists():
            messages.error(self.request, 'This time slot is no longer available. Please choose another one.')
            return self.form_invalid(form)
        
        appointment = form.save(commit=False)
        appointment.conseiller = self.conseiller
        appointment.client = self.request.user
        appointment.save()
        
        messages.success(
            self.request,
            f'Appointment confirmed with {self.conseiller.get_full_name() or self.conseiller.email} '
            f'on {date_time.strftime("%B %d, %Y at %H:%M")}.'
        )
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


class ConseillerDashboardView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        if conseiller.profile.is_admin():
            total_appointments = Appointment.objects.count()
            upcoming_appointments = Appointment.objects.filter(
                date_time__gte=timezone.now()
            ).count()
            next_appointments = Appointment.objects.filter(
                date_time__gte=timezone.now()
            ).order_by('date_time')[:5]
        else:
            total_appointments = Appointment.objects.filter(conseiller=conseiller).count()
            upcoming_appointments = Appointment.objects.filter(
                conseiller=conseiller,
                date_time__gte=timezone.now()
            ).count()
            next_appointments = Appointment.objects.filter(
                conseiller=conseiller,
                date_time__gte=timezone.now()
            ).order_by('date_time')[:5]
        
        context.update({
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'next_appointments': next_appointments,
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
        initial = {}
        if self.client and self.client.profile:
            profile = self.client.profile
            if profile.age is not None:
                initial['age'] = profile.age
            if profile.sex:
                initial['sex'] = profile.sex
            if profile.bmi is not None:
                initial['bmi'] = profile.bmi
            if profile.children is not None:
                initial['children'] = profile.children
            if profile.smoker:
                initial['smoker'] = profile.smoker
            if profile.region:
                initial['region'] = profile.region
        return initial
    
    def form_valid(self, form):
        """Calcule la prime et sauvegarde la prédiction"""
        form_data = form.cleaned_data
        predicted_amount = calculate_insurance_premium(form_data)
        
        Prediction.objects.create(
            user=self.client,
            created_by=self.request.user,
            predicted_amount=predicted_amount,
            **form_data
        )
        
        if self.client:
            profile = self.client.profile
            for key, value in form_data.items():
                setattr(profile, key, value)
            profile.save()
        
        messages.success(self.request, f'Estimated premium: {predicted_amount:.2f} € per year')
        return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = self.client
        if self.request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                form_data = form.cleaned_data
                context['predicted_amount'] = calculate_insurance_premium(form_data)
        return context


class ConseillerCalendarView(ConseillerRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'conseiller/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conseiller = self.request.user
        
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        if year and month:
            try:
                current_date = datetime(int(year), int(month), 1).date()
            except (ValueError, TypeError):
                current_date = datetime.now().date().replace(day=1)
        else:
            current_date = datetime.now().date().replace(day=1)
        
        first_day = current_date.replace(day=1)
        last_day_num = monthrange(current_date.year, current_date.month)[1]
        last_day = current_date.replace(day=last_day_num)
        
        if conseiller.profile.is_admin():
            appointments = Appointment.objects.filter(
                date_time__date__gte=first_day,
                date_time__date__lte=last_day
            ).order_by('date_time')
        else:
            appointments = Appointment.objects.filter(
                conseiller=conseiller,
                date_time__date__gte=first_day,
                date_time__date__lte=last_day
            ).order_by('date_time')
        
        appointments_by_date = {}
        for appointment in appointments:
            day = appointment.date_time.date()
            if day not in appointments_by_date:
                appointments_by_date[day] = []
            appointments_by_date[day].append(appointment)
        
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
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        context.update({
            'calendar_days': calendar_days,
            'current_date': current_date,
            'month_name': month_names[current_date.month],
            'year': current_date.year,
            'prev_month': prev_month,
            'next_month': next_month,
            'today': datetime.now().date(),
            'all_appointments': list(appointments),
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


class AdminDashboardView(AdminRequiredMixin, UserProfileMixin, FormView):
    form_class = AdminUserManagementForm
    template_name = 'admin/dashboard.html'
    success_url = reverse_lazy('insurance_web:admin_dashboard')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f'User {user.get_full_name() or user.email} created successfully '
            f'with role {user.profile.get_role_display()}.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_users': User.objects.count(),
            'total_conseillers': User.objects.filter(profile__role='conseiller').count(),
            'total_appointments': Appointment.objects.count(),
            'total_predictions': Prediction.objects.count(),
        })
        return context


class AdminUserManagementView(AdminRequiredMixin, UserProfileMixin, ListView):
    template_name = 'admin/user_management.html'
    context_object_name = 'users'
    
    def get_queryset(self):
        return User.objects.select_related('profile').all().order_by('-date_joined')


class AdminChangeUserRoleView(AdminRequiredMixin, UserProfileMixin, FormView):
    form_class = AdminUserRoleForm
    template_name = 'admin/change_user_role.html'
    success_url = reverse_lazy('insurance_web:admin_user_management')
    
    def dispatch(self, request, *args, **kwargs):
        self.target_user = get_object_or_404(User, id=kwargs['user_id'])
        if request.user.id == self.target_user.id:
            messages.error(request, "You cannot modify your own role.")
            return redirect('insurance_web:admin_user_management')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'role': self.target_user.profile.role}
    
    def form_valid(self, form):
        new_role = form.cleaned_data.get('role')
        self.target_user.profile.role = new_role
        self.target_user.profile.save()
        messages.success(
            self.request,
            f'The role of {self.target_user.get_full_name() or self.target_user.email} '
            f'has been changed to {self.target_user.profile.get_role_display()}.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context


class AdminToggleUserStatusView(AdminRequiredMixin, UserProfileMixin, TemplateView):
    success_url = reverse_lazy('insurance_web:admin_user_management')
    
    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['user_id'])
        
        if request.user.id == user.id:
            messages.error(request, "You cannot modify your own status.")
            return redirect('insurance_web:admin_user_management')
        
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'The account of {user.get_full_name() or user.email} has been {status}.')
        return redirect(self.success_url)


class AdminDeleteUserView(AdminRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'admin/delete_user.html'
    success_url = reverse_lazy('insurance_web:admin_user_management')
    
    def dispatch(self, request, *args, **kwargs):
        self.target_user = get_object_or_404(User, id=kwargs['user_id'])
        
        if request.user.id == self.target_user.id:
            messages.error(request, "You cannot delete your own account.")
            return redirect('insurance_web:admin_user_management')
        
        if request.method == 'POST':
            user_email = self.target_user.email
            user_name = self.target_user.get_full_name() or user_email
            self.target_user.delete()
            messages.success(request, f'The account of {user_name} has been permanently deleted.')
            return redirect(self.success_url)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context
