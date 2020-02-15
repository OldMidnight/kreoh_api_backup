import json
from datetime import timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from .models import MailingList
from .s3 import s3, FileStore

bp = Blueprint('mailer', __name__, url_prefix="/mail")

@bp.route('/mailing_list/add', methods=('POST',))
def add():
  email = request.get_json()['email']
  email_to_add = MailingList(email=email)
  if MailingList.query.filter_by(email=email).first() is None:
    email_to_add.add()
    return jsonify(added=True), 201
  else:
    return jsonify(added=False), 402