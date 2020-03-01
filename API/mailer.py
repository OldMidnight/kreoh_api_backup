import json
from datetime import timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from API.models import MailingList
from API.s3 import s3, FileStore
from API.mail_service import MailService

bp = Blueprint('mailer', __name__, url_prefix="/mail")

@bp.route('/mailing_list/add', methods=('POST',))
def add():
  email = request.get_json()['email']
  email_to_add = MailingList(email=email)
  if MailingList.query.filter_by(email=email).first() is None:
    mailer = MailService(current_app, ('Fareed From Kreoh', current_app.config['MAIL_USERNAME']), None)
    mailer.send_mailing_list_added_message(email)
    email_to_add.add()
    return jsonify(added=True, msg="Awesome! We'll send you an email to verify that you have been added!"), 201
  else:
    return jsonify(added=False, msg="You've already been added to the Mailing List! Hold your horses, we're working as fast as we can!"), 404