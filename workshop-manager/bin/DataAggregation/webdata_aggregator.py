import time
import traceback
import VMStateManager.vbox_monitor
from vboxapi import VirtualBoxManager
import os

# gevent imports
import gevent
import gevent.monkey
from gevent.lock import BoundedSemaphore
gevent.monkey.patch_all()

#to reduce stdout
import logging

from Workshop_Queue import Workshop_Queue
from Workshop_Unit import Workshop_Unit

mgr = VirtualBoxManager(None, None)

probeTime = 5
aggregatedInfo = []
availableWorkshops = []
unitsOnHold = []
checkoutTime = 30

# vars needed for gevent (lock)
aggregatedInfoSem = BoundedSemaphore(1)


def cleanup():
    logging.info("Cleaning up webdata aggregator...")
    try:

        logging.info("Clean up complete. Exiting...")
    except Exception as e:
        logging.error("Error during cleanup"+str(e))

def unitIsAvailable(vms):
    for vm in vms:
        if (vm not in VMStateManager.vbox_monitor.availableState and VMStateManager.vbox_monitor.vms[vm]["vrde"]) \
                or (VMStateManager.vbox_monitor.vms[vm]["VMState"] != mgr.constants.MachineState_Running):
            return False
    return True

def getAvailableUnits():
    availableUnits = []
    getGroupToVms = VMStateManager.vbox_monitor.getGroupToVms().copy()
    while(getGroupToVms):
        unit = getGroupToVms.popitem()
        if unitIsAvailable(unit[1]):
            workshopName = unit[0].split('/')[1]
            rdp_files = getRDPPath(unit, workshopName)
            rdesktop_files = getRDesktopPath(unit, workshopName)
            if len(rdp_files) and (len(rdp_files) == len(rdesktop_files)):
                availableUnits.append(Workshop_Unit(workshopName, unit[1], rdp_files, rdesktop_files))
    return availableUnits


def aggregateData():
    """ Communicates with VBox Manager to gather and consolidate virtual machine information into Workshop Units """
    global aggregatedInfo
    global availableWorkshops

    while True:
        try:
            # should scan file system and then aggregate any information at the unit level
            availableUnits = getAvailableUnits()
            aggregatedInfoSem.wait()
            aggregatedInfoSem.acquire()
            for unit in availableUnits:
                workshopName = unit.workshopName
                workshopExists = False
                for workshop in availableWorkshops:
                    if workshopName == workshop.workshopName:
                        workshopExists = True
                        break
                if not workshopExists:
                    filesPaths = []
                    materialsPath = os.path.join("WorkshopData", workshopName, "Materials")
                    if os.path.isdir(materialsPath):
                        files = os.listdir(materialsPath)
                        for file in files:
                            if os.path.isfile(os.path.join(materialsPath, file)):
                                filesPaths.append((os.path.join(materialsPath, file).replace('\\', '/'), file))
                    curr_workshop_queue = Workshop_Queue(workshopName, filesPaths)
                    curr_workshop_queue.q.put(unit)
                    availableWorkshops.append(curr_workshop_queue)
                elif workshopExists:
                    workshop_queue = filter(lambda x: x.workshopName == workshopName, availableWorkshops)[0]
                    if unit not in workshop_queue.q.queue and unit not in unitsOnHold:
                        workshop_queue.q.put(unit)
            time.sleep(probeTime)
            for workshop in availableWorkshops:
                workshop.q.queue.clear()
            aggregatedInfoSem.release()
        except Exception as e:
            logging.error("AGGREGATION: An error occurred: " + str(e))
            traceback.print_exc()
            exit()
            time.sleep(probeTime)


def getAggregatedInfo():
    """ Returns: List of Workshop Units that are aggregated from the VBox Monitor. """
    #aggregatedInfoSem.wait()
    return aggregatedInfo


def getAvailableWorkshops():
    """ Returns: List of Workshop objects whose queues contain Workshop Units that are "Available". """
    return availableWorkshops

def checkoutUnit(unit):
    #unitsOnHold.append(unit)
    time.sleep(checkoutTime)
    unitsOnHold.remove(unit)

def putOnHold(unit):
    unitsOnHold.append(unit)

def getRDPPath(unit, workshopName):
    rdpPaths = []
    for vm in unit[1]:
        if VMStateManager.vbox_monitor.vms[vm]["vrde"]:
            rdpPath = os.path.join("WorkshopData", workshopName, "RDP",
                               VMStateManager.vbox_monitor.vms[vm]["name"] + "_" +
                                       VMStateManager.vbox_monitor.vms[vm]["vrdeproperty[TCP/Ports]"] +
                                       ".rdp").replace('\\', '/')
            rdpPaths.append(rdpPath)
    return rdpPaths

def getRDesktopPath(unit, workshopName):
    rdesktopPaths = []
    for vm in unit[1]:
        if VMStateManager.vbox_monitor.vms[vm]["vrde"]:
            rdesktopPath = os.path.join("WorkshopData", workshopName, "RDP",
                                   VMStateManager.vbox_monitor.vms[vm]["name"] + "_" +
                                   VMStateManager.vbox_monitor.vms[vm]["vrdeproperty[TCP/Ports]"] +
                                   ".sh").replace('\\', '/')
            rdesktopPaths.append(rdesktopPath)
    return rdesktopPaths

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
