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