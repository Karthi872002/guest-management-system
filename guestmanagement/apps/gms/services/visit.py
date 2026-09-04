from gms.repositories.visit_repository import VisitRepository


class VisitService:

    def __init__(self, repo: VisitRepository):
        self.repo = repo

    def check_in(self, data):
        guest_id = data.get("guest_id")
        expected_arrival = data.get("expected_arrival")

        if not self.check_invitation_for_guest(
            guest_id,
            expected_arrival,
        ):
            raise ValueError(
                "No invitation exists for this guest on the specified date."
            )

        visit = self.repo.create_visit(data)

        return visit

    def update_visit(self, pk, data):
        if "status" in data:
            raise ValueError(
                "Status cannot be updated using update_visit."
            )

        return self.repo.update_visit(
            pk=pk,
            data=data,
        )

    def list_visits(self, filters=None):
        return self.repo.list_visits(filters=filters)

    def check_out(self, visit_id):
        visit = self.repo.get_visit_by_id(pk=visit_id)

        if visit.status != "CHECKED_IN":
            raise ValueError("Visit is not checked in.")

        visit = self.repo.complete_check_out(
            pk=visit_id
        )

        return visit

    def delete_visit(self, visit_id):
        self.repo.delete_visit(pk=visit_id)

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
