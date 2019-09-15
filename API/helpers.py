from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from API.models import Website, User
import json

bp = Blueprint('helpers', __name__, url_prefix="/helper")

@bp.route('/api_test', methods=('GET', 'POST',))
def api_test():
    if request.method == 'GET':
        return jsonify(hello='world')
    else:
        return jsonify(hello='post')

@bp.route('/refresh_token', methods=('POST',))
@jwt_refresh_token_required
def refresh():
    user = get_jwt_identity()
    new_token = create_access_token(identity=user, fresh=False)
    print(new_token)
    return jsonify(access_token=new_token), 201

@bp.route('/site_config/site_activation', methods=('POST',))
@jwt_required
def site_activation():
    user_id = get_jwt_identity()
    website = Website.query.filter_by(user_id=user_id).first()
    website.site_activation()
    print('test')
    print(website.active)
    return jsonify(active=website.active), 200

@bp.route('/get_site_active', methods=('GET',))
@jwt_required
def get_site_active():
    user_id = get_jwt_identity()
    print(user_id)
    user = User.query.filter_by(u_id=user_id).first()
    print(user)
    website = Website.query.filter_by(user_id=user.u_id).first()
    if website is None:
        return jsonify(site_active=False, site_available=False)
    else:
        return jsonify(site_active=website.active, site_available=True)

@bp.route('/check_domain', methods=('POST',))
def check_domain():
    domain = request.get_json()['domain']
    user = User.query.filter_by(domain=domain).first()
    if user:
        website = Website.query.filter_by(user_id=user.u_id).first()
        if website.active:
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
    site_config = json.loads(website.site_props)
    return jsonify(site_config=site_config), 200

@bp.route('/get_site', methods=('POST',))
@jwt_required
def get_site():
    user_id = get_jwt_identity()
    website = Website.query.filter_by(user_id=user_id).first()
    if website:
        return jsonify(available=True), 200
    else:
        return jsonify(available=False), 200
