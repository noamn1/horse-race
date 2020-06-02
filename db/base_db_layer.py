from cryptography.fernet import Fernet


class BaseDBLayer:
    __key = b'pRmgMa8T0INjEAfksaq2aafzoZXEuwKI7wDe4c1F8AY='

    def __init__(self, cache):
        self.__cipher_suite = Fernet(self.__key)
        self.__cache = cache

    def _put_in_cache(self, key, val):
        self.__cache.set(key, val, timeout=30)

    def _get_from_cache(self, key):
        return self.__cache.get(key)

    def _delete_from_cache(self, key):
        self.__cache.delete(key)

    def encrypt(self, password):
        password_bytes = bytes(password, "ascii")
        ciphered_password = self.__cipher_suite.encrypt(password_bytes)  # required to be bytes
        return ciphered_password.decode("utf-8")

    def decrypt(self, encryptedpwd):
        password_bytes = bytes(encryptedpwd, "ascii")
        uncipher_text = (self.__cipher_suite.decrypt(password_bytes))
        password_str = bytes(uncipher_text).decode("utf-8")  # convert to string
        return password_str

    def get_horse_by_id(self, horse_id):
        pass

    def get_race_by_id(self, race_id):
        pass

    def create_horse(self, name):
        pass

    def start_race(self, horses):
        pass

    def signup(self, name, email, password):
        pass

    def login(self, email, password):
        pass

    def __connect(self):
        pass

    def shutdown(self):
        pass

