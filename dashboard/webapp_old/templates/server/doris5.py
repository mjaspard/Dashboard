

info = {

        'InSAR':[
                'Satellite data (S1, CSK) acquisition',
                'S1 crontab: /Users/doris/scripts/sentinel1_download_all.sh',
                'CSK crontab: /Users/doris/scripts/CSK_download_VVP.sh']
                ,
        
        'Sentinel 2':[
                'Satellite image S2 acquisition',
                'Creation of crop image and GIF of volcanoes crater and synchronise with website (now on Maxime mac)',
                'S2 crontab: /Users/doris/scripts/sentinel2_downloader_ingestiondate.sh',
                'Process crater picture: /Volumes/hp-D3601-Data_RAID6/Sentinel2_data/S2_scripts/Run_All_S2_to_Geotif.sh VegeAna']
        }


backup = {

        'Time Machine':{
                'Target': '/Volumes/DORIS5-TimeMachine-backup/Backups.backupdb/doris5',
                'Source': 'All doris5-BootHD except doris5-BootHD-Clone, /Applicatiosn, /System ',
                'max_days': 1,
                'type': 'External USB 1T'
                },
                   
        'Clone':{
                'Target': '/Volumes/doris5-BootHD-Clone',
                'Source': 'All doris5-BootHD except doris5-BootHD-Clone, /Applicatiosn, /System ',
                'max_days': 500,
                'type': 'Internal 750GB'
                }
        }