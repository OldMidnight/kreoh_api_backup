import os
from io import BytesIO
from .s3 import s3, FileStore
from .screenshot import ScreenshotClient
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
bucket = s3.Bucket('bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0')
store = FileStore(bucket)


def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/screenshot/grab', methods=('GET',))
@jwt_required
def grab_screenshot():
  screenshot_client = ScreenshotClient()
  user_id = get_jwt_identity()
  website = Website.query.filter_by(user_id=user_id).first()
  if website is None:
    return jsonify(screenshot_saved=False, message='No such Website.'), 404
  pages = {
    'home': '/',
    'projects': '/projects',
    'resume': '/resume'
  }
  disable_after = False
  if not website.active:
    website.screenshot_activation()
    disable_after = True
  for page in pages:
    screenshot = screenshot_client.get_screenshot('http://' + website.domain + '.localhost:3001' + pages[page])
    store.upload(screenshot, website.domain + '/' + page + '.kreoh.com.png')
  screenshot_client.driver.quit()
  if disable_after:
    website.screenshot_deactivation()
  return jsonify(screenshot_saved=True), 200

@bp.route('/screenshot/<path:filename>', methods=('GET',))
def display_screenshot(filename):
  try:
    screenshot = store.download(filename)
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

# @bp.route('/favicon', methods=('POST',))
# @jwt_required
# def save_favicon():
#   user_id = get_jwt_identity()
#   domain = User.query.filter_by(id=user_id).first().domain
#   if 'favicon' not in request.files:
#     return jsonify(msg="No File Sent."), 200
#   favicon = request.files['favicon']
#   if favicon.filename == '':
#     return jsonify(msg='No Selected File.'), 200
#   if favicon and allowed_file(favicon.filename):
#     favicon_name = secure_filename(str(user_id) + '_' + domain + '_' + favicon.filename)
#     store.upload(favicon, favicon_name)
#     return jsonify(msg='File Uploaded'), 201

# @bp.route('/favicon/<filename>', methods=('GET',))
# def get_favicon(filename):
#   try:
#     favicon = store.download(filename)
#   except botocore.exceptions.ClientError as e:
#     if e.response['Error']['Code'] == "404":
#       return jsonify(screenshot_saved=False, message='No such Icon.'), 404
#     else:
#       return jsonify(screenshot_saved=False, message='An Error has occured.'), 404
#   favicon.seek(0)
#   return send_file(
#     favicon,
#     mimetype='image/*',
#     as_attachment=True,
#     attachment_filename='%s' % filename
#   )

# @bp.route('/favicon/delete', methods=('POST',))
# @jwt_required
# def delete_favicon():
#   favicon = request.get_json()['filename']
#   try:
#     store.delete_file(favicon)
#   except Exception as e:
#     raise Exception(e)
#   return jsonify(), 200

# USER IMAGE UPLOADS

@bp.route('/images/<domain>/<filename>', methods=('POST',))
@jwt_required
def upload_image(domain, filename):
  if 'image' not in request.files:
    return jsonify(msg="No File Sent."), 200
  image = request.files['image']
  if image.filename == '':
    return jsonify(msg='No Selected File.'), 200
  if image:
    store.upload(image, domain + '/' + filename)
    return jsonify(msg='Image Uploaded'), 201
  return jsonify(error="image Not Uploaded"), 403

@bp.route('/images/<domain>/<filename>', methods=('GET',))
def get_image(domain, filename):
  try:
    image = store.download(domain + '/' + filename)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return jsonify(screenshot_saved=False, message='No such Icon.'), 404
    else:
      return jsonify(screenshot_saved=False, message='An Error has occured.'), 404
  image.seek(0)
  return send_file(
    image,
    mimetype='image/*',
    as_attachment=True,
    attachment_filename='%s' % domain + '/' + filename
  )

@bp.route('/images/<domain>/<filename>/delete', methods=('POST',))
@jwt_required
def delete_image(domain, filename):
  try:
    store.delete_file(domain + '/' + filename)
  except Exception as e:
    return jsonify(error='No such file'), 200
  return jsonify(), 200