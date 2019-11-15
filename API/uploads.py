from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep

from flask import Blueprint, request, jsonify, Response, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_refresh_token_required, create_access_token
from API.models import Website, User
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt, QUrl, QTimer
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import threading

bp = Blueprint('uploads', __name__, url_prefix="/uploads")
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

# class Screenshot(QWebEngineView):
#   def capture(self, url, output_file):
#     print(self.app.thread())
#     self.output_file = output_file
#     self.load(QUrl(url))
#     self.resize(1920, 1080)
#     self.loadFinished.connect(self.on_loaded)
#     # Create hidden view without scrollbars
#     self.setAttribute(Qt.WA_DontShowOnScreen)
#     self.page().settings().setAttribute(
#         QWebEngineSettings.ShowScrollBars, False)
#     self.show()

#   def on_loaded(self):
#     self.resize(1920, 1080)
#     # Wait for resize
#     QTimer.singleShot(1000, self.take_screenshot)


#   def take_screenshot(self):
#     self.grab().save(self.output_file, 'PNG')
#     self.app.quit()


@bp.route('/screenshot/grab', methods=('GET',))
@jwt_required
def grab_screenshot():
  user_id = get_jwt_identity()
  user = User.query.filter_by(u_id=user_id).first()
  # Qapp = QApplication.instance()
  # # del Qapp
  # if Qapp is None:
  #   Qapp = QApplication([])
  # s = Screenshot()
  # s.app = Qapp
  # s.capture('http://' + user.domain + '.localhost:3000/', current_app.config['UPLOAD_FOLDER'] + user.domain + '.kreoh.com.png')
  # Qapp.exec_()
  # Qapp.quit()
  driver.get('http://' + user.domain + '.localhost:3000/')
  sleep(1)
  driver.get_screenshot_as_file(current_app.config['UPLOAD_FOLDER'] + user.domain + '.kreoh.com.png')
  driver.quit()
  return jsonify(sreenshot_saved=True), 200

@bp.route('/screenshot/<path:filename>', methods=('GET',))
def display_screenshot(filename):
  screenshot = Path(current_app.config['UPLOAD_FOLDER'] + filename)
  if screenshot.is_file():
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
  else:
    return jsonify(error="No Screenshot Found!")