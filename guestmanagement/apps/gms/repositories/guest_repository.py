from abc import ABC, abstractmethod
from uuid import UUID

from gms.models import Guest


class GuestRepository(ABC):

    @abstractmethod
    def get_guests(self):
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


class DjangoGuestRepository(GuestRepository):

    def get_guests(self):
        for guest in Guest.objects.all():
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
