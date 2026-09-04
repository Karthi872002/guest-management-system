from ast import In

from rest_framework import routers

from .views import GuestViewset, InvitationViewset, VisitViewset

app_name = 'api'

router = routers.DefaultRouter(trailing_slash=False)
router.register('guests', viewset=GuestViewset, basename='guests')
router.register('invitations', viewset=InvitationViewset,
                basename='invitations')
router.register('visits', viewset=VisitViewset, basename='visits')

urlpatterns = [] + router.urls
