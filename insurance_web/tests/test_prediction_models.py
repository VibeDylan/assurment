import pytest
from django.contrib.auth.models import User
from insurance_web.models import Prediction
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestPredictionModel:
    def test_prediction_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        created_by_user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            first_name='Creator',
            last_name='User'
        )
        
        prediction = Prediction.objects.create(
            user=user,
            created_by=created_by_user,
            predicted_amount=Decimal('1000.50'),
            age=30,
            sex='male',
            bmi=Decimal('25.75'),
            children=0,
            smoker='no',
            region='northwest'
        )
        
        assert prediction.user == user, "La relation user devrait être correcte"
        assert prediction.created_by == created_by_user, "La relation created_by devrait être correcte"
        
        assert isinstance(prediction.predicted_amount, Decimal), "predicted_amount devrait être un Decimal"
        assert prediction.predicted_amount == Decimal('1000.50'), "Le montant prédit devrait être le bon"
        
        assert prediction.age == 30, "L'âge devrait être le bon"
        assert prediction.sex == 'male', "Le sexe devrait être le bon"
        assert isinstance(prediction.bmi, Decimal), "bmi devrait être un Decimal"
        assert prediction.bmi == Decimal('25.75'), "Le BMI devrait être le bon"
        assert prediction.children == 0, "Le nombre d'enfants devrait être le bon"
        assert prediction.smoker == 'no', "Le statut fumeur/non-fumeur devrait être le bon"
        assert prediction.region == 'northwest', "La région devrait être le bon"
        
        assert prediction.created_at is not None, "created_at devrait être défini automatiquement"

    def test_prediction_str_method(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        created_by_user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            first_name='Creator',
            last_name='User'
        )
        
        prediction = Prediction.objects.create(
            user=user,
            created_by=created_by_user,
            predicted_amount=Decimal('1500.75')
        )
        
        expected_str = f"Prediction for {user.get_full_name()} - {Decimal('1500.75')} €"
        assert str(prediction) == expected_str, "Le __str__ devrait retourner le bon format"
        
        user_no_name = User.objects.create_user(
            username='noname',
            email='noname@example.com',
            password='testpass123'
        )
        prediction2 = Prediction.objects.create(
            user=user_no_name,
            created_by=created_by_user,
            predicted_amount=Decimal('2000')
        )
        expected_str2 = f"Prediction for {user_no_name.email} - {Decimal('2000')} €"
        assert str(prediction2) == expected_str2, "Le __str__ devrait utiliser l'email si le nom complet n'existe pas"

    def test_prediction_ordering(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        created_by_user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            first_name='Creator',
            last_name='User'
        )
        
        prediction1 = Prediction.objects.create(
            user=user,
            created_by=created_by_user,
            predicted_amount=Decimal('1000')
        )
        
        import time
        time.sleep(0.01)
        
        prediction2 = Prediction.objects.create(
            user=user,
            created_by=created_by_user,
            predicted_amount=Decimal('2000')
        )
        
        time.sleep(0.01)
        
        prediction3 = Prediction.objects.create(
            user=user,
            created_by=created_by_user,
            predicted_amount=Decimal('3000')
        )
        
        predictions = list(Prediction.objects.all())
        assert predictions == [prediction3, prediction2, prediction1], \
            "Les prédictions devraient être triées par created_at décroissant (plus récent en premier)"

    def test_prediction_cascade_deletion(self):
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            first_name='User',
            last_name='One'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            first_name='User',
            last_name='Two'
        )
        created_by_user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='testpass123',
            first_name='Creator',
            last_name='User'
        )
        
        prediction1 = Prediction.objects.create(
            user=user1,
            created_by=created_by_user,
            predicted_amount=Decimal('1000')
        )
        prediction2 = Prediction.objects.create(
            user=user2,
            created_by=created_by_user,
            predicted_amount=Decimal('2000')
        )
        
        user1_id = user1.id
        user2_id = user2.id
        created_by_id = created_by_user.id
        
        user1.delete()
        assert not Prediction.objects.filter(user_id=user1_id).exists(), \
            "Les prédictions de user1 devraient être supprimées en cascade"
        assert Prediction.objects.filter(user_id=user2_id).exists(), \
            "Les prédictions de user2 devraient être conservées"
        
        created_by_user.delete()
        assert not Prediction.objects.filter(created_by_id=created_by_id).exists(), \
            "Toutes les prédictions créées par created_by_user devraient être supprimées en cascade"
        assert not Prediction.objects.filter(user_id=user2_id).exists(), \
            "La prédiction de user2 devrait aussi être supprimée car created_by a été supprimé"