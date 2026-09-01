from django.core.exceptions import ObjectDoesNotExist
from gms.repositories import guest_repository


class GuestService:

    def __init__(self, repo):
        self.repo = repo

    def create_guest(self, data):
        if self.check_guest_by_email(data.get("email")):
            raise ValueError("Guest with this email already exists.")
        guest = self.repo.create_guest(data)
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
