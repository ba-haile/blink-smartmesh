#!/usr/bin/python

# This script subscribes to data notifications and looks for Blink packets

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import traceback
import json
import datetime

from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe
from SmartMeshSDK.protocols.blink       import blink

#============================ helper functions ================================

def handle_data(notifName, notifParams):
    mac_address = '-'.join(['%02x'%b for b in notifParams.macAddress])
    payload     = ''.join([chr(b) for b in notifParams.data])
    listRSSI = []
    listNeighbor = []
    try: 
        data, neighbors = blink.decode_blink(payload)
        if data:
            print 'Blink packet received from {0}'.format(mac_address)
            for neighbor_id, rssi in neighbors:
                print '    --> Neighbor ID = {0},  RSSI = {1}'.format(neighbor_id, rssi)
                listRSSI.append(rssi)
                listNeighbor.append(neighbor_id)                
            if len(listNeighbor) == 1:
                jsonRssi = {'Time': '{}'.format(datetime.datetime.now()), 'Payload':'{}'.format(data),'BlinkAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'RSSI': '{0}'.format(listRSSI[0])}]}
            elif len(listNeighbor) == 2:
                jsonRssi = {'Time': '{}'.format(datetime.datetime.now()), 'Payload':'{}'.format(data),'BlinkAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'RSSI': '{0}'.format(listRSSI[1])}]}
            elif len(listNeighbor) == 3:
                jsonRssi = {'Time': '{}'.format(datetime.datetime.now()), 'Payload':'{}'.format(data),'BlinkAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'RSSI': '{0}'.format(listRSSI[1])},{'MoteID': '{0}'.format(listNeighbor[2]), 'RSSI': '{0}'.format(listRSSI[2])}]}
            else:
                jsonRssi = {'Time': '{}'.format(datetime.datetime.now()), 'Payload':'{}'.format(data),'BlinkAddress': '{0}'.format(mac_address), 'HeardMote': [{'MoteID': '{0}'.format(listNeighbor[0]), 'RSSI': '{0}'.format(listRSSI[0])},{'MoteID': '{0}'.format(listNeighbor[1]), 'RSSI': '{0}'.format(listRSSI[1])},{'MoteID': '{0}'.format(listNeighbor[2]), 'RSSI': '{0}'.format(listRSSI[2])},{'MoteID': '{0}'.format(listNeighbor[3]), 'RSSI': '{0}'.format(listRSSI[3])}]}
            with open('RSSIvalue.json', 'a') as f:                    
                f.write(json.dumps(jsonRssi))
                f.write('\n')                                                    
            if not neighbors:
                print '    --> Neighbors = n/a'            
            print '    --> Data Sent = {0}\n\n'.format(data.encode("hex"))
            
    except:
        # handle non-blink data
        pass


#============================ main ============================================

try:
    print 'MgrBlinkData (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    print 'Note: Use with BlinkPacketSend.py \n'
    
    #=====
    print "- create the variable 'mgrconnector'"
    
    mgrconnector  = IpMgrConnectorSerial.IpMgrConnectorSerial()
    
    #===== 
    print "- connect to the manager's serial port"
    
    serialport     = raw_input("Enter the serial API port of SmartMesh IP Manager (e.g. COM7): ")
    mgrconnector.connect({'port': serialport})
    
    #=====
    print "- subscribe to data notifications "
    
    subscriber = IpMgrSubscribe.IpMgrSubscribe(mgrconnector)
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                        ],
        fun =           handle_data,
        isRlbl =        False,
    )

    #===
    raw_input("Press any key to stop.\n\n")
    
    mgrconnector.disconnect()
    
    print 'Script ended normally.'

except:
    traceback.print_exc()
    print 'Script ended with an error.'
    
raw_input('Press Enter to close.')



