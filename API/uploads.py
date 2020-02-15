import botocore
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from API.models import Website
from .s3 import s3, FileStore
from .screenshot import ScreenshotClient

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
        # as_attachment=True,
        attachment_filename='%s' % domain + '/' + filename
    )

@bp.route('/images/<domain>/<filename>', methods=('DELETE',))
@jwt_required
def delete_image(domain, filename):
    try:
        store.delete_file(domain + '/' + filename)
    except Exception as e:
        return jsonify(error='No such file'), 200
    return jsonify(), 200