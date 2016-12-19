from falcon import HTTPUnauthorized


class TokenAuthentication(object):
    def _is_token_valid(self, token):
        # TODO: implement this
        return True

    def process_request(self, req, resp):
        token = req.get_param("token")

        if token is None:
            raise HTTPUnauthorized(
                "Authentication error", "An authentication token is required")

        if not self._is_token_valid(token):
            raise HTTPUnauthorized(
                "Authentication error", "Invalid authentication token")
