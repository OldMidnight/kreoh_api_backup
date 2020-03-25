from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
from flask import current_app as app
from API.extensions import kreoh_store

def generate_confirmation_token(new_email):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  token = serializer.dumps(new_email, salt=app.config['SECURITY_PASSWORD_SALT'])
  kreoh_store.set(token, 'false', timedelta(seconds=3600))
  return token


def confirm_token(token, expiration=3600):
  serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
  try:
    email = serializer.loads(
      token,
      salt=app.config['SECURITY_PASSWORD_SALT'],
      max_age=expiration
    )
  except Exception:
    return False
  stored_token = kreoh_store.get(token)
  if not stored_token or stored_token == 'true':
    return False
  kreoh_store.set(token, 'true', timedelta(seconds=1800))
  return email