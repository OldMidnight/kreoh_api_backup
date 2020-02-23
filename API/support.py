from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from API.models import SupportMessage
from API.mail_service import MailService

bp = Blueprint('support', __name__, url_prefix="/support")

@bp.route('/send_message', methods=('POST',))
@jwt_required
def send_support_msg():
  user_id = get_jwt_identity()
  data = request.get_json()
  message = data['message']
  mailer = MailService(current_app, ('Kreoh Support', current_app.config['MAIL_USERNAME']), user_id)
  support_msg = SupportMessage(user_id=user_id, subject=message['subject'], body=message['body'])
  support_msg.add()
  mailer.send_support_message(subject='SUPPORT TICKET: ' + message['subject'], recipients=['admin@kreoh.com'], body=message['body'], ticket_id=support_msg.id)
  mailer.send_support_confirmation_message()
  return jsonify(), 201
