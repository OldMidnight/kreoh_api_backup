#!/usr/bin/env python3
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from API.models import User, Website
import json

bp = Blueprint('site_creation', __name__, url_prefix="/create")

locked_domains = [
  'api',
  'kreoh',
  'sales',
  'blog',
  'support',
  'help',
  'shop',
  'engineering',
  'www',
  'mail',
  'email',
  'remote',
  'ns1',
  'ns2',
  'test',
  'dashboard',
  'creator',
  'editor',
  'dev',
  'web',
  'mx',
  '1',
  '2',
  'www2',
  'store',
  'app',
  'cdn',
  'news',
  'wiki',
  'forums',
  'temp',
  'admin',

]

@bp.route('/validate_domain', methods=('POST',))
def validate_domain():
  domain = request.get_json()['domain']
  user = User.query.filter_by(domain=domain).first()
  if user is None and domain not in locked_domains:
    return jsonify(validated=True), 200
  else:
    return jsonify(validated=False, msg="Invalid or Unavailable domain name."), 409

@bp.route('/register_site', methods=('POST',))
@jwt_required
def register_website():
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()
  data = request.get_json()['site_props']
  site_props = json.loads(data)
  site_props = json.dumps(site_props)
  website = Website(user_id=user_id, domain=user.domain, site_props=site_props)
  try:
    website.add()
  except IntegrityError:
    return jsonify(message='Website already created.'), 409
  # website.site_activation()
  if Website.query.filter_by(user_id=user_id).first() is None:
    return jsonify(message="Webite could not be registered."), 406
  else:
    return jsonify(message="Website Created."), 200

@bp.route('/update_site', methods=('POST',))
@jwt_required
def update_website():
  user_id = get_jwt_identity()
  data = request.get_json()['site_props']
  data = json.loads(data)
  new_site_props = json.dumps(data)
  website = Website.query.filter_by(user_id=user_id).first()
  if website is None:
    return jsonify(message="There is no website to update."), 404
  website.update_site(new_site_props)
  return jsonify(), 200
