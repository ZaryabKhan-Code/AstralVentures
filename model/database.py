from flask_sqlalchemy import SQLAlchemy
import secrets
from datetime import datetime
from flask_login import *
from smtplib import SMTPException
from werkzeug.security import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from itsdangerous import *
import ssl, smtplib
import uuid, requests
from flask import *
from datetime import datetime
from io import BytesIO
from werkzeug.utils import secure_filename
import os, uuid
from flask_migrate import Migrate
from flask_cors import CORS
from flask_session import Session
import openai
import secrets
import string
from functools import wraps
from datetime import timedelta
from datetime import datetime, timedelta
import re, pdfkit

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    role = db.Column(db.String(20), default="user")
    password = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    organization = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    points = db.Column(db.Integer, default=0, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Token(db.Model):
    __tablename__ = "token"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    token = db.Column(db.String(100))


class ChatbotMemory(db.Model):
    __tablename__ = "chatbot_memory"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(255))
    workflow = db.Column(db.String(255))
    speaker = db.Column(db.String(255))
    content = db.Column(db.Text)
