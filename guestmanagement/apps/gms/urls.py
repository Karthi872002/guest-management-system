from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'gms'

urlpatterns = [
    path('api/', include('gms.api.urls', namespace='api')),

]
