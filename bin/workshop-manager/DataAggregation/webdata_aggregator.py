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

# Queue import
from Queue import *

probeTime = 5
aggregatedInfo = []
availableWorkshops = []

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
                logging.debug( "WORKSHOP NAME: "+ str(workshopName))
                ###########Look for RDP Info########
                rdpFilename = os.path.join("WorkshopData", workshopName,"RDP", vm["name"]+"_"+vm["vrdeproperty[TCP/Ports]"]+".rdp").replace('\\', '/')
                rdesktopFilename = os.path.join("WorkshopData", workshopName, "RDP",vm["name"] + "_" + vm["vrdeproperty[TCP/Ports]"] + ".sh").replace('\\', '/')
                logging.debug( "LOOKING FOR "+str(rdpFilename) + " or " + str(rdesktopFilename))
                if os.path.isfile(rdpFilename) == False:
                    rdpFilename = ""
                if os.path.isfile(rdesktopFilename) == False:
                    rdesktopFilename = ""

                if rdpFilename != "" or rdesktopFilename != "":
                    logging.debug("FOUND FILE")
                    filesPaths = []
                    materialsPath = os.path.join("WorkshopData", workshopName,"Materials")
                    if os.path.isdir(materialsPath):
                        files = os.listdir(materialsPath)
                        for file in files:
                            if os.path.isfile(os.path.join(materialsPath,file)):
                                filesPaths.append((os.path.join(materialsPath, file).replace('\\', '/'), file))
                        logging.debug("FOUND FILES IN DIR: "+str(files))
                    aggregatedInfo.append({"workshopName" : workshopName, "VM Name" : vm["name"], "ms-rdp" : rdpFilename, "rdesktop" : rdesktopFilename, "state" : vmInfo[1], "materials" : filesPaths})
            aggregateAvailableWorkshops()
            aggregatedInfoSem.release()
            time.sleep(probeTime)
        except Exception as e:
            logging.error("AGGREGATION: An error occured: " + str(e))
            traceback.print_exc()
            exit()
            time.sleep(probeTime)

def getAggregatedInfo():
    #aggregatedInfoSem.wait()
    return aggregatedInfo

def aggregateAvailableWorkshops():
    global availableWorkshops
    availableInfo = filter(lambda x: x["state"] == "Available", info) # get list of available workshops
    availableWorkshops = []
    while len(availableInfo) > 0:
        curr_workshop = availableInfo[0] # take first available workshop and get tmp list of all other workshops like it
        tmp = filter(lambda x: x["workshopName"] == curr_workshop["workshopName"], availableInfo) 
        q = Queue()
        for w in tmp: # put all like-workshops in a queue
            q.put(w)
        availableWorkshops.append({
            "workshopName": curr_workshop["workshopName"], 
            "materials": curr_workshop["materials"],
            "queue": q
            })
        availableInfo = filter(lambda x: x["workshopName"] != curr_workshop["workshopName"], availableInfo) # remove workshops put in queue

def getAvailableWorkshops():
    return availableWorkshops

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
