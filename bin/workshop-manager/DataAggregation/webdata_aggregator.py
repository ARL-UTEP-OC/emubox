import time
import traceback
import VMStateManager.vbox_monitor
import glob
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

def aggregateData():
    global aggregatedInfo
    while True:
        try:
            #should scan file system and then aggregate any information at the unit level
            monitorInfo = VMStateManager.vbox_monitor.getAvailableInfo()
            aggregatedInfoSem.wait()
            aggregatedInfoSem.acquire()
            aggregatedInfo = []
            for vmInfo in monitorInfo:
                vm = vmInfo[0]
                workshopName = vm["groups"][0].split("/")[1]
                if len(workshopName) < 0:
                    workshopName = vm["groups"][0]
                ###########Look for RDP Info########
                rdpFilename = os.path.join("WorkshopData", workshopName,"RDP", vm["name"]+"_"+vm["vrdeproperty[TCP/Ports]"]+".rdp")
                logging.debug( "LOOKING FOR "+rdpFilename)
                if os.path.isfile(rdpFilename):
                    logging.debug("FOUND: " +rdpFilename)
                materialsPath = os.path.join("WorkshopData", workshopName,"Materials")
                files = os.listdir(materialsPath)
                filesPaths = []
                for file in files:
                    if os.path.isfile(os.path.join(materialsPath,file)):
                        filesPaths.append((os.path.join(materialsPath, file), file))
                print "FOUND FILES IN DIR: ", files
                aggregatedInfo.append({"workshopName" : workshopName, "VM Name" : vm["name"], "ms-rdp" : rdpFilename, "state" : vmInfo[1], "materials" : filesPaths})
            aggregatedInfoSem.release()
            time.sleep(probeTime)
        except Exception as e:
            logging.error("AGGREGATION: An error occured: " + str(e))
            traceback.print_exc()
            exit()
            time.sleep(probeTime)

def getAggregatedInfo():
    aggregatedInfoSem.wait()
    return aggregatedInfo

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    mydata = aggregateData()

    # stateAggregationThread = gevent.spawn(manageStates)
    # restoreThread = gevent.spawn(makeRestoreToAvailableState)
    #
    # try:
    #     gevent.joinall([stateAssignmentThread, restoreThread])
    # except Exception as e:
    #     logging.error("An error occured in threads"+str(e))
    #     exit()
