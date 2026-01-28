import factory
from django.contrib.auth.models import User
from insurance_web.models import Profile, Appointment, Prediction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


try:
    from factory import django
    FACTORY_BOY_AVAILABLE = True
except ImportError:
    FACTORY_BOY_AVAILABLE = False


if FACTORY_BOY_AVAILABLE:
    class UserFactory(django.DjangoModelFactory):
        class Meta:
            model = User
        
        username = factory.Sequence(lambda n: f"user{n}")
        email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
        first_name = factory.Faker('first_name')
        last_name = factory.Faker('last_name')
        password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    
    class ProfileFactory(django.DjangoModelFactory):
        class Meta:
            model = Profile
        
        user = factory.SubFactory(UserFactory)
        role = 'user'
        age = factory.Faker('random_int', min=18, max=100)
        sex = factory.Iterator(['male', 'female'])
        bmi = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True, min_value=10.0, max_value=50.0)
        children = factory.Faker('random_int', min=0, max=10)
        smoker = factory.Iterator(['yes', 'no'])
        region = factory.Iterator(['northwest', 'northeast', 'southwest', 'southeast'])
    
    class AppointmentFactory(django.DjangoModelFactory):
        class Meta:
            model = Appointment
        
        conseiller = factory.SubFactory(UserFactory)
        client = factory.SubFactory(UserFactory)
        date_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
        duration_minutes = 60
        notes = factory.Faker('text', max_nb_chars=200)
    
    class PredictionFactory(django.DjangoModelFactory):
        class Meta:
            model = Prediction
        
        user = factory.SubFactory(UserFactory)
        created_by = factory.SubFactory(UserFactory)
        predicted_amount = factory.Faker('pyfloat', left_digits=4, right_digits=2, positive=True)
        age = factory.Faker('random_int', min=18, max=100)
        sex = factory.Iterator(['male', 'female'])
        bmi = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True, min_value=10.0, max_value=50.0)
        children = factory.Faker('random_int', min=0, max=10)
        smoker = factory.Iterator(['yes', 'no'])
        region = factory.Iterator(['northwest', 'northeast', 'southwest', 'southeast'])

else:
    def create_user(**kwargs):
        defaults = {
            'username': f"user{User.objects.count() + 1}",
            'email': f"user{User.objects.count() + 1}@test.com",
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(**defaults)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def create_profile(user=None, **kwargs):
        if user is None:
            user = create_user()
        defaults = {
            'role': 'user',
            'age': 30,
            'sex': 'male',
            'bmi': Decimal('22.5'),
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        defaults.update(kwargs)
        profile, created = Profile.objects.get_or_create(user=user, defaults=defaults)
        if not created:
            for key, value in defaults.items():
                setattr(profile, key, value)
            profile.save()
        return profile
    
    def create_appointment(conseiller=None, client=None, **kwargs):
        if conseiller is None:
            conseiller = create_user()
        if client is None:
            client = create_user()
        defaults = {
            'date_time': timezone.now() + timedelta(days=1),
            'duration_minutes': 60,
            'notes': 'Test appointment'
        }
        defaults.update(kwargs)
        return Appointment.objects.create(
            conseiller=conseiller,
            client=client,
            **defaults
        )
    
    def create_prediction(user=None, created_by=None, **kwargs):
        if user is None:
            user = create_user()
        if created_by is None:
            created_by = user
        defaults = {
            'predicted_amount': Decimal('1000.00'),
            'age': 30,
            'sex': 'male',
            'bmi': Decimal('22.5'),
            'children': 0,
            'smoker': 'no',
            'region': 'northwest'
        }
        defaults.update(kwargs)
        return Prediction.objects.create(
            user=user,
            created_by=created_by,
            **defaults
        )
    
    UserFactory = type('UserFactory', (), {'create': staticmethod(create_user)})
    ProfileFactory = type('ProfileFactory', (), {'create': staticmethod(create_profile)})
    AppointmentFactory = type('AppointmentFactory', (), {'create': staticmethod(create_appointment)})
    PredictionFactory = type('PredictionFactory', (), {'create': staticmethod(create_prediction)})
