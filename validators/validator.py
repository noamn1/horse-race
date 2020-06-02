import jwt

from util import decode_auth_token


class Validator:

    def __init__(self):
        pass

    def validate_token(self, token, user_id):
        try:
            user_id_from_token = decode_auth_token(token)
            if user_id != user_id_from_token:
                raise ValueError('Invalid token. Please log in again.')

        except jwt.ExpiredSignatureError:
            raise ValueError('Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please log in again.')


