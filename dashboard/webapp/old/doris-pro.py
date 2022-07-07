

info = {

        'InSAR':[
                'MSBAS full automatic process for Congo (S1 + CSK) and Piton de la fournaise (S1)',
                'Gif creation from amplitude S1 image of Nyigo and Nyam crater',
                'All scripts used for the automatic process are stored in ~/PROCESS/SCRIPTS_OK/ and available at https://github.com/ndoreye/SCRIPTS_OK.git ',
                'Documentation can be found in ~/SAR/DOC/...'],
                
        
        'CSL InSAR Suite':[
                'CSL suite must be compiled on the system and the path to executable written in the $PATH (in .bashrc)',
                '/Application/CSL_Insar hosts source files and binaries from CSL (Dominic) for all interferometric programs',
                '/Application/3Dsbas/ hosts source files and binaries from for all MSBAS programs (Sergei)'],

        'Mounted drive':[
                'syno-sar must be mounted using following link:',
                '       smb://sar-user:syn0SAR@syno-sar.ecgs.welter/DataSAR']
        }


backup = {

        'Time Machine':{
                'Target': '/Volumes/SAR_20T_N1/Backups.backupdb/doris-pro',
                'Source': 'All doris-pro except ???',
                'max_days': 1,
                'type': 'External USB 1T'
                },
                   
        }