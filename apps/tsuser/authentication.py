from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from tsuser.const import GET_QUERY_PARAMETER_AUTH_KEY
from tsuser.utils import expired


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Expiring token authentication.
    """

    def authenticate_credentials(self, key):
        user, token = super(ExpiringTokenAuthentication, self).authenticate_credentials(
            key
        )

        if expired(token):
            raise AuthenticationFailed("Token has expired")

        return (user, token)


class QueryKeyAuthentication(ExpiringTokenAuthentication):
    """
    Read only authentication through GET query parameter.
    """

    def authenticate(self, request):
        # Retrieve token from query url.
        token = request.GET.get(GET_QUERY_PARAMETER_AUTH_KEY, None)
        if token is None:
            return
        return self.authenticate_credentials(token)
