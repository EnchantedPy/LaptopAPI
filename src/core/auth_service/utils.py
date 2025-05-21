from datetime import datetime, timedelta, timezone
import uuid
import jwt
import bcrypt
from src.entities.entities import User
from config.settings import SAppSettings

ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'
TOKEN_TYPE_FIELD = 'type'

def create_token(
		token_type: str,
		token_data: dict, 
		expire_minutes: int
) -> str:
	jwt_payload = {TOKEN_TYPE_FIELD: token_type}
	jwt_payload.update(token_data)
	return encode_jwt(
		payload=jwt_payload,
		expire_minutes=expire_minutes
	)

def create_access_token(user: User, admin: bool):
	jwt_payload = {
		'sub': str(user.id),
		'name': user.name,
		'email': user.email,
		'role': 'admin' if admin else 'user'
	}
	return create_token(ACCESS_TOKEN_TYPE, jwt_payload, SAppSettings.access_token_expire_minutes)

def create_refresh_token(user: User, admin: bool):
	jwt_payload = {
		'sub': str(user.id),
		'role': 'admin' if admin else 'user'
	}
	return create_token(REFRESH_TOKEN_TYPE, jwt_payload, SAppSettings.refresh_token_expire_minutes)


def encode_jwt(
		payload: dict,
		expire_minutes: int,
		algorithm: str = SAppSettings.jwt_algorithm,
		private_key: str = SAppSettings.jwt_private_key_path.read_text(),
):
	
	to_encode = payload.copy()
	now = datetime.now(timezone.utc)
	exp = now + timedelta(minutes=expire_minutes)
	jti = str(uuid.uuid4())
	to_encode.update(
		exp=exp,
		iat=now,
		jti=jti
		)
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
	decoded['sub'] = int(decoded['sub'])
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
