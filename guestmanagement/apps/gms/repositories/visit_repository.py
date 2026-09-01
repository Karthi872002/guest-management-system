from abc import ABC, abstractmethod
from uuid import UUID

from django.utils import timezone

from gms.models import Visit


class VisitRepository(ABC):
    @abstractmethod
    def get_visit_by_id(self, pk: UUID):
        pass

    @abstractmethod
    def create_visit(self, data: dict):
        pass

    @abstractmethod
    def update_visit(self, pk: UUID, data: dict):
        pass

    @abstractmethod
    def delete_visit(self, pk: UUID):
        pass

    @abstractmethod
    def update_status(self, pk: UUID, status: str):
        pass

    @abstractmethod
    def complete_check_out(self, pk: UUID):
        pass


class DjangoVisitRepository(VisitRepository):
    def get_visit_by_id(self, pk: UUID):
        return Visit.objects.get(pk=pk)

    def create_visit(self, data: dict):

        visit = Visit.objects.create(**data)
        visit.status = "CHECKED_IN"
        visit.check_in_time = timezone.now()
        visit.save()
        return visit

    def update_visit(self, pk: UUID, data: dict):
        visit = Visit.objects.get(pk=pk)
        for key, value in data.items():
            setattr(visit, key, value)
        visit.save()
        return visit

    def update_status(self, pk: UUID, status: str):
        visit = Visit.objects.get(pk=pk)
        visit.status = status
        visit.save()
        return visit

    def delete_visit(self, pk: UUID):
        visit = Visit.objects.get(pk=pk)
        visit.delete()

    def complete_check_out(self, pk: UUID):
        visit = Visit.objects.get(pk=pk)
        visit.status = "CHECKED_OUT"
        visit.check_out_time = timezone.now()
        visit.save()
        return visit
