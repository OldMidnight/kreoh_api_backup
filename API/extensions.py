import os
import redis
from flask_jwt_extended import JWTManager
from flask_mail import Mail

jwt = JWTManager()

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
  jti = decrypted_token['jti']
  entry = jwt_revoked_store.get(jti)
  if entry is None:
    return True
  return entry == 'true'

mail = Mail()

MAIN_REDIS_URL = os.environ['REDIS_URL'].split('@')
MAIN_REDIS_URL_HOST = MAIN_REDIS_URL[1].split(':')[0]
MAIN_REDIS_URL_PASSWORD = MAIN_REDIS_URL[0].split(':')[2]
MAIN_REDIS_URL_PORT = MAIN_REDIS_URL[1].split(':')[1]

JWT_REDIS_URL = os.environ['HEROKU_REDIS_TEAL_URL'].split('@')
JWT_REDIS_URL_HOST = JWT_REDIS_URL[1].split(':')[0]
JWT_REDIS_URL_PASSWORD = JWT_REDIS_URL[0].split(':')[2]
JWT_REDIS_URL_PORT = JWT_REDIS_URL[1].split(':')[1]

kreoh_store = redis.Redis(host=MAIN_REDIS_URL_HOST, port=MAIN_REDIS_URL_PORT, password=MAIN_REDIS_URL_PASSWORD, decode_responses=True)
jwt_revoked_store = redis.Redis(host=JWT_REDIS_URL_HOST, port=JWT_REDIS_URL_PORT, password=JWT_REDIS_URL_PASSWORD, decode_responses=True)