from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from gms.dependencies import get_service
from .serializers import GuestSerializer, VisitSerializer, InvitationSerializer
from core.logging import get_logger

# Initialize loggers for each ViewSet
guest_logger = get_logger("guest_api")
invitation_logger = get_logger("invitation_api")
visit_logger = get_logger("visit_api")


class GuestViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = get_service("guest")

    def create(self, request):
        guest_logger.info(
            "Creating guest via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "data_keys": list(request.data.keys()) if request.data else []
            }
        )

        serializer = GuestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guest = self.service.create_guest(serializer.validated_data)

        guest_logger.info(
            "Guest created successfully via API",
            extra={
                "guest_id": guest.id,
                "user_id": request.user.id if request.user.is_authenticated else None
            }
        )

        return Response(
            GuestSerializer(guest).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        filters = request.query_params.dict()
        guest_logger.debug(
            "Listing guests via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "filters": filters
            }
        )

        guests = self.service.get_guests(filters=filters)
        serializer = GuestSerializer(guests, many=True)

        guest_logger.debug(
            "Retrieved guests list via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "count": len(guests) if hasattr(guests, '__len__') else 'unknown'
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            guest_logger.debug(
                "Retrieving guest via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            guest = self.service.get_guest_by_id(pk)
            serializer = GuestSerializer(guest)

            guest_logger.debug(
                "Retrieved guest successfully via API",
                extra={
                    "guest_id": guest.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            guest_logger.warning(
                "Failed to retrieve guest via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        guest_logger.info(
            "Updating guest via API",
            extra={
                "guest_id": pk,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "data_keys": list(request.data.keys()) if request.data else []
            }
        )

        serializer = GuestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            guest = self.service.update_guest(pk, serializer.validated_data)

            guest_logger.info(
                "Guest updated successfully via API",
                extra={
                    "guest_id": guest.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(
                GuestSerializer(guest).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            guest_logger.warning(
                "Failed to update guest via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            guest_logger.info(
                "Deleting guest via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            self.service.delete_guest(pk)

            guest_logger.info(
                "Guest deleted successfully via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            guest_logger.warning(
                "Failed to delete guest via API",
                extra={
                    "guest_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
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
            invitation_logger.info(
                "Attempting to approve invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            user = request.user
            invitation = self.service.approve_invitation(pk, user)
            serializer = InvitationSerializer(invitation)

            invitation_logger.info(
                "Invitation approved successfully via API",
                extra={
                    "invitation_id": invitation.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            invitation_logger.warning(
                "Failed to approve invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        reason = request.data.get('reason')
        if not reason:
            invitation_logger.warning(
                "Invitation rejection failed - missing reason",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )
            return Response(
                {"error": "Rejection reason is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            invitation_logger.info(
                "Attempting to reject invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "reason": reason
                }
            )

            invitation = self.service.reject_invitation(
                pk, reason, request.user)
            serializer = InvitationSerializer(invitation)

            invitation_logger.info(
                "Invitation rejected successfully via API",
                extra={
                    "invitation_id": invitation.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            invitation_logger.warning(
                "Failed to reject invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            invitation_logger.info(
                "Attempting to cancel invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            invitation = self.service.cancel_invitation(pk)
            serializer = InvitationSerializer(invitation)

            invitation_logger.info(
                "Invitation cancelled successfully via API",
                extra={
                    "invitation_id": invitation.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            invitation_logger.warning(
                "Failed to cancel invitation via API",
                extra={
                    "invitation_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
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
        visit_logger.info(
            "Creating visit via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "data_keys": list(request.data.keys()) if request.data else []
            }
        )

        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = self.service.create_visit(serializer.validated_data)

        visit_logger.info(
            "Visit created successfully via API",
            extra={
                "visit_id": visit.id,
                "user_id": request.user.id if request.user.is_authenticated else None
            }
        )

        return Response(
            VisitSerializer(visit).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        filters = request.query_params.dict()
        visit_logger.debug(
            "Listing visits via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "filters": filters
            }
        )

        visits = self.service.list_visits(filters=filters)
        serializer = VisitSerializer(visits, many=True)

        visit_logger.debug(
            "Retrieved visits list via API",
            extra={
                "user_id": request.user.id if request.user.is_authenticated else None,
                "count": len(visits) if hasattr(visits, '__len__') else 'unknown'
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            visit_logger.debug(
                "Retrieving visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            visit = self.service.get_visit_by_id(pk)
            serializer = VisitSerializer(visit)

            visit_logger.debug(
                "Retrieved visit successfully via API",
                extra={
                    "visit_id": visit.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            visit_logger.warning(
                "Failed to retrieve visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, pk=None):
        visit_logger.info(
            "Updating visit via API",
            extra={
                "visit_id": pk,
                "user_id": request.user.id if request.user.is_authenticated else None,
                "data_keys": list(request.data.keys()) if request.data else []
            }
        )

        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            visit = self.service.update_visit(pk, serializer.validated_data)

            visit_logger.info(
                "Visit updated successfully via API",
                extra={
                    "visit_id": visit.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(
                VisitSerializer(visit).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            visit_logger.warning(
                "Failed to update visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            visit_logger.info(
                "Deleting visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            self.service.delete_visit(pk)

            visit_logger.info(
                "Visit deleted successfully via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            visit_logger.warning(
                "Failed to delete visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        try:
            visit_logger.info(
                "Attempting to check out visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            visit = self.service.check_out(pk)
            serializer = VisitSerializer(visit)

            visit_logger.info(
                "Visit checked out successfully via API",
                extra={
                    "visit_id": visit.id,
                    "user_id": request.user.id if request.user.is_authenticated else None
                }
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            visit_logger.warning(
                "Failed to check out visit via API",
                extra={
                    "visit_id": pk,
                    "user_id": request.user.id if request.user.is_authenticated else None,
                    "error": str(e)
                }
            )
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
