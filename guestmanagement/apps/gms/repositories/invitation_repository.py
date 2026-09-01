from abc import ABC, abstractmethod
from uuid import UUID
import uuid

from gms.models import Invitation


class InvitationRepository(ABC):
    @abstractmethod
    def get_invitation_by_id(self, _id: UUID):
        pass

    @abstractmethod
    def create_invitation(self, data: dict):
        pass

    @abstractmethod
    def update_invitation(self, _id: UUID, data: dict):
        pass

    @abstractmethod
    def delete_invitation(self, _id: UUID):
        pass

    @abstractmethod
    def get_guest_invitation_by_date(self, guest_id: UUID, expected_arrival):
        pass

    @abstractmethod
    def set_status(self, _id: UUID, status: str):
        pass

    @abstractmethod
    def reject_invitation(self, _id: UUID, reason: str):
        pass


class DjangoInvitationRepository(InvitationRepository):
    def get_invitation_by_id(self, _id: UUID):
        return Invitation.objects.get(id=_id)

    def create_invitation(self, data: dict):
        invitation = Invitation.objects.create(**data)
        invitation_code = uuid.uuid4().hex[:8].upper()
        invitation.invitation_code = invitation_code
        invitation.save()
        return invitation

    def update_invitation(self, _id: UUID, data: dict):

        invitation = Invitation.objects.get(id=_id)
        for key, value in data.items():
            setattr(invitation, key, value)
        invitation.save()
        return invitation

    def delete_invitation(self, _id: UUID):
        invitation = Invitation.objects.get(id=_id)
        invitation.delete()

    def get_guest_invitation_by_date(self, guest_id: UUID, expected_arrival):
        return Invitation.objects.filter(
            guest_id=guest_id, expected_arrival=expected_arrival
        )

    def set_status(self, _id: UUID, status: str):
        invitation = Invitation.objects.get(id=_id)
        invitation.status = status
        invitation.save()
        return invitation

    def reject_invitation(self, _id: UUID, reason: str):
        invitation = Invitation.objects.get(id=_id)
        invitation.status = "REJECTED"
        invitation.rejection_reason = reason
        invitation.save()
        return invitation
