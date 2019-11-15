from pathlib import Path

from flask import Blueprint, request, jsonify, Response, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from API.models import Website, User
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QUrl, QTimer
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

bp = Blueprint('uploads', __name__, url_prefix="/uploads")

class Screenshot(QWebEngineView):
  def capture(self, url, output_file):
    self.output_file = output_file
    self.load(QUrl(url))
    self.loadFinished.connect(self.on_loaded)
    # Create hidden view without scrollbars
    self.setAttribute(Qt.WA_DontShowOnScreen)
    self.page().settings().setAttribute(
        QWebEngineSettings.ShowScrollBars, False)
    self.show()

  def on_loaded(self):
    self.resize(1920, 1080)
    # Wait for resize
    QTimer.singleShot(1000, self.take_screenshot)

  def take_screenshot(self):
    self.grab().save(self.output_file, 'PNG')
    self.app.quit()


@bp.route('/screenshot/grab', methods=('GET',))
@jwt_required
def grab_screenshot():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  app = QApplication.instance()
  if app is None:
    app = QApplication()
  s = Screenshot()
  s.app = app
  s.capture('http://' + user.domain + '.localhost:3000/', current_app.config['UPLOAD_FOLDER'] + user.domain + '.kreoh.com.png')
  app.exec_()
  app.exit()
  return jsonify(sreenshot_saved=True), 200

@bp.route('/screenshot/<path:filename>', methods=('GET',))
def display_screenshot(filename):
  screenshot = Path(current_app.config['UPLOAD_FOLDER'] + filename)
  if screenshot.is_file():
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
  else:
    return jsonify(error="No Screenshot Found!")