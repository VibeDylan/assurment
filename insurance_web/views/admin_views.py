from django.views.generic import TemplateView, FormView, ListView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _

from ..models import User, Appointment, Prediction
from ..forms import AdminUserManagementForm, AdminUserRoleForm
from ..utils.mixins import AdminRequiredMixin, UserProfileMixin
from ..permissions import check_not_self_action


class AdminDashboardView(AdminRequiredMixin, UserProfileMixin, FormView):
    form_class = AdminUserManagementForm
    template_name = 'admin/dashboard.html'
    success_url = reverse_lazy('insurance_web:admin_dashboard')
    
    def form_valid(self, form): 
        user = form.save()  
        messages.success(
            self.request,
            _('User %(name)s created successfully with role %(role)s.') % {
                'name': user.get_full_name() or user.email,
                'role': user.profile.get_role_display()
            }
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
        try:
            check_not_self_action(request.user, self.target_user, "modify the role")
        except PermissionDenied as e:
            messages.error(request, str(e))
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
            _('The role of %(name)s has been changed to %(role)s.') % {
                'name': self.target_user.get_full_name() or self.target_user.email,
                'role': self.target_user.profile.get_role_display()
            }
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
        
        try:
            check_not_self_action(request.user, user, "modify the status")
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('insurance_web:admin_user_management')
        
        user.is_active = not user.is_active
        user.save()
        
        status = _("activated") if user.is_active else _("deactivated")
        messages.success(
            request, 
            _('The account of %(name)s has been %(status)s.') % {
                'name': user.get_full_name() or user.email,
                'status': status
            }
        )
        return redirect(self.success_url)


class AdminDeleteUserView(AdminRequiredMixin, UserProfileMixin, TemplateView):
    template_name = 'admin/delete_user.html'
    success_url = reverse_lazy('insurance_web:admin_user_management')
    
    def dispatch(self, request, *args, **kwargs):
        self.target_user = get_object_or_404(User, id=kwargs['user_id'])
        
        try:
            check_not_self_action(request.user, self.target_user, "delete")
        except PermissionDenied as e:
            messages.error(request, str(e))
            return redirect('insurance_web:admin_user_management')
        
        if request.method == 'POST':
            user_email = self.target_user.email
            user_name = self.target_user.get_full_name() or user_email
            self.target_user.delete()
            messages.success(
                request, 
                _('The account of %(name)s has been permanently deleted.') % {
                    'name': user_name
                }
            )
            return redirect(self.success_url)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.target_user
        return context
