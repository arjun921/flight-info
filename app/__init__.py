from flask import Flask

app = Flask(__name__, static_url_path='/static', instance_relative_config=True)

from app import views

app.config.from_object('config')
