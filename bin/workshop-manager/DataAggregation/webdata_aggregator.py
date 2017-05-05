import time
import traceback
import VMStateManager.vbox_monitor
import os

# gevent imports
import gevent
import gevent.monkey
from gevent.lock import BoundedSemaphore
gevent.monkey.patch_all()

#to reduce stdout
import logging

probeTime = 5
aggregatedInfo = []

# vars needed for gevent (lock)
aggregatedInfoSem = BoundedSemaphore(1)

def cleanup():
    logging.info("Cleaning up webdata aggregator...")
    try:

        logging.info("Clean up complete. Exitting...")
    except Exception as e:
        logging.error("Error during cleanup"+str(e))

def aggregateRDP():
    global aggregatedInfo
    while True:
        try:
            #should scan file system and then aggregate any information at the unit level
            monitorInfo = VMStateManager.vbox_monitor.getAvailableInfo()
            aggregatedInfoSem.wait()
            aggregatedInfoSem.acquire()
            aggregatedInfo = []
            for vm in monitorInfo:
                rdp_filename = os.path.join("WorkshopData", "RDP", ""+vm["name"]+"_"+vm["vrdeproperty[TCP/Ports]"]+".rdp")
                logging.debug( "LOOKING FOR "+rdp_filename)
                if os.path.isfile(rdp_filename):
                    logging.debug("FOUND: " +rdp_filename)
                    workshopName = vm["groups"][0].split("/")[1]
                    if len(workshopName) < 0:
                        workshopName = vm["groups"][0]
                    aggregatedInfo.append({"workshopName" : workshopName, "VM Name" : vm["name"], "ms-rdp" : rdp_filename})
                    #aggregatedInfo.append(({"groups": "a"}))
            aggregatedInfoSem.release()
            time.sleep(probeTime)
        except Exception as e:
            logging.error("AGGREGATION: An error occured: " + str(e))
            traceback.print_exc()
            exit()
            time.sleep(probeTime)

def getAggregatedInfo():
    aggregatedInfoSem.wait()
    aggregatedInfo
    return aggregatedInfo

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    mydata = aggregateRDP()

    # stateAggregationThread = gevent.spawn(manageStates)
    # restoreThread = gevent.spawn(makeRestoreToAvailableState)
    #
    # try:
    #     gevent.joinall([stateAssignmentThread, restoreThread])
    # except Exception as e:
    #     logging.error("An error occured in threads"+str(e))
    #     exit()
