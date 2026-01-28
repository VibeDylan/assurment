from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange

from ..models import Appointment, User


def get_available_slots(conseiller, selected_date, existing_appointments):
    """Calcule les créneaux disponibles pour un conseiller à une date donnée"""
    available_slots = []
    
    if not selected_date:
        return available_slots
    
    try:
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
    
    return available_slots


def check_appointment_conflict(conseiller, date_time, duration_minutes):
    """Vérifie s'il y a un conflit avec un rendez-vous existant"""
    if date_time <= timezone.now():
        return True, "You cannot book a time slot in the past."
    
    conflicting_appointments = Appointment.objects.filter(
        conseiller=conseiller,
        date_time__lt=date_time + timedelta(minutes=duration_minutes),
        date_time__gte=date_time - timedelta(minutes=duration_minutes)
    )
    
    if conflicting_appointments.exists():
        return True, "This time slot is no longer available. Please choose another one."
    
    return False, None


def create_appointment(conseiller, client, date_time, duration_minutes, notes=''):
    """Crée un nouveau rendez-vous"""
    appointment = Appointment.objects.create(
        conseiller=conseiller,
        client=client,
        date_time=date_time,
        duration_minutes=duration_minutes,
        notes=notes
    )
    return appointment


def get_appointments_for_calendar(conseiller, year=None, month=None):
    """Récupère les rendez-vous pour un calendrier mensuel"""
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
    
    return appointments_by_date, current_date, first_day, last_day_num, last_day
