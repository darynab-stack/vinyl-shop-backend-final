import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Subscription

logger = logging.getLogger(__name__)


def notify_subscribers(album):
    subscriptions = Subscription.objects.filter(album=album)
    sent = 0

    for subscription in subscriptions:
        user = subscription.user
        send_mail(
            subject=f"«{album.title}» знову в наявності",
            message=(
                f"Вітаємо, {user.username}!\n\n"
                f"Платівка «{album.title}» ({album.artist.name}) знову є в "
                f"наявності у Vinyl Shop. Ціна: {album.price} грн.\n\n"
                "Ви отримали цей лист, бо натиснули «Повідомити про наявність»."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        sent += 1

    subscriptions.delete()
    logger.info("Sent %s back-in-stock emails for album %s", sent, album.id)
    return sent
