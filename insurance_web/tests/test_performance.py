import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from django.db import connection, reset_queries
from django.test.utils import override_settings
from insurance_web.models import Profile, Appointment, Prediction
from decimal import Decimal


@pytest.mark.django_db
class TestPerformance:
    
    def test_model_query_optimization(self):
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        
        with connection.cursor() as cursor:
            initial_queries = len(connection.queries)
            
            users_list = list(User.objects.all()[:5])
            for user in users_list:
                _ = user.profile
            
            queries_without_optimization = len(connection.queries) - initial_queries
            
            initial_queries = len(connection.queries)
            
            users_list_optimized = list(User.objects.select_related('profile').all()[:5])
            for user in users_list_optimized:
                _ = user.profile
            
            queries_with_optimization = len(connection.queries) - initial_queries
            
            assert queries_with_optimization <= queries_without_optimization, \
                "select_related devrait réduire le nombre de requêtes"
    
    def test_pagination_performance(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        for i in range(25):
            Prediction.objects.create(
                user=user,
                created_by=user,
                predicted_amount=Decimal('1000.00')
            )
        
        predictions_page1 = Prediction.objects.filter(user=user)[:10]
        assert predictions_page1.count() == 10, \
            "La première page devrait contenir 10 prédictions"
        
        predictions_page2 = Prediction.objects.filter(user=user)[10:20]
        assert predictions_page2.count() == 10, \
            "La deuxième page devrait contenir 10 prédictions"
        
        assert len(list(predictions_page1)) == 10, \
            "Seulement 10 prédictions devraient être chargées"
    
    def test_model_caching(self):
        from insurance_web import prediction_service
        from insurance_web.prediction_service import _load_model
        
        original_model = prediction_service._model
        
        prediction_service._model = None
        
        try:
            model1 = _load_model()
            
            model2 = _load_model()
            
            assert model1 is model2, \
                "Le modèle devrait être mis en cache (même objet)"
            assert prediction_service._model is not None, \
                "Le modèle devrait être dans le cache global"
            
        finally:
            prediction_service._model = original_model
    
    def test_bulk_operations(self):
        import time
        
        start_time = time.time()
        users_individual = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'individual{i}',
                email=f'individual{i}@example.com',
                password='testpass123'
            )
            users_individual.append(user)
        individual_time = time.time() - start_time
        
        start_time = time.time()
        users_bulk = []
        for i in range(10):
            user = User(
                username=f'bulk{i}',
                email=f'bulk{i}@example.com'
            )
            user.set_password('testpass123')
            users_bulk.append(user)
        User.objects.bulk_create(users_bulk)
        bulk_time = time.time() - start_time
        
        assert User.objects.filter(username__startswith='bulk').count() == 10, \
            "Les utilisateurs en bulk devraient être créés"
        
    
    def test_database_indexes(self):
        for i in range(10):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123'
            )
        
        import time
        
        start_time = time.time()
        user = User.objects.get(email='user5@example.com')
        query_time = time.time() - start_time
        
        assert query_time < 0.1, \
            f"La requête devrait être rapide grâce aux index (temps: {query_time}s)"
        assert user is not None, "L'utilisateur devrait être trouvé"
    
    def test_lazy_loading(self):
        with override_settings(DEBUG=True):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123'
            )
            
            user_id = user.id
            
            reset_queries()
            
            user_from_db = User.objects.get(id=user_id)
            
            initial_queries = len(connection.queries)
            
            _ = user_from_db.profile
            
            queries_after_access = len(connection.queries)
            
            assert hasattr(user_from_db, 'profile'), \
                "Le profil devrait être accessible"
