from django.core.exceptions import ObjectDoesNotExist
from gms.repositories.guest_repository import GuestRepository
from core.logging import get_logger

# Initialize logger for this service
logger = get_logger("guest_service")


class GuestService:

    def __init__(self, repo: GuestRepository):
        self.repo = repo

    def create_guest(self, data):
        email = data.get("email")
        logger.debug(
            "Checking if guest already exists by email",
            extra={
                "email": email
            }
        )

        if self.check_guest_by_email(email):
            logger.warning(
                "Guest creation failed - email already exists",
                extra={
                    "email": email
                }
            )
            raise ValueError("Guest with this email already exists.")

        logger.info(
            "Creating new guest",
            extra={
                "email": email,
                "name": data.get("name"),
                "phone_number": data.get("phone_number")
            }
        )

        guest = self.repo.create_guest(data)

        logger.info(
            "Guest created successfully",
            extra={
                "guest_id": guest.id,
                "email": email
            }
        )

        return guest

    def get_guest_by_id(self, guest_id):
        logger.debug(
            "Fetching guest by ID",
            extra={
                "guest_id": guest_id
            }
        )

        if not self.check_guest_exists(guest_id):
            logger.warning(
                "Guest not found",
                extra={
                    "guest_id": guest_id
                }
            )
            raise ValueError("Guest with this ID does not exist.")

        guest = self.repo.get_guest_by_id(pk=guest_id)

        logger.debug(
            "Guest retrieved successfully",
            extra={
                "guest_id": guest_id,
                "guest_name": guest.name
            }
        )

        return guest

    def update_guest(self, guest_id, data):
        logger.debug(
            "Checking if guest exists before update",
            extra={
                "guest_id": guest_id
            }
        )

        if not self.check_guest_exists(guest_id):
            logger.warning(
                "Guest update failed - guest not found",
                extra={
                    "guest_id": guest_id
                }
            )
            raise ValueError("Guest with this ID does not exist.")

        logger.info(
            "Updating guest",
            extra={
                "guest_id": guest_id,
                "update_fields": list(data.keys()) if data else []
            }
        )

        guest = self.repo.update_guest(pk=guest_id, guest_data=data)

        logger.info(
            "Guest updated successfully",
            extra={
                "guest_id": guest_id,
                "updated_fields": list(data.keys()) if data else []
            }
        )

        return guest

    def delete_guest(self, guest_id):
        logger.debug(
            "Checking if guest exists before deletion",
            extra={
                "guest_id": guest_id
            }
        )

        if not self.check_guest_exists(guest_id):
            logger.warning(
                "Guest deletion failed - guest not found",
                extra={
                    "guest_id": guest_id
                }
            )
            raise ValueError("Guest with this ID does not exist.")

        logger.info(
            "Deleting guest",
            extra={
                "guest_id": guest_id
            }
        )

        self.repo.delete_guest(pk=guest_id)

        logger.info(
            "Guest deleted successfully",
            extra={
                "guest_id": guest_id
            }
        )

    def check_guest_by_email(self, guest_email):
        logger.debug(
            "Checking guest existence by email",
            extra={
                "email": guest_email
            }
        )

        try:
            guest = self.repo.get_guest_by_email(email=guest_email)
            logger.debug(
                "Guest found by email",
                extra={
                    "email": guest_email,
                    "guest_id": guest.id
                }
            )
            return True
        except ObjectDoesNotExist:
            logger.debug(
                "Guest not found by email",
                extra={
                    "email": guest_email
                }
            )
            return False

    def check_guest_exists(self, guest_id):
        logger.debug(
            "Checking guest existence by ID",
            extra={
                "guest_id": guest_id
            }
        )

        try:
            guest = self.repo.get_guest_by_id(pk=guest_id)
            logger.debug(
                "Guest found by ID",
                extra={
                    "guest_id": guest_id,
                    "guest_name": guest.name
                }
            )
            return True
        except ObjectDoesNotExist:
            logger.debug(
                "Guest not found by ID",
                extra={
                    "guest_id": guest_id
                }
            )
            return False

    def get_guests(self, filters=None):
        logger.info(
            "Getting guests list",
            extra={
                "filters": filters or {}
            }
        )

        guests = self.repo.get_guests(filters=filters)

        logger.debug(
            "Retrieved guests list",
            extra={
                "count": len(guests) if hasattr(guests, '__len__') else 'unknown',
                "filters": filters or {}
            }
        )

        return guests

    def get_guest_by_email(self, email):
        """Get guest by email address"""
        logger.debug(
            "Getting guest by email",
            extra={
                "email": email
            }
        )

        guest = self.repo.get_guest_by_email(email=email)

        logger.debug(
            "Guest retrieved by email",
            extra={
                "email": email,
                "guest_id": guest.id if guest else None
            }
        )

        return guest

    def get_guest_with_invitations(self, guest_id):
        """Get guest with invitations prefetched"""
        logger.debug(
            "Getting guest with invitations",
            extra={
                "guest_id": guest_id
            }
        )

        guest = self.repo.get_guest_with_invitations(pk=guest_id)

        logger.debug(
            "Guest with invitations retrieved",
            extra={
                "guest_id": guest_id,
                "guest_name": guest.name if guest else None
            }
        )

        return guest
