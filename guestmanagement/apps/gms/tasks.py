from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from gms.models import Invitation
from core.logging import get_logger

# Initialize logger for this module using our centralized logger
logger = get_logger("email_task")

@shared_task
def send_invitation_approved_email(invitation_id):
    """
    Send approval email to guest and inviter when an invitation is approved.
    """
    logger.info(
        "Starting to send approval email for invitation",
        extra={
            "invitation_id": invitation_id
        }
    )

    try:
        # Fetch invitation with related guest and invited_by to avoid extra queries
        invitation = Invitation.objects.select_related('guest', 'invited_by').get(id=invitation_id)
    except Invitation.DoesNotExist:
        logger.error(
            "Invitation not found for email sending",
            extra={
                "invitation_id": invitation_id
            }
        )
        return

    guest = invitation.guest
    inviter = invitation.invited_by

    logger.debug(
        "Retrieved invitation details for email",
        extra={
            "invitation_id": invitation_id,
            "guest_id": guest.id,
            "inviter_id": inviter.id,
            "guest_email": guest.email,
            "inviter_email": inviter.email
        }
    )

    # Prepare email context
    context = {
        'invitation': invitation,
        'guest': guest,
        'inviter': inviter,
        'invitation_code': invitation.invitation_code,
        'purpose': invitation.purpose,
        'expected_arrival': invitation.expected_arrival,
        'expected_departure': invitation.expected_departure,
    }

    # Render email template (we'll create a simple one for now)
    # Since we don't have templates yet, we'll create a simple plain text email.
    # For simplicity, we'll just send a plain text message.
    subject = f"Invitation Approved: {invitation.invitation_code}"

    message = f"""
    Hello {guest.name},

    Your invitation to visit has been approved.

    Invitation Details:
    - Invitation Code: {invitation.invitation_code}
    - Purpose: {invitation.purpose}
    - Expected Arrival: {invitation.expected_arrival}
    - Expected Departure: {invitation.expected_departure}
    - Invited By: {inviter.name} ({inviter.email})

    Please bring a valid ID upon arrival.

    Best regards,
    Guest Management System
    """

    # Also send a copy to the inviter
    recipient_list = [guest.email, inviter.email]

    logger.info(
        "Sending approval email",
        extra={
            "invitation_id": invitation_id,
            "subject": subject,
            "recipients": recipient_list
        }
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        logger.info(
            "Approval email sent successfully",
            extra={
                "invitation_id": invitation_id,
                "recipient_count": len(recipient_list),
                "recipients": recipient_list
            }
        )
    except Exception as e:
        logger.error(
            "Failed to send approval email",
            extra={
                "invitation_id": invitation_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )