

info = {

        'Web Server apache':[
                'Start: sudo serveradmin start WEB',
                'Stop: sudo serveradmin stop WEB',
                'html path: /Library/Server/Web/Data/Sites',
                'config path: /etc/apache2/...',
                'error path: /var/log/apache2/']
                ,
        

        'General maintenance macport':[
                'sudo port reclaim (Reclaim disk space)',
                'port selfupdate (Update the local ports tree with the global MacPorts ports repository)',
                'sudo port upgrade outdated (The upgrade action upgrades installed ports and their dependencies to the latest version available in MacPorts)']

        }


backup = {

        'Chronosync Weekly':{
                'Target': '/Volumes/Backup-terra2-Lacie',
                'Source': 'Root folder of Boot-SSD',
                'max_days': 7,
                'type': 'External USB 1TB'
                },
        
        'Chronosync Daily':{
                'Target': '/Volumes/Backup-HD',
                'Source': 'Root folder of Boot-SSD',
                'max_days': 1,
                'type': 'External USB 1TB'}
        }

               
