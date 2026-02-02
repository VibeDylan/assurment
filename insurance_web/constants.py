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

UNAVAILABILITY_REASON_CHOICES = [
    ('vacation', _('Vacation')),
    ('sick', _('Sick leave')),
    ('training', _('Training')),
    ('personal', _('Personal')),
    ('other', _('Other')),
]

NOTIFICATION_TYPE_CHOICES = [
    ('appointment_confirmation', _('Appointment Confirmation')),
    ('appointment_reminder', _('Appointment Reminder')),
    ('appointment_cancelled', _('Appointment Cancelled')),
    ('appointment_rescheduled', _('Appointment Rescheduled')),
    ('appointment_moved', _('Appointment Moved')),
    ('appointment_request', _('Appointment Request')),
    ('appointment_accepted', _('Appointment Accepted')),
    ('appointment_rejected', _('Appointment Rejected')),
]