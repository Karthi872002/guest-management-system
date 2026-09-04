from django.core.exceptions import ObjectDoesNotExist
from gms.repositories.guest_repository import GuestRepository


class GuestService:

    def __init__(self, repo: GuestRepository):
        self.repo = repo

    def create_guest(self, data):
        if self.check_guest_by_email(data.get("email")):
            print("Guest with this email already exists.")
            raise ValueError("Guest with this email already exists.")
        guest = self.repo.create_guest(data)
        return guest

    def get_guest_by_id(self, guest_id):
        if not self.check_guest_exists(guest_id):
            raise ValueError("Guest with this ID does not exist.")

        print("Fetching guest with ID:", guest_id)
        guest = self.repo.get_guest_by_id(pk=guest_id)
        return guest

    def update_guest(self, guest_id, data):
        if not self.check_guest_exists(guest_id):
            raise ValueError("Guest with this email does not exist.")
        guest = self.repo.update_guest(pk=guest_id, guest_data=data)
        return guest

    def delete_guest(self, guest_id):
        if not self.check_guest_exists(guest_id):
            raise ValueError("Guest with this ID does not exist.")
        self.repo.delete_guest(pk=guest_id)

    def check_guest_by_email(self, guest_email):
        try:
            guest = self.repo.get_guest_by_email(email=guest_email)
            return True
        except ObjectDoesNotExist:
            return False

    def check_guest_exists(self, guest_id):
        try:
            guest = self.repo.get_guest_by_id(pk=guest_id)
            return True
        except ObjectDoesNotExist:
            return False

    def get_guests(self, filters=None):
        return self.repo.get_guests(filters=filters)

    def get_guest_by_email(self, email):
        """Get guest by email address"""
        return self.repo.get_guest_by_email(email=email)

    def get_guest_with_invitations(self, guest_id):
        """Get guest with invitations prefetched"""
        return self.repo.get_guest_with_invitations(pk=guest_id)
