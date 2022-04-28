import os
basedir = os.path.abspath(os.path.dirname(__file__))

print("basedir = {}".format(basedir))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'test'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.environ.get('mail.ecgs.lu')
	MAIL_PORT = int('587')
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('maxime')
	MAIL_PASSWORD = os.environ.get('***')
	ADMINS = ['maxime@ecgs.lu']



