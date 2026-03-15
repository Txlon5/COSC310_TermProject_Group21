import hashlib

class PasswordHandler:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hash_password: str) -> bool:
        return PasswordHandler.hash_password(plain_password) == hash_password