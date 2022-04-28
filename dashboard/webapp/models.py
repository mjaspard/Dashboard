
from datetime import datetime
from webapp import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from webapp import login
from hashlib import md5
import os, platform, psutil
from webapp import function_models as fm
import subprocess
import re

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    device = db.Column(db.String(30), index=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(15), index=True, unique=True)
    name = db.Column(db.String(30), index=True)
    user = db.Column(db.String(15), index=True)
    about_me = db.Column(db.String(140))
    public_address = db.Column(db.String(15), index=True)
    public_name = db.Column(db.String(30), index=True)
    public_server = db.Column(db.Boolean, default=False, index=True)
    os = db.Column(db.String(30), index=True)
    raminfo = db.Column(db.String(30), index=True)
    modele = db.Column(db.String(30), index=True)
    cpuinfo = db.Column(db.String(30), index=True)
    system_type = db.Column(db.String(30), index=True)


    def __repr__(self):
        return '{}'.format(self.name)

    def ping_ip(self):
        response = os.system("ping -c 1 " + self.address)
        return response

    def ping_hostname(self):
        response = os.system("ping -c 1 " + self.name)
        return response

    def ping_public_ip(self):
        if self.public_server:
            response = os.system("ping -c 1 " + self.public_address)
            return response

    def ping_public_hostname(self):
        if self.public_server and self.public_name != None:
            response = os.system("ping -c 1 " + self.public_name)
            return response


    def test_ssh(self):
        test = subprocess.Popen(f"ssh -o StrictHostKeyChecking=no -o NumberOfPasswordPrompts=0 -l {self.user} {self.name} {'exit'}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        test = test[1].decode('ascii')
        if re.search('denied', str(test)):
            return False
        else:
            return True

    def get_sysinfo(self):
        cmd = 'uname'
        if not self.test_ssh():
            return 'ssh to server failed'
        else:
            resp = subprocess.Popen(f"ssh {self.user}@{self.name} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            resp = resp[0].decode('ascii')
            self.system_type = str(resp)
            return str(resp)


    def get_raminfo(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'system_profiler SPHardwareDataType | grep "Memory:"'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'free -h | grep Mem: | awk {\'print $2\'}'
        else:
            return ''
        if not self.test_ssh():
            return 'ssh to server failed'
        else:
            resp = subprocess.Popen(f"ssh {self.user}@{self.name} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            resp = re.search(r'[0-9].*[TG].', str(resp))[0]
            resp = "RAM: {}".format(resp)
            self.raminfo = resp
            return resp


    def get_os(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd= 'system_profiler SPSoftwareDataType | grep "System Version" | cut -d \':\' -f 2 | cut -d \'(\' -f 1'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'cat /etc/os-release | grep PRETTY_NAME | cut -d "=" -f 2 | sed \'s/"//g\''
        else:
            return ''
        if not self.test_ssh():
            return ''
        else:
            resp = subprocess.Popen(f"ssh {self.user}@{self.name} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            resp = resp[0].decode('ascii')
            self.os = resp
            return resp


    def get_cpuinfo(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'sysctl -n machdep.cpu.brand_string'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'lscpu | grep "Model name" | cut -d \':\' -f 2 | sed \'s/^ *//g\''
        else:
            return ''
        if not self.test_ssh():
            return ''
        else:
            resp = subprocess.Popen(f"ssh {self.user}@{self.name} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            resp = resp[0].decode('ascii')
            self.cpuinfo = resp
            return resp

    def get_modele(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'system_profiler SPHardwareDataType | grep "Model Identifier" | cut -d ":" -f 2'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'cat /sys/devices/virtual/dmi/id/product_name'
        else:
            return ''
        if not self.test_ssh():
            return ''
        else:
            resp = subprocess.Popen(f"ssh {self.user}@{self.name} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            resp = resp[0].decode('ascii')
            self.modele = resp
            return resp
