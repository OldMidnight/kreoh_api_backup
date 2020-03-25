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
  if MailingList.query.filter_by(email=email).first() is None:
    email_to_add = MailingList(email=email)
    mailer = MailService(current_app, ('Fareed From Kreoh', current_app.config['MAIL_USERNAME']), None)
    try:
      mailer.send_mailing_list_added_message(email)
    except Exception as e:
      return jsonify(error=True, message="An error occured while adding your email. Please try again later!"), 400
    email_to_add.add()
    return jsonify(error=False, message="Awesome! We'll send you an email to verify that you have been added!"), 201
  else:
    return jsonify(error=True, message="You've already been added to the Mailing List! Hold your horses, we're working as fast as we can!"), 400