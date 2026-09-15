from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

privateKey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

publicKey = privateKey.public_key()
print(
    privateKey.private_bytes(encoding=serialization.Encoding.PEM,
                             format=serialization.PrivateFormat.TraditionalOpenSSL.PKCS8,
                             encryption_algorithm=serialization.NoEncryption()).decode(),
    publicKey.public_bytes(encoding=serialization.Encoding.PEM,
                           format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()
)