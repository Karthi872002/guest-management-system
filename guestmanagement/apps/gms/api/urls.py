from rest_framework import routers

from .views import GuestViewset

app_name = 'api'

router = routers.DefaultRouter(trailing_slash=False)
router.register('guests', viewset=GuestViewset, basename='guests')

urlpatterns = [] + router.urls
