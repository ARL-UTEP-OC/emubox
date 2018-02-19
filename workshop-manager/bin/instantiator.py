import logging
import signal

import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer
from socketio.server import SocketIOServer

import DataAggregation.webdata_aggregator
import VMStateManager.vbox_monitor
import WebServer
from RequestHandler.client_updater import RequestHandlerApp
from WebServer.flask_server import app

gevent.monkey.patch_all()


def signal_handler(signal, frame):
    try:
        logging.info("Killing webserver...")
        httpServer.stop()
        logging.info("Killing threads...")
        gevent.kill(srvGreenlet)
        gevent.kill(ioGreenlet)
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
    sio_server = SocketIOServer(('0.0.0.0', 9090), RequestHandlerApp(), namespace="socket.io")
    stateAssignmentThread = gevent.spawn(VMStateManager.vbox_monitor.manageStates)
    restoreThread = gevent.spawn(VMStateManager.vbox_monitor.makeRestoreToAvailableState)
    srvGreenlet = gevent.spawn(httpServer.start)
    ioGreenlet = gevent.spawn(sio_server.serve_forever)
    dataAggregator = gevent.spawn(DataAggregation.webdata_aggregator.aggregateData)
    threadHandler = gevent.spawn(WebServer.flask_server.threadHandler)

    try:
        # Let threads run until signal is caught
        gevent.joinall([srvGreenlet, stateAssignmentThread, restoreThread, dataAggregator, threadHandler, ioGreenlet])
    except Exception as e:
        logging.error("An error occurred in threads" + str(e))
        exit()
