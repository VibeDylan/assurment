from django.utils.translation import gettext_lazy as _

SEX_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female')),
]

SMOKER_CHOICES = [
    ('yes', _('Yes')),
    ('no', _('No')),
]

REGION_CHOICES = [
    ('northwest', _('Northwest')),
    ('northeast', _('Northeast')),
    ('southwest', _('Southwest')),
    ('southeast', _('Southeast')),
]

ROLE_CHOICES = [
    ('user', _('User')),
    ('conseiller', _('Advisor')),
    ('admin', _('Administrator')),
]

APPOINTMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('confirmed', _('Confirmed')),
    ('cancelled', _('Cancelled')),
]

NOTIFICATION_TYPE_CHOICES = [
    ('appointment_confirmation', _('Appointment Confirmation')),
    ('appointment_reminder', _('Appointment Reminder')),
    ('appointment_cancelled', _('Appointment Cancelled')),
    ('appointment_rescheduled', _('Appointment Rescheduled')),
    ('appointment_moved', _('Appointment Moved')),
]