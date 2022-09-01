
from datetime import datetime
from webapp import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import UserMixin
from webapp import login
from hashlib import md5
import os, platform, psutil
from webapp import function_models as fm
import subprocess
import re
from webapp import app
from time import time
import jwt
from importlib.machinery import SourceFileLoader
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship


class User(UserMixin, db.Model):
    __tablename__ = 'user'
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

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    device = db.Column(db.String(30), index=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Server_info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(30))
    informations = db.Column(db.String(1000))
    server_name = db.Column(db.String(30), index=True)
    def __repr__(self):
        return '<server info  {}>'.format(self.service)

    def get_picture(self, path):
        pictures = []
        if os.path.isdir(path):
            for file in os.listdir(path):
                pictures.append(file)
            return pictures
        else:
            return None

    def attach_picture(self, file):
        filename = secure_filename(file.filename)
        filepath = self.get_picture_fullpath()
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        file.save(os.path.join(filepath, filename))


    def delete_picture(self):
        filepath = self.get_picture_fullpath()
        if os.path.isfile(filepath):
            for file in os.listdir(filepath):
                os.remove(os.path.join(filepath, file))
                os.rmdir(filepath)


    def get_picture_fullpath(self):
        path = os.path.join(current_app.root_path + '/static/pictures/' + self.server_name + '/' + self.service)
        return path

    def get_picture_localpath(self):
        path = os.path.join('/pictures/' + self.server_name + '/' + self.service)
        return path


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(15), index=True, unique=True)
    name = db.Column(db.String(30), index=True)
    user = db.Column(db.String(15), index=True)
    about_me = db.Column(db.String(300))
    public_address = db.Column(db.String(15), index=True)
    public_name = db.Column(db.String(30), index=True)
    public_server = db.Column(db.Boolean, default=False, index=True)
    os = db.Column(db.String(30), index=True)
    raminfo = db.Column(db.String(30), index=True)
    modele = db.Column(db.String(30), index=True)
    cpuinfo = db.Column(db.String(30), index=True)
    system_type = db.Column(db.String(30), index=True)
    ssh_connection = db.Column(db.Boolean, default=False, index=True)
    mount_volumes = db.Column(db.Boolean, default=False, index=True)
    mandatory_volumes = db.Column(db.String(300), default='', index=True)


    def __repr__(self):
        return '{}'.format(self.name)

    def toggle_ssh(self):
        if self.ssh_connection == True:
            return False
        else:
            return True


    def test_connect(self):
        if self.ping_ip():
            if not self.ssh_connection:
                return False, "SSH not enable for this server"
            try:
                address = self.address
                user = self.user
                # ssh = subprocess.Popen(['ssh',address, '-T', '-l',user,'-o', 'PasswordAuthentication=No','-o', 'StrictHostKeyChecking=no'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
                ssh = subprocess.Popen(['ssh',address, '-T', '-l',user,'-o', 'PreferredAuthentications=publickey'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,  universal_newlines=True, bufsize=0)
                cmd = "exit"
                finalCMD = "{} \n".format(cmd)
                ssh.stdin.write(finalCMD)
                ssh.stdin.close()
                sshError = ssh.stderr.readlines()
                if len(sshError) > 0:
                    for msg in sshError:
                        print(msg)
                        return False, "ssh error: {}".format(msg)
                if len(sshError) == 0:
                    return True, "ok"
            except:
                return False, "unknown issue"
        else:
            return False, "server is not pingable"  


    def deco_test_ssh(function):
        def test_ssh(self):
            if self.ping_ip():
                test = subprocess.Popen(f"ssh -o StrictHostKeyChecking=no -o PasswordAuthentication=No -l {self.user} {self.address} {'exit'}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                test = test[0].decode('ascii')
                if re.search('denied', str(test)):
                    return False
                else:
                    return function(self)
            else:
                return False
        return test_ssh

    def deco_unix_like(function):
        def unix_like(self):
            if (re.search('Darwin', self.system_type)) or (re.search('Linux', self.system_type)):
                return function(self)
            else:
                return False
        return unix_like

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
        resp = "{}".format(resp)
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


    def check_mandatory_volumes_old(self):
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

    def check_mandatory_volumes(self):
            volumes = "[]"
            try:
                volumes = self.mandatory_volumes.split(",")
                return volumes
            except:
                return ''



    def get_mounted_volumes(self):
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
                            volumes = ''
        if volumes == '':
            return False
        return volumes

    @deco_test_ssh
    def check_mounted_all_volumes(self):
        volumes  = self.get_mounted_volumes() 
        i = 0
        if volumes:
            volumes = volumes.split(",")
            for vol in volumes:
                x = self.check_mounted_volumes(vol)[0]
                if not x:
                    i += 1
            if i == 0:
                return True, True
            else:
                return True, False


    def check_mounted_volumes(self, volume_name):
            x = self.get_sysinfo()
            volume_name = re.search(r"\w.*\w", volume_name)[0]   # Keep only alaphanum  (removes spaces)
            if re.search('Darwin', self.system_type):
                cmd = 'ls -l /Volumes/' + volume_name  + ' | wc -l'
            else:
                cmd = 'ls -l /mnt/' + volume_name  + ' | wc -l'
            resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()       
            resp = resp[0].decode('ascii')
            resp = int(resp)
            if resp <= 1:
                return False, resp
            else:
                return True, resp


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
            if len(foo.backup) != 0:
                return True, foo.backup.items()
            else:
                return False, ''
        except:
            return False, ''



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
        # backups = self.get_backup_info()[1]
        i = 0
        for backup, details in self.get_backup_info()[1]:
            if not self.check_backup_last_update(details['Target'], details['max_days']):
                i += 1
        if i == 0:
            return True
        else:
            return False


    # def check_vol_capacity(self):
    #     values = {}
    #     if (self.get_mounted_volumes()) and (self.mount_volumes):
    #         volumes = self.check_mandatory_volumes()
    #         i = 0
    #         for vol in volumes:
    #             vol = vol.strip(' ')
    #             volume = '/Volumes/{}'.format(vol)
    #             filter1 = '{\'print $2\'}'
    #             cmd = ['df',  '-h', volume]
    #             resp = subprocess.Popen(('df',  '-h', volume), stdout=subprocess.PIPE)
    #             resp1 = subprocess.check_output(('grep', volume), stdin=resp.stdout) 
    #             resp1 = resp1.decode('ascii')
    #             total = resp1.split(' ')[3]
    #             total_vol = int(re.search(r"\d*",total)[0])
    #             total_unit = re.search(r"\D{2}",total)[0]
    #             used_vol = re.search(r"\d+%", resp1)[0]
    #             used_vol = int(re.search(r"\d*", used_vol)[0]) # in percent
    #             cnt = i
    #             i += 1
    #             values[vol] = [total_vol, total_unit, used_vol, cnt]
    #             # return values, len(values)
    #     elif (self.check_mandatory_volumes() != ['']) and (not self.mount_volumes):
    #         volumes = self.check_mandatory_volumes()
    #         i = 0
    #         for vol in volumes:
    #             cmd = 'df -H | grep ' + vol 
    #             resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
    #             resp = resp[0].decode('ascii')
    #             try:
    #                 total = re.search(r"\s\d+\.*\d+[G|T]", resp)[0] # search number + unit total volume icluding decimal   
    #                 total_vol = re.search(r"\d+\.*\d+",total)[0] # remove unit
    #                 total_unit = re.search(r"[G|T]",total)[0]  # remove numbers
    #                 used_vol = re.search(r"\d+\.*\d+%", resp)[0]
    #                 used_vol = int(re.search(r"\d+\.*\d+", used_vol)[0]) # remove percent
    #                 cnt = i
    #                 i += 1
    #             except:
    #                 continue

    #             # values[vol] = resp
    #             values[vol] = [total_vol, total_unit, used_vol, cnt]
    #     else:
    #         return False, False
    #     return values, len(values)

    def check_vol_capacity(self):
        mounted_volume = {}
        local_volume = {}
        if self.mount_volumes:
            volumes = self.check_mandatory_volumes()
            i = 0
            for vol in volumes:
                vol = vol.strip(' ')
                volume = '/Volumes/{}'.format(vol)
                filter1 = '{\'print $2\'}'
                cmd = ['df',  '-H', volume]
                resp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                resp1 = subprocess.check_output(('grep', volume), stdin=resp.stdout) 
                resp1 = resp1.decode('ascii')
                total_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp1)[0]
                used_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp1)[1]
                used_vol = fm.convert_to_gigabyte(used_vol_str)
                avail_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp1)[2]
                avail_vol = fm.convert_to_gigabyte(avail_vol_str)
                mounted_volume[vol] = [total_vol_str, used_vol, used_vol_str, avail_vol, avail_vol_str ]
        elif not self.mount_volumes:
            local_volume = self.read_local_storage()
            if self.check_mandatory_volumes() != ['']:
                volumes = self.check_mandatory_volumes()
                i = 0
                for vol in volumes:
                    cmd = 'df -H | grep ' + vol 
                    resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
                    resp = resp[0].decode('ascii')
                    try:
                        total_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp)[0]
                        used_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp)[1]
                        used_vol = fm.convert_to_gigabyte(used_vol_str)
                        avail_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp)[2]
                        avail_vol = fm.convert_to_gigabyte(avail_vol_str)
                    except:
                        continue
                    mounted_volume[vol] = [total_vol_str, used_vol, used_vol_str, avail_vol, avail_vol_str ]
        else:
            return False, False
        
        all_volumes = {**mounted_volume, **local_volume}
        return all_volumes, len(all_volumes)


    @deco_unix_like
    def read_local_storage(self):
        vol_data = {}
        if  re.search('Darwin', self.system_type):
            cmd = 'diskutil list | grep internal | tail -1' 
            resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
            resp = resp[0].decode('ascii')
            resp = resp.split('\n')
            for vol in resp:
                if not vol:
                        continue
                location, vol_path = fm.get_synth_disk_info_mac(vol)
                cmd = 'df -H | grep ' + vol_path + ' | head -1' 
                resp1 = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
                resp1 = resp1[0].decode('ascii')  
                total_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp1)[0]
                total_vol = fm.convert_to_gigabyte(total_vol_str)
                avail_vol_str = re.findall(r"\s\d+\.*\d+[G|T]", resp1)[2]
                avail_vol = fm.convert_to_gigabyte(avail_vol_str)
                used_vol = total_vol - avail_vol
                if re.search(r"\d{4}\d*", str(used_vol)):
                    used_vol_str = float(used_vol/1000)
                    used_vol_str = "{} TB".format(str(used_vol_str))
                else:
                    used_vol_str = "{} GB".format(str(used_vol))
                vol_data[location] = [total_vol_str, used_vol, used_vol_str, avail_vol, avail_vol_str]
        if  re.search('Linux', self.system_type):
            cmd = 'lsblk | grep disk | grep mnt' 
            resp = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
            resp = resp[0].decode('ascii')
            resp = resp.split('\n')
            for vol in resp:
                if not vol:
                        continue
                location, vol_path = fm.get_disk_info_linux(vol)
                cmd = 'df -H | grep ' + vol_path + ' | head -1' 
                resp1 = subprocess.Popen(f"ssh {self.user}@{self.address} {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()  
                resp1 = resp1[0].decode('ascii')  
                total_vol_str = re.findall(r"\s\d+\,*\d+[G|T]", resp1)[0]
                total_vol = fm.convert_to_gigabyte(total_vol_str)
                avail_vol_str = re.findall(r"\s\d+\,*\d+[G|T]", resp1)[2]
                avail_vol = fm.convert_to_gigabyte(avail_vol_str)
                used_vol = total_vol - avail_vol
                if re.search(r"\d{4}\d*", str(used_vol)):
                    used_vol_str = float(used_vol/1000)
                    used_vol_str = "{} TB".format(str(used_vol_str))
                else:
                    used_vol_str = "{} GB".format(str(used_vol))
                vol_data[location] = [total_vol_str, used_vol, used_vol_str, avail_vol, avail_vol_str]
        return vol_data



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







