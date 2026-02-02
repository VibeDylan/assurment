from django.views.generic import TemplateView, FormView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
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
from ..utils.mixins import ConseillerRequiredMixin, UserProfileMixin
from ..exceptions import (
    PredictionError,
    InvalidPredictionDataError,
    ModelNotFoundError,
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
