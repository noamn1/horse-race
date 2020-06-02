from datetime import datetime, timedelta
import jwt
from decouple import config


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1, seconds=5),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            config('SECRET_KEY'),
            algorithm='HS256'
        ).decode("utf-8")
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """

    payload = jwt.decode(auth_token, config('SECRET_KEY'))
    return payload['sub']


