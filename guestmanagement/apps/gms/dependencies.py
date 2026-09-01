from gms.services.guest import GuestService
from gms.services.invitation import InvitationService
from gms.services.visit import VisitService

from gms.repositories.guest_repository import DjangoGuestRepository
from gms.repositories.invitation_repository import DjangoInvitationRepository
from gms.repositories.visit_repository import DjangoVisitRepository


services = {
    "guest": GuestService(DjangoGuestRepository()),
    "invitation": InvitationService(DjangoInvitationRepository()),
    "visit": VisitService(DjangoVisitRepository())
}


def get_service(name):
    if name not in services:
        raise ValueError("Given service not found")

    return services[name]
