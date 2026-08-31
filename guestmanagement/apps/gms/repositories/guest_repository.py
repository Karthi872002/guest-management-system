from abc import ABC, abstractmethod
from uuid import UUID

from gms.models import Guest


class GuestRepository(ABC):
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
    def get_guest_by_id(self, pk: UUID):

        return Guest.objects.get(pk=pk)

    def create_guest(self, guest_data: dict):

        return Guest.objects.create(**guest_data)

    def update_guest(self, pk: UUID, guest_data: dict):
        guest = Guest.objects.get(pk=pk)
        for key, value in guest_data.items():
            setattr(guest, key, value)
        guest.save()
        return guest

    def delete_guest(self, pk: UUID):
        guest = Guest.objects.get(pk=pk)
        guest.delete()
