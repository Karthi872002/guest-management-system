from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from gms.dependencies import get_service
from .serializers import GuestSerializer, VisitSerializer, InvitationSerializer


class GuestViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = get_service("guest")

    def create(self, request):
        serializer = GuestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guest = self.service.create_guest(serializer.validated_data)
        return Response(
            GuestSerializer(guest).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        filters = request.query_params.dict()
        guests = self.service.get_guests(filters=filters)
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            guest = self.service.get_guest_by_id(pk)
            serializer = GuestSerializer(guest)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        serializer = GuestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            guest = self.service.update_guest(pk, serializer.validated_data)
            return Response(
                GuestSerializer(guest).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            self.service.delete_guest(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


class InvitationViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = get_service("invitation")

    def create(self, request):
        serializer = InvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.pk  # Get the ID of the authenticated user
        invitation = self.service.create_invitation(
            serializer.validated_data, user_id)
        return Response(
            InvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        filters = request.query_params.dict()
        invitations = self.service.list_invitations(filters=filters)
        serializer = InvitationSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            invitation = self.service.get_invitation_by_id(pk)
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        serializer = InvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invitation = self.service.update_invitation(
                pk, serializer.validated_data)
            return Response(
                InvitationSerializer(invitation).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            self.service.delete_invitation(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            user = request.user
            invitation = self.service.approve_invitation(pk, user)
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        reason = request.data.get('reason')
        if not reason:
            return Response(
                {"error": "Rejection reason is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            invitation = self.service.reject_invitation(
                pk, reason, request.user)
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            invitation = self.service.cancel_invitation(pk)
            serializer = InvitationSerializer(invitation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class VisitViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = get_service("visit")

    def create(self, request):
        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = self.service.create_visit(serializer.validated_data)
        return Response(
            VisitSerializer(visit).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        filters = request.query_params.dict()
        visits = self.service.list_visits(filters=filters)
        serializer = VisitSerializer(visits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            visit = self.service.get_visit_by_id(pk)
            serializer = VisitSerializer(visit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            visit = self.service.update_visit(pk, serializer.validated_data)
            return Response(
                VisitSerializer(visit).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            self.service.delete_visit(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        try:
            visit = self.service.check_out(pk)
            serializer = VisitSerializer(visit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
