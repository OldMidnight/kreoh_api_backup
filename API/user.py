from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from API.models import KreohUser, Message, Upload
from API.mail_service import MailService
from API.token import confirm_token
from API.s3 import FileStore, s3
import re

bp = Blueprint('user', __name__, url_prefix='/u')
bucket = s3.Bucket('bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0')
store = FileStore(bucket)

@bp.route('/email_verify', methods=('POST',))
@jwt_required
def email_verification():
  user_id = get_jwt_identity()
  mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
  try:
    mailer.send_email_verify_message()
  except:
    return jsonify(error=True, message="An error has occurred. Please try again later."), 400
  return jsonify(error=False, message='Confirmation link has been resent!'), 201

@bp.route('/confirm_email/<token>', methods=('POST',))
@jwt_required
def confirm_email(token):
  user_id = get_jwt_identity()
  email = confirm_token(token)
  if not email:
    return jsonify(error=True, message='Link has expired.'), 403
  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
      return jsonify(error=True, message='Inavlid Email.'), 400
  user = KreohUser.query.filter_by(id=user_id).first()
  user.update_email(email)
  return jsonify(error=False, message='Email Verified.'), 201


@bp.route('/password_change', methods=('POST',))
@jwt_required
def password_change():
  user_id = get_jwt_identity()
  current_password = request.get_json()['current_password']
  new_password = request.get_json()['new_password']

  if not re.search(r'\d+', new_password) or \
    len(new_password) < 8 or \
    len(new_password) > 25 or \
    not re.search(r'[A-Z]+', new_password):
    return jsonify(error=True, message='Invalid details.'), 400

  user = KreohUser.query.filter_by(id=user_id).first()
  if not check_password_hash(user.password, current_password):
    return jsonify(error=True, message='Invalid details.'), 400
  mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
  try:
    mailer.send_password_change_message(new_password)
  except Exception:
    return jsonify(error=True, message="There was an error processing your request. Please try again later.")
  return jsonify(error=False, message='Confirmation link sent to your email.'), 201

@bp.route('/confirm_password/<token>', methods=('POST',))
@jwt_required
def confirm_password(token):
  user_id = get_jwt_identity()
  new_password = confirm_token(token)
  if not new_password:
    return jsonify(error=True, message='Password not changed. Link has expired.'), 403
  if not re.search(r'\d+', new_password) or \
    len(new_password) < 8 or \
    len(new_password) > 25 or \
    not re.search(r'[A-Z]+', new_password):
    return jsonify(error=True, message='Paassword not changed. Invalid password.'), 400
  new_password = generate_password_hash(new_password)
  user = KreohUser.query.filter_by(id=user_id).first()
  user.update_password(new_password)
  return jsonify(error=False, message='Password Changed.'), 202

@bp.route('/delete_account', methods=('POST',))
@jwt_required
def delete_account():
  user_id = get_jwt_identity()
  user = KreohUser.query.filter_by(id=user_id).first()
  if user is None:
    return jsonify(error=True, message='No such user'), 404
  uploads = Upload.query.filter_by(user_id=user.id).all()
  for upload in uploads:
    store.deleteFile(upload.url)
    upload.delete()
  pages = {
    'home': '/',
    'projects': '/projects',
    'resume': '/resume'
  }
  for page in pages:
    store.deleteFile(user.domain + '/' + page + '.kreoh.com.png')
  user.delete()
  user = KreohUser.query.filter_by(id=user_id).first()
  if user is None:
    return jsonify(error=False, message='Account Deleted.'), 201
  else:
    return jsonify(error=True, message='An error has occured. Please try again later.'), 400
  

@bp.route('/status', methods=('GET',))
@jwt_required
def get_status():
  user_id = get_jwt_identity()
  user = KreohUser.query.filter_by(id=user_id).first()
  raw_messages = Message.query.filter_by(user_id=user_id).all()
  messages = []
  for message in raw_messages:
    if message.support_ticket_id is None:
      messages.append({
        'id': message.id,
        'sender': message.sender_name,
        'address': message.sender_address,
        'subject': message.subject,
        'body': message.body,
        'read': message.read,
        'time_sent': message.time_sent
      })

  return jsonify(messages=messages), 200

@bp.route('/msg/read', methods=('PUT',))
@jwt_required
def set_read():
  data = request.get_json()
  message_id = data['id']
  message = Message.query.filter_by(id=message_id).first()
  message.set_read()
  return jsonify(), 201
