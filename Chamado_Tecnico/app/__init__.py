from flask import Flask

app = Flask(__name__)

app.secret_key = '3fb88c8328ebf7a03188aa92364e569162484f8a7422d1fc'

from app import views