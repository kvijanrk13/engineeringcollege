from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_user_key_pair(password):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    encrypted_private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode("utf-8")),
    )
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return {
        "public_key": public_key_pem.decode("utf-8"),
        "encrypted_private_key": encrypted_private_key_pem.decode("utf-8"),
    }


def generate_oauth_user_key_pair(secret_value):
    return generate_user_key_pair(secret_value)


def load_private_key(encrypted_private_key, password):
    return serialization.load_pem_private_key(
        encrypted_private_key.encode("utf-8"),
        password=password.encode("utf-8"),
    )
