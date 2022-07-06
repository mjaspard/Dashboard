info = {

        'Seismo20TA':[
                'This server manages the manipulation of seismic data and store all datas in drive Seismo20TA:',
                '       -  from SDS disk (Seiscomp-main) to Seismo20TA/SDSarchive/Merged for continuous transmitted data (automatic)',
                '       -  from SD card to Seismo20TA/RAW for datas retreive manually from seismic station (manually)',
                '       -  Uniformisation of datas from Seismo20TA/RAW to Seismo20TA/SDSarchive/Local (manually)',
                '       -  Merege Seismo20TA/SDSarchive/Local and  transmitted data to Seismo20TA/SDSarchive/Merged (manually)'
                '       -  Convert all data in a common format and merge tool ara available',
                '       -  Plot automatically State-of-health to https://www.ecgs.lu/sismo-volc/ (automatic)',
                '\'Seiscomp-theBeast_script.png\' display data flow executed automatically by seiscomp-main (up) and the-beast (down).',
                '\'TheBeast-seismo20T_scripts.png\' display seismic data manipulation performed by scripts Matlab',
                '\'TheBeast-seismo20T_scripts_python.png\' display seismic data manipulation performed by scripts Python'
                ]
                ,
        
        'Images':{
                'Seiscomp and the-beast automatic scripts':'Seiscomp-theBeast_script.png',
                'Seismo20TA: Data Management (matlab)':'TheBeast-seismo20T_scripts.png',
                'Seismo20TA: Data Management (python)':'TheBeast-seismo20T_scripts_python.png'
                }
        }


backup = {

        'Time Machine':{
                'Target': '/Volumes/TM-the-beast',
                'Source': 'All he-beast except Seismo20TA and shared user',
                'max_days': 2,
                'type': 'External USB 4T'
                }
        }