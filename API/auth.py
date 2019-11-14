#!/usr/bin/env python3
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity,
    jwt_refresh_token_required, create_refresh_token
)
from werkzeug.security import check_password_hash, generate_password_hash
from API.models import User, Website

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/register', methods=('POST',))
def register():
    data = request.get_json()
    f_name = data['f_name']
    s_name = data['s_name']
    email = data['email']
    password = data['password']
    domain = data['domain']
    user = User.query.filter_by(domain=domain).first()
    if user is None:
        user = User(domain=domain, email=email, f_name=f_name, s_name=s_name, password=generate_password_hash(password))
        user.add()
        user = User.query.filter_by(domain=domain).first()
        access_token = create_access_token(user.u_id, fresh=True)
        refresh_token = create_refresh_token(user.u_id)
        # user_data = {
        #     'id': user.u_id,
        #     'domain': user.domain,fd
        #     'f_name': f_name,
        #     's_name': s_name
        # }
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify(error="unable to create user"), 401

@bp.route('/login', methods=('POST',))
def login():
    data = request.get_json()
    print(data)
    email = data['email']
    password = data['password']
    user = User.authenticate(email, password)
    if user:
        access_token = create_access_token(user.u_id, fresh=True)
        refresh_token = create_refresh_token(user.u_id)
        return jsonify(id=user.u_id, domain=user.domain, f_name=user.f_name, s_name=user.s_name, access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify(error="unable to login"), 401

@bp.route('/user', methods=('GET',))
@jwt_required
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(u_id=user_id).first()
    website = Website.query.filter_by(user_id=user.u_id).first()
    if website is None:
      return jsonify(id=user.u_id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=False), 200
    else:
      return jsonify(id=user.u_id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=True), 200