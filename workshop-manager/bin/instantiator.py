# gevent imports
import gevent
import gevent.monkey
import threading
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()

import os
import time

# to reduce stdout
import logging

# catch signal for quitting
import signal

# Flask imports
from flask import Flask
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
from flask import render_template
from flask import send_from_directory
from flask import jsonify

from gevent.lock import BoundedSemaphore

# DataAggregation
import DataAggregation.webdata_aggregator

# VM State Manager
import VMStateManager.vbox_monitor

import zipfile

# Webserver commands
app = Flask(__name__)
app.debug = True

threadsToRun = []
threadsToRunSem = threading.Semaphore(1)
threadTime = 2
threadHandlerSem = threading.Semaphore(1)

zipSem = BoundedSemaphore(1)
zipClearTime = 15
i = 0


def clearZip(zip_file_name):
    time.sleep(zipClearTime)
    os.remove(zip_file_name)


def threadHandler():
    while True:
        threadHandlerSem.acquire()
        if len(threadsToRun):
            for thread in threadsToRun:
                t = thread
                threadsToRun.remove(thread)
                t.start()
        threadHandlerSem.release()
        time.sleep(threadTime)

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        #response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'public, no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return update_wrapper(no_cache, view)

@app.route('/WorkshopData/<path:filename>', methods=['GET', 'POST'])
@nocache
def download(filename):
    downloads = os.path.join(app.root_path, "WorkshopData/")
    return send_from_directory(directory=downloads, as_attachment=True, filename=filename, mimetype='application/octet-stream')

# Simple catch-all server
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@nocache
def catch_all(path):
    """ Handles all requests to the main index page of the Web Server. """
    return render_template('index.html', workshops=DataAggregation.webdata_aggregator.getAvailableWorkshops())

@app.route('/checkout/ms-rdp/<workshopName>')
def checkoutRDP(workshopName):
    global i
    workshop = filter(lambda x: x.workshopName == workshopName, DataAggregation.webdata_aggregator.getAvailableWorkshops())[0]
    if workshop.q.qsize():
        unit = workshop.q.get()
        threadsToRunSem.acquire()
        threadsToRun.append(threading.Thread(target=DataAggregation.webdata_aggregator.checkoutUnit, args=(unit,)))
        threadsToRunSem.release()
        rdpPaths = unit.rdp_files

        if len(rdpPaths) is 1:
            return render_template('download.html', download_path=rdpPaths[0])

        zipSem.acquire()
        zip_file_name = "Workshop" + str(i) + ".zip"
        zip_file_path = os.path.join("WorkshopData", workshopName, zip_file_name)
        i += 1
        zip_files(rdpPaths, zip_file_path)
        threadsToRun.append(threading.Thread(target=clearZip, args=(zip_file_path,)))
        zipSem.release()
        return render_template('download.html', download_path=zip_file_path)
    else:
        return "Sorry, there are no workshops available."


@app.route('/checkout/rdesktop/<workshopName>')
def checkoutrdesktop(workshopName):
    global i
    workshop = filter(lambda x: x.workshopName == workshopName, DataAggregation.webdata_aggregator.getAvailableWorkshops())[0]
    if workshop.q.qsize():
        unit = workshop.q.get()
        threadsToRunSem.acquire()
        threadsToRun.append(threading.Thread(target=DataAggregation.webdata_aggregator.checkoutUnit, args=(unit,)))
        threadsToRunSem.release()
        rdesktopPaths = unit.rdesktop_files

        if len(rdesktopPaths) is 1:
            return render_template('download.html', download_path=rdesktopPaths[0])

        zipSem.acquire()
        zip_file_name = unit.workshopName + "_" + str(i) + ".zip"
        zip_file_path = os.path.join("WorkshopData", workshopName, zip_file_name)
        i += 1
        zip_files(rdesktopPaths, zip_file_path)
        threadsToRun.append(threading.Thread(target=clearZip, args=(zip_file_path,)))
        zipSem.release()
        return render_template('download.html', download_path=zip_file_path)
    else:
        return "Sorry, there are no workshops available."

@app.route('/getQueueSize/<workshopName>')
def giveQueueSize(workshopName):
    """ Catch AJAX Requests for Queue Size. """
    availableWorkshops = DataAggregation.webdata_aggregator.getAvailableWorkshops()
    if (availableWorkshops):
        return jsonify(filter(lambda x: x.workshopName == workshopName, availableWorkshops)[0].q.qsize())
    else:
        return jsonify("0")

''' 
    zip_files:
        @src: Iterable object containing one or more element
        @dst: filename (path/filename if needed)
        @arcname: Iterable object containing the names we want to give to the elements in the archive (has to correspond to src) 
'''
def zip_files(src, dst, arcname=None):
    zip_ = zipfile.ZipFile(dst, 'w')
    for i in range(len(src)):
        if arcname is None:
            zip_.write(src[i], os.path.basename(src[i]), compress_type = zipfile.ZIP_DEFLATED)
        else:
            zip_.write(src[i], arcname[i], compress_type = zipfile.ZIP_DEFLATED)
    zip_.close()


def signal_handler(signal, frame):
    try:
        logging.info("Killing webserver...")
        httpServer.stop()
        logging.info("Killing threads...")
        gevent.kill(srvGreenlet)
        gevent.kill(stateAssignmentThread)
        gevent.kill(restoreThread)
        gevent.kill(threadHandler)
        VMStateManager.vbox_monitor.cleanup()

        exit()
    except Exception as e:
        logging.error("Error during cleanup"+str(e))
        exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig(level=logging.DEBUG)

    httpServer = WSGIServer(('0.0.0.0', 8080), app)
    stateAssignmentThread = gevent.spawn(VMStateManager.vbox_monitor.manageStates)
    restoreThread = gevent.spawn(VMStateManager.vbox_monitor.makeRestoreToAvailableState)
    srvGreenlet = gevent.spawn(httpServer.start)
    dataAggregator = gevent.spawn(DataAggregation.webdata_aggregator.aggregateData)
    threadHandler = gevent.spawn(threadHandler)

    try:
        # Let threads run until signal is caught
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread, dataAggregator, threadHandler])
    except Exception as e:
        logging.error("An error occurred in threads" + str(e))
        exit()
