import sys
import botocore
import math
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from API.models import Website, Upload, User
from .s3 import s3, FileStore
from .screenshot import ScreenshotClient

bp = Blueprint('uploads', __name__, url_prefix="/uploads")
bucket = s3.Bucket('bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0')
store = FileStore(bucket)

storage_dict = {
    0: 100000000,
    1: 100000000,
    2: 300000000,
    3: 500000000,
    4: 100000000
}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

@bp.route('/', methods=('GET',))
@jwt_required
def getUploads():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    uploads = user.uploads
    upload_resp = []
    for upload in uploads:
        # print(upload.url, upload.size)
        upload_resp.append({
            'url': upload.url,
            'size': convert_size(upload.size),
            'type': upload.type,
            'name': upload.name,
            'upload_date': upload.upload_date
        })
    storage = {
        'max_storage_space': storage_dict[user.account_type],
        'current_storage_space': user.storage_space
    }
    return jsonify(error=False, uploads=upload_resp, storage=storage), 200

@bp.route('/screenshot/grab', methods=('GET',))
@jwt_required
def grab_screenshot():
    if not current_app.config['DEBUG']:
        screenshot_client = ScreenshotClient()
        user_id = get_jwt_identity()
        website = Website.query.filter_by(user_id=user_id).first()
        if website is None:
            return jsonify(error=True, message='No such Website.'), 404
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
            screenshot = screenshot_client.get_screenshot('http://' + website.domain + '.kreoh.com' + pages[page])
            store.upload(screenshot, website.domain + '/' + page + '.kreoh.com.png')
        screenshot_client.driver.quit()
        if disable_after:
            website.screenshot_deactivation()
    return jsonify(error=False, message='Website screenshots captured!'), 201

# USER FILE UPLOADS

@bp.route('/user-content/<domain>/<filename>', methods=('POST',))
@jwt_required
def upload_file(domain, filename):
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if 'upload' not in request.files:
        return jsonify(error=True, message="No File Sent."), 400
    upload_filename = filename.split('.')
    user_file = request.files['upload']
    user_file.seek(0, 2)
    size = user_file.tell()
    user_file.seek(0)
    if user_file.filename == '':
        return jsonify(error=True, message='No Selected File.'), 400
    if user_file:
        store.upload(user_file, domain + '/' + filename)
        upload = Upload.query.filter_by(label=domain + '/' + upload_filename[0]).first()
        if upload is None:
            upload = Upload(url=domain + '/' + filename, type=user_file.content_type, size=size, name=user_file.filename, ext=upload_filename[1], label=domain + '/' + upload_filename[0], user_id=user.id)
            upload.add()
            user.updateStorageSpace('-', size)
        else:
            store.deleteFile(upload.url)
            if upload.size > size:
                user.updateStorageSpace('+', upload.size - size)
            elif upload.size < size:
                user.updateStorageSpace('-', size - upload.size)
            upload.update(new_values={
                'url': domain + '/' + filename,
                'ext': upload_filename[1],
                'size': size,
                'type': user_file.content_type,
                'name': user_file.filename
            })
        return jsonify(error=False, message='File Uploaded!'), 201
    return jsonify(error=True, messgae="File Not Uploaded"), 400

@bp.route('/user-content/<domain>/<filename>', methods=('GET',))
def get_file(domain, filename):
  try:
    user_upload = store.download(domain + '/' + filename)
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
      return jsonify(error=True, message='No such File.'), 404
    else:
      return jsonify(error=True, message='An Error has occured.'), 404
  user_upload.seek(0)
  return send_file(
    user_upload,
    attachment_filename='%s' % domain + '/' + filename
  )

@bp.route('/user-content/<domain>/<filename>', methods=('DELETE',))
@jwt_required
def delete_file(domain, filename):
  user_id = get_jwt_identity()
  user = User.query.filter_by(id=user_id).first()
  upload = Upload.query.filter_by(url=domain + '/' + filename).first()
  if upload is None:
    return jsonify(error=True, message='No such file'), 404
  else:
    try:
      store.deleteFile(upload.url)
      upload.delete()
      user.updateStorageSpace('+', upload.size)
    except Exception as e:
      return jsonify(error=True, message='File not found.'), 404
    return jsonify(error=False, message='File Deleted!'), 200