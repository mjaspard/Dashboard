

info = {

        'GPS':[
                'Bernese Software (ITR2008) is running on this system:',
                'This server is running Bernese with reference frame (ITR2008).',
                'Data from station are first downloaded on Syno-congo (DATARDC) where the scripts start to process gps data.',
                'Web page are displayed on https://www.ecgs.lu/gps-backup']
                ,
        
        'Bernese Software':[
                'Here under 2 links with documentation about GPS processing details:',
                'Data Processing: Graphical representation of data processing throw Bernese folders with scripts name informations.',
                'Bernese folders: Main folders used by Bernese to store data.<br> Important files are mentionned and a small explanation about reference frame update',
                ],
        'Images':{
                'Gorisk Bernese Folders':'Gorisk_BerneseFolders.png',
                'Gorisk Data Processing':'Gorisk_DataProcess.png'
                }
        }


backup = {

        'Time Machine':{
                'Target': '/Volumes/Bern-Gorisk-Bkup-TimeMachine/Backups.backupdb/bern-gorisk-bkup',
                'Source': 'All Bern-Gorisk-Bkup-BootHD except 2 Clones, System files and Applications ',
                'max_days': 1,
                'type': 'External USB 2.5TB'
                },
                   
        'Clone1':{
                'Target': '/Volumes/Bern-Gorisk-Bkup-BootHD-Clone',
                'Source': 'All Bern-Gorisk-Bkup-BootHD',
                'max_days': 365,
                'type': 'External USB 1TB'
                },
        'Clone2':{
                'Target': '/Volumes/BernGorisk-Bkup-Clone2',
                'Source': 'All Bern-Gorisk-Bkup-BootHD',
                'max_days': 365,
                'type': 'External USB 500GB'
                }
        }