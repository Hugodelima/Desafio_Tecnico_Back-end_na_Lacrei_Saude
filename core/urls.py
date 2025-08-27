"""
URL configuration for core project.

Inclui:
- Endpoints da API (profissionais e consultas)
- Autenticação JWT
- Documentação Swagger/OpenAPI
"""

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from profissionais.views import ProfissionalViewSet
from consultas.views import ConsultaViewSet

# Importações para documentação Swagger
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Importar settings para acessar DEBUG
from django.conf import settings

# Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API Lacrei Saúde",
        default_version='v1',
        description="""
        Documentação da API de Gerenciamento de Consultas Médicas - Lacrei Saúde
        
        ## Autenticação
        Esta API utiliza autenticação JWT. Para usar os endpoints protegidos:
        1. Obtenha um token em `/api/auth/token/`
        2. Use o token no header: `Authorization: Bearer <seu_token>`
        
        ## Endpoints Principais
        - **Profissionais**: CRUD de professionals de saúde
        - **Consultas**: Agendamento e gerenciamento de consultas
        - **Autenticação**: Obtenção e refresh de tokens JWT
        
        ## Filtros Disponíveis
        - Por profissional: `?profissional=1`
        - Por data: `?data_inicio=2024-01-01&data_fim=2024-01-31`
        - Por horário: `?horario_inicio=08:00&horario_fim=17:00`
        - Busca: `?search=cardiologista`
        - Ordenação: `?ordering=-data` (mais recente primeiro)
        """,
        terms_of_service="https://www.lacreisaude.com/terms/",
        contact=openapi.Contact(email="contato@lacreisaude.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Configuração dos routers da API
router = routers.DefaultRouter()
router.register(r'profissionais', ProfissionalViewSet, basename='profissional')
router.register(r'consultas', ConsultaViewSet, basename='consulta')

urlpatterns = [
    # Admin do Django
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # Autenticação JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Documentação Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    # Documentação na raiz (opcional)
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-root'),
]

# Configuração adicional para debug - CORRIGIDO: usar settings.DEBUG
if settings.DEBUG:
    urlpatterns += [
        # URLs de debug podem ser adicionadas aqui
    ]