from django.urls import include, path

app_name = 'iam'

urlpatterns = [
    path('api/', include('iam.api.urls', namespace='api')),
]
