info = {

        'Seiscomp':[
                'This server hosts seiscomp software and perform the data acquisition of all stations by the module seedlink.',
                'The data are directly stored on SDS disk by sdsarchive module.',
                'Helicorder module send last 24H Seismogram to https://www.ecgs.lu/seismic-networks/',
                '\'Seiscomp_config.png\' represents different configuration of seiscomp including seiscomp-main.',
                '\'Seiscomp-theBeast_script.png\' display data flow executed automatically by seiscomp-main (up) and the-beast (down).'
                ]
                ,
        
        'Images':{
                'Img 1: Seiscomp configuration':'Seiscomp_config.png',
                'Img 2: Seiscomp automatic scripts':'Seiscomp-theBeast_script.png'
                }
        }


backup = {

        'Time Machine':{
                'Target': '/Volumes/TM-seiscomp-main',
                'Source': 'All seiscomp-main except SDSdisk',
                'max_days': 1,
                'type': 'External firewire 2T'
                }
        }