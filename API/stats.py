from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import WebsiteStats, User
from datetime import datetime, timedelta

bp = Blueprint('stats', __name__, url_prefix='/stats')

@bp.route('/add_record', methods=('POST',))
def add_record():
  data = request.get_json()
  domain = data['domain']
  date_time = data['date_time']
  print(data)
  stats = WebsiteStats(domain=domain, visit_date_time=date_time)
  stats.add()
  return jsonify(error=False), 200


@bp.route('/fetch_weekly', methods=('GET',))
@jwt_required
def fetch_weekly():
  current_time = datetime.utcnow()
  user_id = get_jwt_identity()
  user_domain = User.query.filter_by(u_id=user_id).first().domain
  stats = WebsiteStats.query.filter(WebsiteStats.domain == user_domain, WebsiteStats.visit_date_time > (current_time - timedelta(days=7))).all()
  data = {
    '0': [],
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': [],
    '6': [],
  }
  for stat in stats:
    if stat.visit_date_time.weekday() == 0:
      data['0'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 1:
      data['1'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 2:
      data['2'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 3:
      data['3'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 4:
      data['4'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 5:
      data['5'].append(stat.visit_date_time)
    elif stat.visit_date_time.weekday() == 6:
      data['6'].append(stat.visit_date_time)
  return jsonify(data), 200