from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from ..utils.decorators import admin_required
from ..forms import AdminUserManagementForm, AdminUserRoleForm
from ..models import Profile, Appointment, Prediction

@admin_required
def admin_dashboard(request):
    if request.method == 'POST':
        form = AdminUserManagementForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.get_full_name() or user.email} created successfully with role {user.profile.get_role_display()}.')
            return redirect('insurance_web:admin_dashboard')
    else:
        form = AdminUserManagementForm()
    
    total_users = User.objects.count()
    total_conseillers = User.objects.filter(profile__role='conseiller').count()
    total_appointments = Appointment.objects.count()
    total_predictions = Prediction.objects.count()
    
    context = {
        'form': form,
        'total_users': total_users,
        'total_conseillers': total_conseillers,
        'total_appointments': total_appointments,
        'total_predictions': total_predictions,
    }
    
    return render(request, 'admin/dashboard.html', context)


@admin_required
def admin_user_management(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'admin/user_management.html', {'users': users})


@admin_required
def admin_change_user_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, "You cannot modify your own role.")
        return redirect('insurance_web:admin_user_management')
    
    if request.method == 'POST':
        form = AdminUserRoleForm(request.POST)
        if form.is_valid():
            new_role = form.cleaned_data.get('role')
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f'The role of {user.get_full_name() or user.email} has been changed to {user.profile.get_role_display()}.')
            return redirect('insurance_web:admin_user_management')
    else:
        form = AdminUserRoleForm(initial={'role': user.profile.role})
    
    return render(request, 'admin/change_user_role.html', {
        'form': form,
        'target_user': user
    })


@admin_required
def admin_toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, "You cannot modify your own status.")
        return redirect('insurance_web:admin_user_management')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'The account of {user.get_full_name() or user.email} has been {status}.')
    return redirect('insurance_web:admin_user_management')


@admin_required
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('insurance_web:admin_user_management')
    
    if request.method == 'POST':
        user_email = user.email
        user_name = user.get_full_name() or user_email
        user.delete()
        messages.success(request, f'The account of {user_name} has been permanently deleted.')
        return redirect('insurance_web:admin_user_management')
    
    return render(request, 'admin/delete_user.html', {
        'target_user': user
    })