from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, IPAddress, Length
from webapp.models import User, Server

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class AddServerForm(FlaskForm):
    user = StringField('Login User', validators=[DataRequired()])
    address = StringField('Local IP address', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message=None)])
    name = StringField('Local hostname', validators=[DataRequired()])
    public_server = BooleanField('Public Server')
    public_address = StringField('Public IP address', default='0.0.0.0', validators=[IPAddress(ipv4=True, ipv6=False, message=None)])
    public_name = StringField('Public hostname')
    about_me = TextAreaField('About this server', validators=[Length(min=0, max=140)])
    submit = SubmitField('Save data')

    def __init__(self, new):
        super(AddServerForm, self).__init__()
        self.new = new

    def validate_address(self, address):
        x = Server.query.filter_by(address=address.data).first()
        if x is not None and self.new:
            raise ValidationError('Please use a different IP address.')

    def validate_servername(self, name):
        x = Server.query.filter_by(name=name.data).first()
        if x is not None and self.new:
            raise ValidationError('Please use a different name for this server.')

class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Add comments', validators=[DataRequired(), Length(min=1, max=1000)])
    device = SelectField('Select device', choices=Server.query.all())
    submit = SubmitField('Submit')