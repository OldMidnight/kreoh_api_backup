from flask import Blueprint, request, jsonify, Response, current_app, g, url_for, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message as Msg
from werkzeug.security import generate_password_hash
from .models import User
from .extensions import mail
from .token import generate_confirmation_token, confirm_token

bp = Blueprint('user', __name__, url_prefix='/u')

@bp.route('/email_change', methods=('POST',))
@jwt_required
def email_change():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  new_email = request.get_json()['new_email']
  other_user = User.query.filter_by(email=new_email).first()
  if other_user is None:
    msg = Msg('Email Change Confirmation', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    token = generate_confirmation_token(new_email)
    confirm_url = 'http://localhost:3000/u/confirm_email/' + token
    msg.body = 'Hi {f_name},\n\nWe have recieved your email change request to:\n {new_email}\n\nFollow the link below to confirm:\n{confirm_url}\n\nThis link will expire in 1 hour. If you did not request this email change or you are not registered with our service, please ignore this email.\n\nKind Regards,\nKreoh Representative\nhttps://Kreoh.com'.format(f_name=user.f_name, new_email=new_email, confirm_url=confirm_url)
    mail.send(msg)
    return jsonify(message='Confirmation link sent to current email.'), 201
  else:
    return jsonify(message='Email is already in use.'), 200

@bp.route('/confirm_email/<token>', methods=('POST',))
@jwt_required
def confirm_email(token):
  user_id = get_jwt_identity()
  email = confirm_token(token)
  if not email:
    return jsonify(message='Link has expired.'), 403
  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
      return jsonify(message='Please check your email!'), 406
  user = User.query.filter_by(u_id=user_id).first()
  user.update_email(email)
  return jsonify(message='Email Changed.'), 202


@bp.route('/password_change', methods=('POST',))
@jwt_required
def password_change():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  new_password = request.get_json()['new_password']
  msg = Msg('Password Change Request', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
  token = generate_confirmation_token(new_password)
  confirm_url = 'http://localhost:3000/u/confirm_password/' + token
  msg.body = 'Hi {f_name},\n\nWe have recieved your password change request.\n\nFollow the link below to confirm:\n{confirm_url}\n\nThis link will expire in 1 hour. If you did not request this password change please secure account at https://Kreoh.com/secure_my_account .\n\nKind Regards,\nKreoh Representative\nhttps://Kreoh.com'.format(f_name=user.f_name, confirm_url=confirm_url)
  mail.send(msg)
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
  user = User.query.filter_by(u_id=user_id).first()
  user.update_password(password)
  return jsonify(message='Password Changed.'), 202

@bp.route('/delete_account', methods=('POST',))
@jwt_required
def delete_account():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  if user is None:
    return jsonify(message='No such user'), 404
  user.delete()
  user = User.query.filter_by(u_id=user_id).first()
  if user is None:
    return jsonify(message='Account Deleted.'), 200