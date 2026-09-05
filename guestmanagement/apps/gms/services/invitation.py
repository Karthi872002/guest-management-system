from django.db import transaction
from gms.repositories.invitation_repository import InvitationRepository
from gms.tasks import send_invitation_approved_email
from core.logging import get_logger

# Initialize logger for this service
logger = get_logger("invitation_service")


class InvitationService:

    def __init__(self, repo: InvitationRepository):
        self.repo = repo

    def create_invitation(self, data, user_id):
        expected_arrival = data.get("expected_arrival")
        guest_id = data.get("guest_id")

        if self.check_invitation_for_guest(
            guest_id,
            expected_arrival,
        ):
            logger.warning(
                "Invitation creation failed - duplicate invitation for guest",
                extra={
                    "guest_id": guest_id,
                    "expected_arrival": expected_arrival,
                    "user_id": user_id
                }
            )
            raise ValueError(
                "An invitation for this guest already exists "
                "on the specified date."
            )

        data["invited_by"] = user_id
        logger.info(
            "Creating new invitation",
            extra={
                "guest_id": guest_id,
                "user_id": user_id,
                "expected_arrival": expected_arrival
            }
        )

        invitation = self.repo.create_invitation(data)

        logger.info(
            "Invitation created successfully",
            extra={
                "invitation_id": invitation.id,
                "guest_id": guest_id,
                "user_id": user_id
            }
        )

        return invitation

    def _check_approval_permission(self, user, invitation):
        """Check if the given user is allowed to approve/reject the invitation.
        - Cannot be the creator of the invitation.
        - Must have appropriate role (e.g., ADMIN) or is_staff.
        """
        # Prevent the creator from approving/rejecting
        if user.pk == invitation.invited_by.pk:
            raise ValueError(
                "The user who created the invitation cannot approve or reject it."
            )
        # Only staff/admins can approve/reject
        if not user.is_staff:
            raise ValueError(
                "Only staff members are allowed to approve or reject invitations."
            )

    def approve_invitation(self, invitation_id, user):
        logger.info(
            "Attempting to approve invitation",
            extra={
                "invitation_id": invitation_id,
                "user_id": user.id,
                "user_email": user.email
            }
        )

        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        # Log invitation details for debugging
        logger.debug(
            "Retrieved invitation details",
            extra={
                "invitation_id": invitation_id,
                "invitation_status": invitation.status,
                "invited_by_id": invitation.invited_by.id,
                "inviting_user_id": user.id
            }
        )

        self._check_approval_permission(user, invitation)

        if invitation.status != "PENDING":
            logger.warning(
                "Invitation approval failed - not in pending status",
                extra={
                    "invitation_id": invitation_id,
                    "current_status": invitation.status,
                    "user_id": user.id
                }
            )
            raise ValueError(
                "Only pending invitations can be approved."
            )

        # Update the invitation status to APPROVED
        logger.info(
            "Updating invitation status to APPROVED",
            extra={
                "invitation_id": invitation_id,
                "previous_status": invitation.status
            }
        )

        approved_invitation = self.repo.set_status(
            pk=invitation_id,
            status="APPROVED",
        )

        # Send approval email asynchronously after transaction commits
        def send_approval_email():
            logger.info(
                "Sending approval email for invitation",
                extra={
                    "invitation_id": invitation_id,
                    "guest_id": invitation.guest.id,
                    "inviter_id": invitation.invited_by.id
                }
            )
            send_invitation_approved_email.delay(invitation_id)

        transaction.on_commit(send_approval_email)

        logger.info(
            "Invitation approved successfully",
            extra={
                "invitation_id": invitation_id,
                "approved_by_user_id": user.id,
                "guest_id": invitation.guest.id
            }
        )

        return approved_invitation

    def reject_invitation(self, invitation_id, reason, user):
        logger.info(
            "Attempting to reject invitation",
            extra={
                "invitation_id": invitation_id,
                "user_id": user.id,
                "user_email": user.email,
                "reason": reason
            }
        )

        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        # Log invitation details for debugging
        logger.debug(
            "Retrieved invitation details for rejection",
            extra={
                "invitation_id": invitation_id,
                "invitation_status": invitation.status,
                "invited_by_id": invitation.invited_by.id,
                "inviting_user_id": user.id
            }
        )

        self._check_approval_permission(user, invitation)

        if invitation.status != "PENDING":
            logger.warning(
                "Invitation rejection failed - not in pending status",
                extra={
                    "invitation_id": invitation_id,
                    "current_status": invitation.status,
                    "user_id": user.id
                }
            )
            raise ValueError(
                "Only pending invitations can be rejected."
            )

        if not reason:
            logger.warning(
                "Invitation rejection failed - missing reason",
                extra={
                    "invitation_id": invitation_id,
                    "user_id": user.id
                }
            )
            raise ValueError(
                "A rejection reason is required."
            )

        logger.info(
            "Rejecting invitation with reason",
            extra={
                "invitation_id": invitation_id,
                "reason": reason,
                "rejecting_user_id": user.id
            }
        )

        rejected_invitation = self.repo.reject_invitation(
            pk=invitation_id,
            reason=reason,
        )

        logger.info(
            "Invitation rejected successfully",
            extra={
                "invitation_id": invitation_id,
                "rejected_by_user_id": user.id,
                "guest_id": rejected_invitation.guest.id
            }
        )

        return rejected_invitation

    def cancel_invitation(self, invitation_id):
        logger.info(
            "Attempting to cancel invitation",
            extra={
                "invitation_id": invitation_id,
                "user_id": None  # This method doesn't take a user parameter
            }
        )

        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        # Log invitation details for debugging
        logger.debug(
            "Retrieved invitation details for cancellation",
            extra={
                "invitation_id": invitation_id,
                "invitation_status": invitation.status,
                "guest_id": invitation.guest.id if invitation.guest else None,
                "invited_by_id": invitation.invited_by.id if invitation.invited_by else None
            }
        )

        if invitation.status not in ("PENDING", "APPROVED"):
            logger.warning(
                "Invitation cancellation failed - invalid status",
                extra={
                    "invitation_id": invitation_id,
                    "current_status": invitation.status,
                    "user_id": None
                }
            )
            raise ValueError(
                "This invitation cannot be cancelled."
            )

        logger.info(
            "Updating invitation status to CANCELLED",
            extra={
                "invitation_id": invitation_id,
                "previous_status": invitation.status
            }
        )

        cancelled_invitation = self.repo.set_status(
            pk=invitation_id,
            status="CANCELLED",
        )

        logger.info(
            "Invitation cancelled successfully",
            extra={
                "invitation_id": invitation_id,
                "guest_id": cancelled_invitation.guest.id if cancelled_invitation.guest else None,
                "invited_by_id": cancelled_invitation.invited_by.id if cancelled_invitation.invited_by else None
            }
        )

        return cancelled_invitation

    def update_invitation(self, invitation_id, data):
        logger.info(
            "Attempting to update invitation",
            extra={
                "invitation_id": invitation_id,
                "update_fields": list(data.keys()) if data else []
            }
        )

        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        # Log invitation details for debugging
        logger.debug(
            "Retrieved invitation details for update",
            extra={
                "invitation_id": invitation_id,
                "invitation_status": invitation.status
            }
        )

        if invitation.status != "PENDING":
            logger.warning(
                "Invitation update failed - not in pending status",
                extra={
                    "invitation_id": invitation_id,
                    "current_status": invitation.status
                }
            )
            raise ValueError(
                "Only pending invitations can be updated."
            )

        if "status" in data:
            logger.warning(
                "Invitation update failed - attempting to update status directly",
                extra={
                    "invitation_id": invitation_id,
                    "attempted_status": data["status"]
                }
            )
            raise ValueError(
                "Use approve, reject, or cancel operations to change status."
            )

        logger.info(
            "Updating invitation fields",
            extra={
                "invitation_id": invitation_id,
                "fields_to_update": list(data.keys()),
                "current_status": invitation.status
            }
        )

        updated_invitation = self.repo.update_invitation(
            _id=invitation_id,
            data=data,
        )

        logger.info(
            "Invitation updated successfully",
            extra={
                "invitation_id": invitation_id,
                "updated_fields": list(data.keys())
            }
        )

        return updated_invitation

    def list_invitations(self, filters=None):
        logger.debug(
            "Listing invitations",
            extra={
                "filters": filters or {}
            }
        )

        invitations = self.repo.list_invitations(filters=filters)

        logger.debug(
            "Retrieved invitations list",
            extra={
                "count": len(invitations) if hasattr(invitations, '__len__') else 'unknown',
                "filters": filters or {}
            }
        )

        return invitations

    def get_invitations_by_guest(self, guest_id):
        """Get all invitations for a specific guest"""
        return self.repo.get_invitations_by_guest(guest_id=guest_id)

    def delete_invitation(self, invitation_id):
        self.repo.delete_invitation(_id=invitation_id)

    def check_invitation_for_guest(
        self,
        guest_id,
        expected_arrival,
    ):
        invitations = self.repo.get_guest_invitation_by_date(
            guest_id,
            expected_arrival,
        )

        return invitations.exists()
