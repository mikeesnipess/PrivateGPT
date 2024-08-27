from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
# app.config['UPLOAD_FOLDER'] = 'static/files'

from app.controllers.upload_controller import upload
