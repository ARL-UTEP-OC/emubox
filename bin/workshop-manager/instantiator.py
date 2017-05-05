# gevent imports
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()

import os

#to reduce stdout
import logging

#catch signal for quitting
import signal

#Flask imports
from flask import Flask
from flask import json
from flask import render_template
from flask import send_from_directory

#DataAggregation
import DataAggregation.webdata_aggregator

#VM State Manager
import VMStateManager.vbox_monitor

#######Webserver commands#########
app = Flask(__name__)
app.debug = True

@app.route('/WorkshopData/RDP/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    downloads = os.path.join(app.root_path, "WorkshopData/RDP/")
    return send_from_directory(directory=downloads, filename=filename)

# Simple catch-all server
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
#@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    return render_template('show_data.html', templateAvailable=DataAggregation.webdata_aggregator.getAggregatedInfo())

def signal_handler(signal, frame):
    try:
        logging.info("Killing webserver...")
        httpServer.stop()
        logging.info("Killing threads...")
        gevent.kill(srvGreenlet)
        gevent.kill(stateAssignmentThread)
        gevent.kill(restoreThread)

        VMStateManager.vbox_monitor.cleanup()

        exit()
    except Exception as e:
        logging.error("Error during cleanup"+str(e))
        exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig(level=logging.INFO)

    httpServer = WSGIServer(('0.0.0.0', 8080), app)
    stateAssignmentThread = gevent.spawn(VMStateManager.vbox_monitor.manageStates)
    restoreThread = gevent.spawn(VMStateManager.vbox_monitor.makeRestoreToAvailableState)
    srvGreenlet = gevent.spawn(httpServer.start)
    dataAggregator = gevent.spawn(DataAggregation.webdata_aggregator.aggregateRDP())

    try:
        #Let threads run until signal is caught
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread])
    except Exception as e:
        logging.error("An error occured in threads"+str(e))
        exit()
