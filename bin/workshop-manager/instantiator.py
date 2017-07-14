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
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
from flask import render_template
from flask import send_from_directory
#DataAggregation
import DataAggregation.webdata_aggregator

#VM State Manager
import VMStateManager.vbox_monitor

#######Webserver commands#########
app = Flask(__name__)
app.debug = True

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
    return render_template('index.html', templateAvailable=DataAggregation.webdata_aggregator.aggregateAvailableWorkshops())

# Catch rdp requests
@app.route('/ms-rdp/<workshopName>')
def giveRDP(workshopName):
    availableWorkshops = DataAggregation.webdata_aggregator.getAvailableWorkshops()
    return filter(lambda x: x["workshopName"] == workshopName, availableWorkshops)[0]["queue"].get()["ms-rdp"]

# Catch rdesktop requests
@app.route('/rdesktop/<workshopName>')
def giverdesktop(workshopName):
    availableWorkshops = DataAggregation.webdata_aggregator.getAvailableWorkshops()
    return filter(lambda x: x["workshopName"] == workshopName, availableWorkshops)[0]["queue"].get()["rdesktop"]

# Catch AJAX request
@app.route('/generateTable')
def giveWorkshopData():
    return render_template('generate_table.html', templateAvailable=DataAggregation.agg_test.getAvailableWorkshops())


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
    logging.basicConfig(level=logging.DEBUG)

    httpServer = WSGIServer(('0.0.0.0', 8080), app)
    stateAssignmentThread = gevent.spawn(VMStateManager.vbox_monitor.manageStates)
    restoreThread = gevent.spawn(VMStateManager.vbox_monitor.makeRestoreToAvailableState)
    srvGreenlet = gevent.spawn(httpServer.start)
    dataAggregator = gevent.spawn(DataAggregation.webdata_aggregator.aggregateData())

    try:
        #Let threads run until signal is caught
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread])
    except Exception as e:
        logging.error("An error occured in threads"+str(e))
        exit()
