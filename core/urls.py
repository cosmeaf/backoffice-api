from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# Views de autenticação
from authentication.views import (
    UserRegisterViewSet,
    UserLoginViewSet,
    UserBlockViewSet,
    UserRecoveryViewSet,
    OtpVerifyViewSet,
    ResetPasswordViewSet,
)

# Views do seletivo
from seletivo.views.address_view import AddressViewSet
from seletivo.views.user_data_view import UserDataViewSet
from seletivo.views.allowed_city_view import AllowedCityViewSet
from seletivo.views.persona_view import PersonaViewSet
from seletivo.views.guardian_view import GuardianViewSet
from seletivo.views.contract_view import ContractViewSet
from seletivo.views.registration_data_view import RegistrationDataViewSet
from seletivo.views.verify_data_view import VerifyDataViewSet
from seletivo.views.exam_scheduled_view import (
    ExamLocalViewSet, ExamDateViewSet, ExamHourViewSet, ExamViewSet
)
from enem.views import EnemResultViewSet
from merito_academico.views import RecommendationLetterViewSet, AcademicMeritDocumentViewSet

# Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="BackOffice API",
        default_version='v1',
        description="Documentação da API do sistema BackOffice",
        terms_of_service="https://pdinfinita.dev/terms/",
        contact=openapi.Contact(email="suporte@pdinfinita.dev"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# ROTAS principais
router = DefaultRouter()
router.register(r'auth/register', UserRegisterViewSet, basename='user-register')
router.register(r'auth/login', UserLoginViewSet, basename='user-login')
router.register(r'auth/block', UserBlockViewSet, basename='user-block')
router.register(r'auth/recovery', UserRecoveryViewSet, basename='user-recovery')
router.register(r'auth/otp-verify', OtpVerifyViewSet, basename='otp-verify')
router.register(r'auth/reset-password', ResetPasswordViewSet, basename='reset-password')

# ROTAS do app seletivo
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'user-data', UserDataViewSet, basename='user-data')
router.register(r'allowed-cities', AllowedCityViewSet, basename='allowed-cities')
router.register(r'personas', PersonaViewSet, basename='persona')
router.register(r'exam-scheduling/locals', ExamLocalViewSet, basename='exam-local')
router.register(r'exam-scheduling/dates', ExamDateViewSet, basename='exam-date')
router.register(r'exam-scheduling/hours', ExamHourViewSet, basename='exam-hour')
router.register(r'exam-scheduling/exams', ExamViewSet, basename='exam')
router.register(r'guardians', GuardianViewSet, basename='guardian')
router.register(r'registration-data', RegistrationDataViewSet, basename='registration-data')
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'verify-data/cpf', VerifyDataViewSet, basename='verify-data')

# ROTSA do app enem
router.register(r'enem', EnemResultViewSet, basename='enem')

# ROTAS MERITO ACADEMICO
router.register(r'merito', RecommendationLetterViewSet, basename='merito')
router.register(r'academic-merit/document', AcademicMeritDocumentViewSet, basename='academic-merit-document')

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
  
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
