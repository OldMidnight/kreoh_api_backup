from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from .models import User, Message
from .mail_service import MailService
from .token import confirm_token
import re

bp = Blueprint('user', __name__, url_prefix='/u')
# mailer = MailService(current_app)

@bp.route('/email_change', methods=('POST',))
@jwt_required
def email_change():
  user_id = get_jwt_identity()
  new_email = request.get_json()['new_email']
  other_user = User.query.filter_by(email=new_email).first()
  if other_user is None:
    mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
    # mailer.user_id = user_id
    # mailer.sender = ('Kreoh Support', 'noreply' + current_app.config['MAIL_USERNAME'])
    mailer.send_email_change_message(new_email)
    return jsonify(message='Confirmation link sent to current email.'), 201
  else:
    return jsonify(message='Email is already in use.'), 200

@bp.route('/email_verify', methods=('POST',))
@jwt_required
def email_verification():
  user_id = get_jwt_identity()
  mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
  mailer.send_email_verify_message()
  return jsonify(message='Confirmation link sent to current email.'), 201

@bp.route('/confirm_email/<token>', methods=('POST',))
@jwt_required
def confirm_email(token):
  user_id = get_jwt_identity()
  email = confirm_token(token)
  if not email:
    return jsonify(message='Link has expired.'), 403
  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
      return jsonify(message='Please check your email!'), 406
  user = User.query.filter_by(id=user_id).first()
  user.update_email(email)
  return jsonify(message='Email Changed.'), 202


@bp.route('/password_change', methods=('POST',))
@jwt_required
def password_change():
  user_id = get_jwt_identity()
  new_password = request.get_json()['new_password']
  mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
  # mailer.sender = ('Kreoh Support', 'noreply' + current_app.config['MAIL_USERNAME'])
  # mailer.user_id = user_id
  mailer.send_password_change_message(new_password)
  return jsonify(message='Confirmation link sent to current email.'), 201

@bp.route('/confirm_password/<token>', methods=('POST',))
@jwt_required
def confirm_password(token):
  user_id = get_jwt_identity()
  password = confirm_token(token)
  if not password:
    return jsonify(message='Link has expired.'), 403
  if len(password) < 8 or len(password) > 25:
    return jsonify(message='Invalid password.'), 406
  password = generate_password_hash(password)
  user = User.query.filter_by(id=user_id).first()
  user.update_password(password)
  return jsonify(message='Password Changed.'), 202

@bp.route('/delete_account', methods=('POST',))
@jwt_required
def delete_account():
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()
  if user is None:
    return jsonify(message='No such user'), 404
  user.delete()
  user = User.query.filter_by(id=user_id).first()
  if user is None:
    return jsonify(message='Account Deleted.'), 200

@bp.route('/status', methods=('GET',))
@jwt_required
def get_status():
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()
  raw_messages = Message.query.filter_by(user_id=user_id).all()
  messages = []
  for message in raw_messages:
    messages.append({
      'sender': message.sender_name,
      'address': message.sender_address,
      'subject': message.subject,
      'body': message.body,
      'read': message.read
    })

  return jsonify(email_confirmed=user.email_confirmed, messages=messages), 200