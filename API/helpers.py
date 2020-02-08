import json
from datetime import timedelta
from pathlib import Path
from flask import Blueprint, request, jsonify, Response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from .models import Website, User, WebsiteStats
from .s3 import s3, FileStore

bp = Blueprint('helpers', __name__, url_prefix="/helper")
bucket = s3.Bucket('bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0')
store = FileStore(bucket)

@bp.route('/refresh_token', methods=('POST',))
@jwt_refresh_token_required
def refresh():
  user = get_jwt_identity()
  new_token = create_access_token(identity=user, fresh=False, expires_delta=timedelta(minutes=30))
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
  user = User.query.filter_by(id=user_id).first()
  website = Website.query.filter_by(user_id=user.id).first()
  if website is None:
    return jsonify(site_parked=False, site_available=False)
  else:
    return jsonify(site_parked=not(website.active), site_available=True)

@bp.route('/check_domain', methods=('POST',))
def check_domain():
  domain = request.get_json()['domain']
  user = User.query.filter_by(domain=domain).first()
  if user:
    website = Website.query.filter_by(user_id=user.id).first()
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
  website = Website.query.filter_by(user_id=user.id).first()
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
    # screenshot = domain + '.kreoh.com.png'
    # for page in ['home', 'projects', 'resume']:
    #   try:
    #     store.delete_file(domain + '/' + page + '.' + screenshot)
    #   except Exception:
    #     raise Exception('Could not delete screenshot', domain + '/' + page + '.' + screenshot)
    # objects = [e['Key'] for p in s3.get_paginator("list_objects_v2").paginate(Bucket='bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0', Prefix=domain) for e in p['Contents']]
    # print(objects)
    bucket.objects.filter(Prefix=domain).delete()
    return jsonify(message="Website deleted."), 200