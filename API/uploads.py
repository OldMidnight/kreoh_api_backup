import os
from io import BytesIO
from .s3 import bucket
import botocore
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

from flask import Blueprint, request, jsonify, Response, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from API.models import Website, User

bp = Blueprint('uploads', __name__, url_prefix="/uploads")


def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/screenshot/grab', methods=('GET',))
@jwt_required
def grab_screenshot():
  user_id = get_jwt_identity()
  website = Website.query.filter_by(user_id=user_id).first()
  if website is None:
    return jsonify(screenshot_saved=False, message='No such Website.'), 404
  elif not website.active:
    return jsonify(screenshot_saved=False, message='Website Disabled.'), 200
  if current_app.config['DEBUG']:
    chromedriver_path = '/home/fareed/Documents/Gecko/chromedriver'
  else:
    chromedriver_path = "/app/.chromedriver/bin/chromedriver"
  options = webdriver.ChromeOptions()
  if not current_app.config['DEBUG']:
    chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
    options.binary_location = chrome_bin
  options.add_argument("--disable-gpu")
  options.add_argument("--no-sandbox")
  options.add_argument('headless')
  options.add_argument('window-size=1920x1080')
  driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options)
  pages = {
    'home': '/',
    'projects': '/projects',
    'resume': '/resume'
  }
  for page in pages:
    driver.get('http://' + website.domain + '.localhost:3001' + pages[page])
    sleep(1)
    screenshot = driver.get_screenshot_as_png()
    screenshot = BytesIO(screenshot)
    bucket.upload_fileobj(screenshot, page + '.' + website.domain + '.kreoh.com.png')
  driver.quit()
  return jsonify(screenshot_saved=True), 200

@bp.route('/screenshot/<path:filename>', methods=('GET',))
def display_screenshot(filename):
  try:
    screenshot = BytesIO()
    bucket.download_fileobj(filename, screenshot)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return jsonify(screenshot_saved=False, message='No such Image.'), 404
    else:
      return jsonify(screenshot_saved=False, message='An Error has occured.'), 404
  screenshot.seek(0)
  return send_file(
    screenshot,
    mimetype='image/png',
    as_attachment=True,
    attachment_filename='%s' % filename
  )

@bp.route('/favicon/set', methods=('POST', ))
@jwt_required
def save_favicon():
  user_id = get_jwt_identity()
  domain = User.query.filter_by(u_id=user_id).first().domain
  if 'favicon' not in request.files:
    return jsonify(msg="No File Sent."), 200
  favicon = request.files['favicon']
  if favicon.filename == '':
    return jsonify(msg='No Selected File.'), 200
  if favicon and allowed_file(favicon.filename):
    favicon_name = secure_filename(str(user_id) + '_' + domain + '_' + favicon.filename)
    bucket.upload_fileobj(favicon, favicon_name)
    return jsonify(msg='File Uploaded'), 201

@bp.route('/favicon/<filename>', methods=('GET',))
def get_favicon(filename):
  try:
    favicon = BytesIO()
    bucket.download_fileobj(filename, favicon)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return jsonify(screenshot_saved=False, message='No such Icon.'), 404
    else:
      return jsonify(screenshot_saved=False, message='An Error has occured.'), 404
  favicon.seek(0)
  return send_file(
    favicon,
    mimetype='image/*',
    as_attachment=True,
    attachment_filename='%s' % filename
  )

@bp.route('/favicon/delete', methods=('POST',))
@jwt_required
def delete_favicon():
  favicon = request.get_json()['filename']
  try:
    bucket.delete_key(favicon)
  except:
    pass
  return jsonify(), 200