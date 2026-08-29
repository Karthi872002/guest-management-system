from django.db import models

from core.models import BaseModel
from iam.models import User


class Guest(BaseModel):

    name = models.CharField(
        max_length=255
    )
    email = models.EmailField(
        unique=True
    )
    phone_number = models.CharField(
        max_length=255,
        unique=True
    )

    def __str__(self):
        return self.name


class Invitation(BaseModel):
    status_choices = (
        ("PENDING", "Pending"),
        ("Approved", "Approved"),
        ("Cancelled", "Cancelled"),
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    purpose = models.TextField()

    expected_arrival = models.DateTimeField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.guest.name} - {self.invitation_code}"


class Visit(BaseModel):

    status_choices = (
        ("CHECKED_IN", "Checked In"),
        ("CHECKED_OUT", "Checked Out"),
    )
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name="visits"
    )
    check_in_time = models.DateTimeField(
        auto_now_add=True
    )
    check_out_time = models.DateTimeField(
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=status_choices,
        default="CHECKED_IN"
    )

    def __str__(self):
        return f"{self.guest.name} - {self.check_in_time}"
