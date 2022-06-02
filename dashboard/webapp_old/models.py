
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
from importlib.machinery import SourceFileLoader


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
    ssh_connection = db.Column(db.Boolean, default=True, index=True)


    def __repr__(self):
        return '{}'.format(self.name)

    def toggle_ssh(self):
        if self.ssh_connection == True:
            return False
        else:
            return True




    def test_connect(self):
        if self.ping_ip():
            test = subprocess.Popen(f"ssh -o StrictHostKeyChecking=no -o NumberOfPasswordPrompts=0 -l {self.user} {self.address} {'exit'}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            test = test[0].decode('ascii')
            if re.search('denied', str(test)):
                return "server is not reachable via ssh" 
            else:
                return "OK"
        else:
            return "server is not pingable"   


    def deco_test_ssh(function):
        def test_ssh(self):
            if self.ping_ip():
                test = subprocess.Popen(f"ssh -o StrictHostKeyChecking=no -o NumberOfPasswordPrompts=0 -l {self.user} {self.address} {'exit'}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                test = test[0].decode('ascii')
                if re.search('denied', str(test)):
                    return False
                else:
                    return function(self)
            else:
                return False
        return test_ssh

    def ping_ip(self):
        response = os.system("ping -c 1 -t 2 " + self.address)
        if response == 0:
            return True
        else:
            return False

    def ping_hostname(self):
        response = os.system("ping -c 1 -t 2 " + self.name)
        if response == 0:
            return True
        else:
            return False

    def ping_public_ip(self):
        if self.public_server:
            response = os.system("ping -c 1 -t 2 " + self.public_address)
            if response == 0:
                return True
            else:
                return False
        else:
            return True

    def ping_public_hostname(self):
        if self.public_server and self.public_name != None:
            response = os.system("ping -c 1 -t 2 " + self.public_name)
            if response == 0:
                return True
            else:
                return False
        else:
            return True

    @deco_test_ssh
    def ping_all(self):
        if self.ping_ip() and self.ping_hostname() and self.ping_public_ip() and self.ping_public_hostname():
            return True
        else:
            return False


    def get_sysinfo(self):
        cmd = 'uname'
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        resp = resp[0].decode('ascii')
        self.system_type = str(resp)
        return str(resp)


    def get_raminfo(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'system_profiler SPHardwareDataType | grep "Memory:"'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'free -h | grep Mem: | awk {\'print $2\'}'
        else:
            return ""
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
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
            return ""
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        resp = resp[0].decode('ascii')
        self.os = resp
        return resp


    def get_cpuinfo(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'sysctl -n machdep.cpu.brand_string'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'lscpu | grep "Model name" | cut -d \':\' -f 2 | sed \'s/^ *//g\''
        else:
            return ""
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        resp = resp[0].decode('ascii')
        self.cpuinfo = resp
        return resp

    def get_modele(self):
        if re.search('Darwin', self.get_sysinfo()):
            cmd = 'system_profiler SPHardwareDataType | grep "Model Identifier" | cut -d ":" -f 2'
        elif re.search('Linux', self.get_sysinfo()):
            cmd = 'cat /sys/devices/virtual/dmi/id/product_name'
        else:
            return ""
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        resp = resp[0].decode('ascii')
        self.modele = resp
        return resp


    def check_mandatory_volumes(self):
            volumes = "[]"
            home = os.getcwd()
            file = "{}/webapp/templates/server/mounted_volumes.txt".format(home)
            with open (file, "r") as f:
                for line in f:
                        server_x = "{}:".format(self.name)
                        if re.search(server_x, line):
                                volumes = line.split(":")[1]
                                volumes = re.search(r"\w.*\w", volumes)[0]  # Keep only alaphanum
                                break
                        else:
                                volumes = ""
            volumes = volumes.split(",")
            return volumes

    @deco_test_ssh
    def check_mounted_all_volumes(self):
            i = 0
            volumes = "[]"
            home = os.getcwd()
            file = "{}/webapp/templates/server/mounted_volumes.txt".format(home)
            with open (file, "r") as f:
                for line in f:
                        server_x = "{}:".format(self.name)
                        if re.search(server_x, line):
                                volumes = line.split(":")[1]
                                volumes = re.search(r"\w.*\w", volumes)[0]  # Keep only alaphanum (removes spaces)
                                break
                        else:
                                volumes = ""
            volumes = volumes.split(",")
            for vol in volumes:
                if re.search('Darwin', self.system_type):
                    cmd = 'ls -l /Volumes/' + vol + ' | wc -l'
                else:
                    cmd = 'ls -l /mnt/' + vol + ' | wc -l'
                resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                resp = resp[0].decode('ascii')
                resp = int(resp)
                # resp1 = re.search(r"\d.*\d", resp1)[0]  # Keep only alaphanum
                if resp == 0 or resp == 64:
                    i += 1
            if i == 0:
                return True
            else:
                return False


    def check_mounted_volumes(self, volume_name):
            x = self.get_sysinfo()
            volume_name = re.search(r"\w.*\w", volume_name)[0]   # Keep only alaphanum  (removes spaces)
            if re.search('Darwin', self.get_sysinfo()):
                cmd = 'ls -l /Volumes/' + volume_name  + ' | wc -l'
            else:
                cmd = 'ls -l /mnt/' + volume_name  + ' | wc -l'
            resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()       
            resp = resp[0].decode('ascii')
            resp = int(resp)
            if resp == 0 or resp == 64:
                return False
            else:
                return True


    def get_server_info(self):
        home = os.getcwd()
        file = "{}/webapp/templates/server/{}.py".format(home, self.name)
        try:
            foo = SourceFileLoader("info", file).load_module()
        except:
            return 0
        return foo.info.items()


    def get_backup_info(self):
        home = os.getcwd()
        file = "{}/webapp/templates/server/{}.py".format(home, self.name)    
        try: 
            foo = SourceFileLoader("backup", file).load_module()
            foo.backup
            return foo.backup.items()
        except:
            return False


    def check_backup_last_update(self, path_backup, max_days):
        folder = path_backup.split("/")[-1]
        cmd = 'find ' + path_backup + ' -name ' + folder + ' -maxdepth 1 -mtime -' + str(max_days) + ' | wc -l | grep -o [0-9].*'
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()       
        resp = resp[0].decode('ascii')
        resp = int(resp)
        if resp >= 1:
            return True
        else:
            return False

    
    def check_all_backup(self):
        backups = self.get_backup_info()
        i = 0
        for backup, details in self.get_backup_info():
            if not self.check_backup_last_update(details['Target'], details['max_days']):
                i += 1
        if i == 0:
            return True
        else:
            return False




    def test(self, path_backup, max_days):
        folder = path_backup.split("/")[-1]
        cmd = 'find ' + path_backup + ' -name ' + folder + ' -maxdepth 1 -mtime -' + str(max_days) + ' | wc -l | grep -o [0-9].*'
        resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()       
        resp = resp[0].decode('ascii')
        resp = int(resp)
        if resp >= 1:
            return resp
        else:
            return resp

