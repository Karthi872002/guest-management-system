from gms.repositories.visit_repository import VisitRepository
from core.logging import get_logger

# Initialize logger for this service
logger = get_logger("visit_service")


class VisitService:

    def __init__(self, repo: VisitRepository):
        self.repo = repo

    def check_in(self, data):
        guest_id = data.get("guest_id")
        expected_arrival = data.get("expected_arrival")

        logger.debug(
            "Checking invitation for guest check-in",
            extra={
                "guest_id": guest_id,
                "expected_arrival": expected_arrival
            }
        )

        if not self.check_invitation_for_guest(
            guest_id,
            expected_arrival,
        ):
            logger.warning(
                "Check-in failed - no valid invitation found",
                extra={
                    "guest_id": guest_id,
                    "expected_arrival": expected_arrival
                }
            )
            raise ValueError(
                "No invitation exists for this guest on the specified date."
            )

        logger.info(
            "Creating visit (check-in) for guest",
            extra={
                "guest_id": guest_id,
                "expected_arrival": expected_arrival
            }
        )

        visit = self.repo.create_visit(data)

        logger.info(
            "Visit created successfully (guest checked in)",
            extra={
                "visit_id": visit.id,
                "guest_id": guest_id,
                "check_in_time": visit.check_in_time.isoformat() if visit.check_in_time else None
            }
        )

        return visit

    def update_visit(self, pk, data):
        logger.debug(
            "Attempting to update visit",
            extra={
                "visit_id": pk,
                "update_fields": list(data.keys()) if data else []
            }
        )

        if "status" in data:
            logger.warning(
                "Visit update failed - attempt to update status directly",
                extra={
                    "visit_id": pk,
                    "attempted_status": data.get("status")
                }
            )
            raise ValueError(
                "Status cannot be updated using update_visit."
            )

        logger.info(
            "Updating visit",
            extra={
                "visit_id": pk,
                "update_fields": list(data.keys()) if data else []
            }
        )

        visit = self.repo.update_visit(
            pk=pk,
            data=data,
        )

        logger.info(
            "Visit updated successfully",
            extra={
                "visit_id": pk,
                "updated_fields": list(data.keys()) if data else []
            }
        )

        return visit

    def list_visits(self, filters=None):
        logger.debug(
            "Listing visits",
            extra={
                "filters": filters or {}
            }
        )

        visits = self.repo.list_visits(filters=filters)

        logger.debug(
            "Retrieved visits list",
            extra={
                "count": len(visits) if hasattr(visits, '__len__') else 'unknown',
                "filters": filters or {}
            }
        )

        return visits

    def check_out(self, visit_id):
        logger.info(
            "Attempting to check out visit",
            extra={
                "visit_id": visit_id
            }
        )

        visit = self.repo.get_visit_by_id(pk=visit_id)

        logger.debug(
            "Retrieved visit for check-out",
            extra={
                "visit_id": visit_id,
                "visit_status": visit.status,
                "check_in_time": visit.check_in_time.isoformat() if visit.check_in_time else None
            }
        )

        if visit.status != "CHECKED_IN":
            logger.warning(
                "Check-out failed - visit not checked in",
                extra={
                    "visit_id": visit_id,
                    "current_status": visit.status
                }
            )
            raise ValueError("Visit is not checked in.")

        logger.info(
            "Completing check-out for visit",
            extra={
                "visit_id": visit_id
            }
        )

        visit = self.repo.complete_check_out(
            pk=visit_id
        )

        logger.info(
            "Visit checked out successfully",
            extra={
                "visit_id": visit_id,
                "check_out_time": visit.check_out_time.isoformat() if visit.check_out_time else None,
                "status": visit.status
            }
        )

        return visit

    def delete_visit(self, visit_id):
        logger.info(
            "Attempting to delete visit",
            extra={
                "visit_id": visit_id
            }
        )

        visit = self.repo.get_visit_by_id(pk=visit_id)

        logger.debug(
            "Retrieved visit for deletion",
            extra={
                "visit_id": visit_id,
                "visit_status": visit.status if visit else None
            }
        )

        self.repo.delete_visit(pk=visit_id)

        logger.info(
            "Visit deleted successfully",
            extra={
                "visit_id": visit_id
            }
        )

    def check_invitation_for_guest(
        self,
        guest_id,
        expected_arrival,
    ):
        logger.debug(
            "Checking invitation existence for guest",
            extra={
                "guest_id": guest_id,
                "expected_arrival": expected_arrival
            }
        )

        invitations = self.repo.get_guest_invitation_by_date(
            guest_id,
            expected_arrival,
        )

        exists = invitations.exists()

        logger.debug(
            "Invitation check result",
            extra={
                "guest_id": guest_id,
                "expected_arrival": expected_arrival,
                "exists": exists
            }
        )

        return exists
