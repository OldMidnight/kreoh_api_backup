import json
from datetime import timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from .models import Website, User
from .s3 import bucket

bp = Blueprint('helpers', __name__, url_prefix="/helper")

@bp.route('/refresh_token', methods=('POST',))
@jwt_refresh_token_required
def refresh():
  user = get_jwt_identity()
  new_token = create_access_token(identity=user, fresh=False, expires_delta=timedelta(hours=3))
  return jsonify(access_token=new_token), 201

@bp.route('/site_config/site_activation', methods=('POST',))
@jwt_required
def site_activation():
  user_id = get_jwt_identity()
  website = Website.query.filter_by(user_id=user_id).first()
  if website is None:
    return jsonify(message='No website to toggle activation.'), 404
  website.site_activation()
  return jsonify(active=website.active), 200

@bp.route('/get_site_active', methods=('GET',))
@jwt_required
def get_site_active():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  website = Website.query.filter_by(user_id=user.u_id).first()
  if website is None:
    return jsonify(site_parked=False, site_available=False)
  else:
    return jsonify(site_parked=not(website.active), site_available=True)

@bp.route('/check_domain', methods=('POST',))
def check_domain():
  domain = request.get_json()['domain']
  user = User.query.filter_by(domain=domain).first()
  if user:
    website = Website.query.filter_by(user_id=user.u_id).first()
    if website is None:
      return jsonify(available=False, active=False), 200
    elif website.active:
      return jsonify(available=True, active=True), 200
    else:
      return jsonify(available=True, active=False), 200
  else:
    return jsonify(available=False, active=False), 200

@bp.route('/site_config', methods=('POST',))
def get_site_config():
  data = request.get_json()
  domain = data['domain']
  user = User.query.filter_by(domain=domain).first()
  website = Website.query.filter_by(user_id=user.u_id).first()
  if website is None:
    return jsonify(error="No such website")
  else:
    site_config = json.loads(website.site_props)
    return jsonify(site_config=site_config), 200

@bp.route('/auth_site_config', methods=('GET',))
@jwt_required
def get_auth_site_config():
  user_id = get_jwt_identity()
  website = Website.query.filter_by(user_id=user_id).first()
  if website is None:
    return jsonify(site_not_created=True)
  else:
    site_config = json.loads(website.site_props)
    return jsonify(site_config=site_config), 200


@bp.route('/delete_site', methods=('POST',))
@jwt_required
def delete_site():
  domain = request.get_json()['domain']
  website = Website.query.filter_by(domain=domain).first()
  if website is None:
    return jsonify(message="Website could not be deleted. No Such website."), 404
  else:
    website.delete()
    website = Website.query.filter_by(domain=domain).first()
    screenshot = domain + '.kreoh.com.png'
    try:
      bucket.delete_key(screenshot)
    except:
      pass
    return jsonify(message="Website deleted."), 200