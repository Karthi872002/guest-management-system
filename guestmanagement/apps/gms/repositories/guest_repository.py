from abc import ABC, abstractmethod
from uuid import UUID

from gms.models import Guest


class GuestRepository(ABC):

    @abstractmethod
    def get_guests(self, filters=None):
        pass

    @abstractmethod
    def get_guest_by_id(self, pk: UUID):
        pass

    @abstractmethod
    def create_guest(self, guest_data: dict):
        pass

    @abstractmethod
    def update_guest(self, pk: UUID, guest_data: dict):
        pass

    @abstractmethod
    def delete_guest(self, pk: UUID):
        pass

    @abstractmethod
    def get_guest_with_invitations(self, pk: UUID):
        pass

    @abstractmethod
    def get_guest_by_email(self, email: str):
        pass


class DjangoGuestRepository(GuestRepository):

    def get_guests(self, filters=None):
        if filters is None:
            filters = {}
        queryset = Guest.objects.filter(
            **filters).prefetch_related('invitations')
        for guest in queryset:
            yield guest

    def get_guest_by_id(self, pk: UUID):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Guest.DoesNotExist(f"Guest with id {pk} does not exist.")

    def create_guest(self, guest_data: dict):
        return Guest.objects.create(**guest_data)

    def update_guest(self, pk: UUID, guest_data: dict):
        guest = self.get_guest_by_id(pk)
        for key, value in guest_data.items():
            setattr(guest, key, value)
        guest.save()
        return guest

    def delete_guest(self, pk: UUID):
        guest = self.get_guest_by_id(pk)
        guest.delete()

    def get_guest_with_invitations(self, pk: UUID):
        return Guest.objects.prefetch_related(
            "invitations"
        ).get(pk=pk)

    def get_guest_by_email(self, email: str):
        try:
            return Guest.objects.get(email=email)
        except Guest.DoesNotExist:
            raise Guest.DoesNotExist(
                f"Guest with email {email} does not exist.")
