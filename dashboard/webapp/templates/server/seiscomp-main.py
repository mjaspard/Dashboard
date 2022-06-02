info = {

        'Seiscomp':[
                'This server hosts seiscomp software and perform the data acquisition of all stations by the module seedlimk.',
                'The data are directly stored on SDS disk by sdsarchive module.',
                'Please find below a graphics representing different configuration of seiscomp.']
                ,
        
        'Images':{
                'Seiscomp configuration':'Seiscomp_config.png'
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