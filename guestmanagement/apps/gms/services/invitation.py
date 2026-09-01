
class InvitationService:

    def __init__(self, repo):
        self.repo = repo

    def create_invitation(self, data):
        expected_arrival = data.get("expected_arrival")
        guest_id = data.get("guest_id")

        if self.check_invitation_for_guest(
            guest_id,
            expected_arrival,
        ):
            raise ValueError(
                "An invitation for this guest already exists "
                "on the specified date."
            )

        return self.repo.create_invitation(data)

    def approve_invitation(self, invitation_id):
        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        if invitation.status != "PENDING":
            raise ValueError(
                "Only pending invitations can be approved."
            )

        return self.repo.set_status(
            pk=invitation_id,
            status="APPROVED",
        )

    def reject_invitation(self, invitation_id, reason):
        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        if invitation.status != "PENDING":
            raise ValueError(
                "Only pending invitations can be rejected."
            )

        if not reason:
            raise ValueError(
                "A rejection reason is required."
            )

        return self.repo.reject_invitation(
            pk=invitation_id,
            reason=reason,
        )

    def cancel_invitation(self, invitation_id):
        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        if invitation.status not in ("PENDING", "APPROVED"):
            raise ValueError(
                "This invitation cannot be cancelled."
            )

        return self.repo.set_status(
            pk=invitation_id,
            status="CANCELLED",
        )

    def update_invitation(self, invitation_id, data):
        invitation = self.repo.get_invitation_by_id(pk=invitation_id)

        if invitation.status != "PENDING":
            raise ValueError(
                "Only pending invitations can be updated."
            )

        if "status" in data:
            raise ValueError(
                "Use approve, reject, or cancel operations to change status."
            )

        return self.repo.update_invitation(
            _id=invitation_id,
            data=data,
        )

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
