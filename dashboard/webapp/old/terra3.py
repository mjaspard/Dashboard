

info = {

        'Web Server apache':[
                'Start: sudo port load apache2',
                'Stop: sudo port unload apache2',
                'Check config: apachectl -t',
                'html path: /opt/local/www/apache2/html',
                'config path: /opt/local/etc/apache2/',
                'error path: /opt/local/var/log/apache2/']
                ,
        

        'General maintenance macport':[
                'sudo port reclaim (Reclaim disk space)',
                'port selfupdate (Update the local ports tree with the global MacPorts ports repository)',
                'sudo port upgrade outdated (The upgrade action upgrades installed ports and their dependencies to the latest version available in MacPorts)']

}

backup = {

        'Time Machine':{
                'Target': '/Volumes/Lacie-terra3-Backup/Backups.backupdb/terra3',
                'Source': 'All Boot-terra3 except ~/Downloads and ~/.Trash',
                'max_days': 1,
                'type': 'External USB 1T'
                }
        }