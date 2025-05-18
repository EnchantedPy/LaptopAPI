from config.settings import SAppSettings
import jwt
import bcrypt

def encode_jwt(
		payload: dict,
		algorithm: str = SAppSettings.jwt_algorithm,
		private_key: str = SAppSettings.jwt_private_key_path.read_text()
):
	encoded = jwt.encode(
		payload=payload,
		algorithm=algorithm,
		key=private_key
	)
	return encoded


def decode_jwt(
		token: str | bytes,
		algorithm: str = SAppSettings.jwt_algorithm,
		public_key: str = SAppSettings.jwt_public_key_path.read_text()
):
	decoded = jwt.decode(
		jwt=token,
		algorithms=[algorithm],
		key=public_key
	)
	return decoded



def hash_password(
		password: str
) -> bytes:
	salt = bcrypt.gensalt()
	pwd_bytes: bytes = password.encode()
	return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
		password: str,
		hashed_password: bytes
) -> bool:
	return bcrypt.checkpw(
		password=password.encode(),
		hashed_password=hashed_password
	)
