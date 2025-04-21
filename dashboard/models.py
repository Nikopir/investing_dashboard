from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from dashboard import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Share(db.Model):
    __tablename__ = 'shares'
    id = db.Column(db.Integer, primary_key=True)
    figi = db.Column(db.String(255), unique=True, nullable=False)
    isin = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    ticker = db.Column(db.String(10), unique=False, nullable=False)
    currency = db.Column(db.String(20), nullable=False)
    uid = db.Column(db.String(255), unique=True, nullable=False)
    last_price = db.Column(db.Float, nullable=True)
    is_trend_high = db.Column(db.Boolean, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)
