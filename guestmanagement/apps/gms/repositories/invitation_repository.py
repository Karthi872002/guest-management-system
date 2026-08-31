from abc import ABC, abstractmethod
from uuid import UUID

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


class DjangoInvitationRepository(InvitationRepository):
    def get_invitation_by_id(self, _id: UUID):
        return Invitation.objects.get(id=_id)

    def create_invitation(self, data: dict):
        return Invitation.objects.create(**data)

    def update_invitation(self, _id: UUID, data: dict):

        invitation = Invitation.objects.get(id=_id)
        for key, value in data.items():
            setattr(invitation, key, value)
        invitation.save()
        return invitation

    def delete_invitation(self, _id: UUID):
        invitation = Invitation.objects.get(id=_id)
        invitation.delete()
