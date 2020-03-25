from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import WebsiteStats, KreohUser
from datetime import datetime, timedelta

bp = Blueprint('stats', __name__, url_prefix='/stats')

@bp.route('/record_cta_inter', methods=('POST',))
def record_interaction():
  data = request.get_json()
  domain = data['domain']
  date_time = data['date_time']
  stats = WebsiteStats(domain=domain, cta_inter=True, visit_date_time=date_time)
  stats.add()
  return jsonify(), 200

@bp.route('/add_record', methods=('POST',))
def add_record():
  data = request.get_json()
  domain = data['domain']
  date_time = data['date_time']
  stats = WebsiteStats(domain=domain, visit_date_time=date_time)
  stats.add()
  return jsonify(), 200


@bp.route('/fetch_stats', methods=('GET',))
@jwt_required
def fetch_stats():
  ''' Fetch Call To Action Interaction stats '''
  current_time = datetime.utcnow()
  day = current_time.weekday()
  labels = []
  values = []
  value_labels = []

  user_id = get_jwt_identity()
  user_domain = KreohUser.query.filter_by(id=user_id).first().domain
  stats = WebsiteStats.query.filter(WebsiteStats.domain == user_domain, WebsiteStats.visit_date_time > (current_time - timedelta(days=6)), WebsiteStats.cta_inter).all()
  data = {
    '0': [],
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': [],
    '6': [],
  }

  data_labels = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

  # append visits for specific days in data
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

  temp_day = day
  if not data[str(temp_day)]:
    temp_day -= 1
    while temp_day > -1 and not data[str(temp_day)] and temp_day != day:
      if temp_day == 0:
        temp_day = 6
      else:
        temp_day -= 1
  if temp_day == -1 or not data[str(temp_day)]:
    last_visitor_time = 'Kinda quiet round here...'
  else:
    last_visitor_time = data[str(temp_day)][-1]

    time_difference = str(current_time - last_visitor_time)
    time_difference = time_difference.split(':')
    time_difference[0] = time_difference[0] + ' hours,'
    time_difference[1] = time_difference[1] + ' minutes and'
    time_difference[2] = str(int(float(time_difference[2]))) + ' seconds ago'
    last_visitor_time = ' '.join(time_difference)

  i = day
  labels.append(i)

  i = day
  while i > 0:
    i -= 1
    labels.append(i)

  i = 6
  while i > day:
    labels.append(i)
    i -= 1

  labels.reverse()
  
  for day in labels:
    values.append(len(data[str(day)]))

  for label in labels:
    value_labels.append(data_labels[label])

  total = 0
  for value in values:
    total = total + value

  # avg = avg // 7

  highest_val = '0'
  for val in data:
    if len(data[val]) >= len(data[highest_val]):
      highest_val = val
  if not data[highest_val]:
    highest = 'Kinda quiet round here...'
  else:
    highest = str(len(data[highest_val])) + ' interactions - ' + data[highest_val][-1].strftime('%A')

  cta_stats = { 'values': values, 'labels': value_labels, 'last_visitor_time': last_visitor_time, 'total': total, highest: highest }

  ''' Fetch weekly stats '''
  labels = []
  values = []
  value_labels = []
  stats = WebsiteStats.query.filter(WebsiteStats.domain == user_domain, WebsiteStats.visit_date_time > (current_time - timedelta(days=6))).all()
  data = {
    '0': [],
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': [],
    '6': [],
  }

  data_labels = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

  # append visits for specific days in data
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

  temp_day = day
  if not data[str(temp_day)]:
    temp_day -= 1
    while temp_day > -1 and not data[str(temp_day)] and temp_day != day:
      if temp_day == 0:
        temp_day = 6
      else:
        temp_day -= 1
  if temp_day == -1 or not data[str(temp_day)]:
    last_visitor_time = 'Kinda quiet round here...'
  else:
    last_visitor_time = data[str(temp_day)][-1]

    time_difference = str(current_time - last_visitor_time)
    time_difference = time_difference.split(':')
    time_difference[0] = time_difference[0] + ' hours,'
    time_difference[1] = time_difference[1] + ' minutes and'
    time_difference[2] = str(int(float(time_difference[2]))) + ' seconds ago'
    last_visitor_time = ' '.join(time_difference)

  i = day
  labels.append(i)

  i = day
  while i > 0:
    i -= 1
    labels.append(i)

  i = 6
  while i > day:
    labels.append(i)
    i -= 1

  labels.reverse()
  
  for day in labels:
    values.append(len(data[str(day)]))

  for label in labels:
    value_labels.append(data_labels[label])

  total = 0
  for value in values:
    total = total + value

  # avg = avg // 7

  highest_val = '0'
  for val in data:
    if len(data[val]) >= len(data[highest_val]):
      highest_val = val
  if not data[highest_val]:
    highest = 'Kinda quiet round here...'
  else:
    highest = str(len(data[highest_val])) + ' visitors - ' + data[highest_val][-1].strftime('%A')

  weekly_stats = { 'values': values, 'labels': value_labels, 'last_visitor_time': last_visitor_time, 'total': total, 'highest': highest }

  ''' HOURLY STATS '''
  labels = []
  value_labels = []
  values = []
  stats = WebsiteStats.query.filter(WebsiteStats.domain == user_domain, WebsiteStats.visit_date_time > (current_time - timedelta(hours=23))).all()

  data = {
    '0': [],
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': [],
    '6': [],
    '7': [],
    '8': [],
    '9': [],
    '10': [],
    '11': [],
    '12': [],
    '13': [],
    '14': [],
    '15': [],
    '16': [],
    '17': [],
    '18': [],
    '19': [],
    '20': [],
    '21': [],
    '22': [],
    '23': []
  }

  data_labels = {
    '0': '12 AM',
    '3': '3 AM',
    '6': '6 AM',
    '9': '9 AM',
    '12': '12 PM',
    '15': '3 PM',
    '18': '6 PM',
    '21': '9 PM'
  }

  for stat in stats:
    hour = stat.visit_date_time.hour
    data[str(hour)].append(stat.visit_date_time)


  i = current_time.hour
  labels.append(i)


  first_label = labels[0]
  i = first_label
  while i != 0:
    i -= 1
    labels.append(i)

  i = 23
  while i != first_label:
    labels.append(i)
    i -= 1

  labels.reverse()

  for hour in labels:
    values.append(len(data[str(hour)]))

  for label in labels:
    if label % 3 == 0:
      value_labels.append(data_labels[str(label)])
    else:
      value_labels.append(' ')

  total = 0
  for value in values:
    total = total + value

  # avg = avg // 8

  highest_val = '0'
  for val in data:
    if len(data[val]) >= len(data[highest_val]):
      highest_val = val

  if not data[highest_val]:
    highest = 'Kinda quiet round here...'
  else:
    highest = str(len(data[highest_val])) + ' students - ' + str(data[highest_val][-1].strftime('%I %p'))

  hourly_stats = { 'values': values, 'labels': value_labels, 'total': total, 'highest': highest }

  ''' MONTHLY STATS '''
  labels = []
  value_labels = []
  values = []
  stats = WebsiteStats.query.filter(WebsiteStats.domain == user_domain, WebsiteStats.visit_date_time > (current_time - timedelta(days=364))).all()
  data = {
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': [],
    '6': [],
    '7': [],
    '8': [],
    '9': [],
    '10': [],
    '11': [],
    '12': []
  }

  data_labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

  for stat in stats:
    month = stat.visit_date_time.month
    data[str(month)].append(stat.visit_date_time)


  i = current_time.month
  labels.append(i)

  while i != 1:
    i -= 1
    labels.append(i)
  
  i = 12
  while i != current_time.month:
    labels.append(i)
    i -= 1
  labels.reverse()
  
  for month in labels:
    values.append(len(data[str(month)]))

  for label in labels:
    value_labels.append(data_labels[label - 1])

  total = 0
  for value in values:
    total = total + value

  # avg = avg // 12

  highest_val = '1'
  for val in data:
    if len(data[val]) >= len(data[highest_val]):
      highest_val = val

  if not data[highest_val]:
    highest = 'Kinda quiet round here...'
  else:
    highest = str(len(data[highest_val])) + ' visitors - ' + str(data[highest_val][-1].strftime('%B'))

  monthly_stats = { 'values': values, 'labels': value_labels, 'total': total, 'highest': highest }
  return jsonify(cta_stats=cta_stats, weekly_stats=weekly_stats, hourly_stats=hourly_stats, monthly_stats=monthly_stats), 200