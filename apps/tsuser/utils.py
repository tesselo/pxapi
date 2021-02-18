from django.utils import timezone
from tsuser.const import EXPIRING_TOKEN_LIFESPAN


def expired(token):
    """
    Verify the token expiry date.
    """
    return timezone.now() - token.created >= EXPIRING_TOKEN_LIFESPAN
