from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from gms.dependencies import get_service
from .serializers import GuestSerializer


class GuestViewset(viewsets.ViewSet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = get_service("guest")

    def create(self, request):
        serializer = GuestSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        guest = self.service.create_guest(serializer.validated_data)
        return Response(
            GuestSerializer(guest).data,
            status=status.HTTP_201_CREATED
        )
