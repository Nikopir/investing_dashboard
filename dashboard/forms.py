from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from .models import User, Share


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'placeholder': 'Пароль'})
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'placeholder': 'Пароль'})
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')],
                              render_kw={'placeholder': 'Повторите пароль'})
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(
                'Данный e-mail уже зарегистрирован! Введите другой e-mail или воспользуйтесь формой авторизации.')


class ShareForm(FlaskForm):
    figi = StringField('Figi', validators=[DataRequired()])
    isin = StringField('ISIN', validators=[DataRequired()])
    name = StringField('Наименование компании', validators=[DataRequired()])
    ticker = StringField('Тикер', validators=[DataRequired()])
    currency = StringField('Валюта', validators=[DataRequired()])
    uid = StringField('UID', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, original_share=None, *args, **kwargs):
        super(ShareForm, self).__init__(*args, **kwargs)
        self.original_share = original_share

    def validate_figi(self, field):
        share = Share.query.filter_by(figi=field.data).first()
        if share and (not self.original_share or share.id != self.original_share.id):
            raise ValidationError('Figi уже существует.')

    def validate_ticker(self, field):
        share = Share.query.filter_by(ticker=field.data).first()
        if share and (not self.original_share or share.id != self.original_share.id):
            raise ValidationError('Тикер уже существует.')

    def validate_uid(self, field):
        share = Share.query.filter_by(uid=field.data).first()
        if share and (not self.original_share or share.id != self.original_share.id):
            raise ValidationError('UID уже существует.')
