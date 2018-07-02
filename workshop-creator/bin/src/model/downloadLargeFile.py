# this is based on downloadChunks from: https://gist.github.com/gourneau/1430932
import os
import urllib2
import math
import logging
from src.gui_constants import DOWNLOAD_LOCATION, DOWNLOAD_ERROR
from gi.repository import GLib


def downloadLargeFile(url, workshopName, dest, spinnerDialog):
    logging.debug("Large File Download starting")
    os.umask(0002)

    try:
        file = dest
        req = urllib2.urlopen(url)
        # contents = req.read()
        # total_size = int(req.info()['content-length'].strip())
        # print "total_size", total_size
        # downloaded = 0.0
        CHUNK = 256 * 10240
        with open(file, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                # downloaded += len(chunk)
                # print "Downloaded " + str(math.floor((downloaded / total_size) * 100)) + "%"
                # GLib.idle_add(spinnerDialog.setLabelVal,
                #               str(math.floor((downloaded / total_size) * 1000) / 10) + "% Downloaded")
                # GLib.idle_add(spinnerDialog.setProgressVal, downloaded / total_size)
                if not chunk:
                    break
                fp.write(chunk)
    except urllib2.HTTPError, e:
        if os.path.isfile(file):
            os.remove(file)
        spinnerDialog.destroy()
        print DOWNLOAD_ERROR
        return
    except urllib2.URLError, e:
        if os.path.isfile(file):
            os.remove(file)
        spinnerDialog.destroy()
        print DOWNLOAD_ERROR
        return

    spinnerDialog.destroy()
