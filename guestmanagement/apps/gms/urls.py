from django.urls import include, path

app_name = 'gms'

urlpatterns = [
    path('api/', include('gms.api.urls', namespace='api'))

]
