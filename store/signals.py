from django.core.mail import send_mail
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Card
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Card)
def send_email_new_card(sender, instance, created, **kwargs):
    logger.info(f"post_save triggered: id={instance.id}, created={created}")
    
    if not created:
        return

    logger.info(f"Card: {instance.name} has been created.")

    try:
        send_mail(
            subject="New card has been created.",
            message=f"Card: {instance.name} has been created.",
            from_email="my_store@magicstore.com",
            recipient_list=["customer@email.com"],
            fail_silently=False,
        )
        logger.info("Email has been sent.")
    except Exception:
        logger.exception("Error to send a Email.")

@receiver(post_delete, sender=Card)
def card_deleted(sender, instance, **kwargs):
    logger.info(f"card {instance.name} deleted.")
