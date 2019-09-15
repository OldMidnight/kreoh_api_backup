#!/usr/bin/env python3
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from API.models import User, Website
import json

bp = Blueprint('site_creation', __name__, url_prefix="/create")

nav_dict = {
    0: 'bottom_nav',
    1: 'side_nav'
}

@bp.route('/validate_domain', methods=('POST',))
def validate_domain():
    user = User.query.filter_by(domain=request.get_json()['domain']).first()
    if user is None:
        return jsonify(validated=True), 200
    else:
        return jsonify(validated=False), 200

@bp.route('/register_site', methods=('POST',))
@jwt_required
def register_website():
    user_id = get_jwt_identity()
    user = User.query.filter_by(u_id=user_id).first()
    data = request.get_json()
    print(data)
    site_props = json.dumps(data)
    print(site_props)
    website = Website(user_id=user_id, domain=user.domain, site_props=site_props)
    website.add()
    website.site_activation()
    return jsonify(), 200
