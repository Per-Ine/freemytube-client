#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""FreeMyTube Client

Usage: freemytube.py [-Fhv]

Options:
    -F              Fake mode (randomly generates data).
    -h --help       Show this screen.
    -v --version    Show version.
"""

import sys
import time
import math
import random

import quvi
import requests
from docopt import docopt

__title__ = 'freemytube-client'
__version__ = '0.1.1'
__author__ = 'Julien Maupetit'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013 Julien Maupetit'


# Default config
DEFAULT_URL = 'http://www.youtube.com/watch?v=h7o_gyujJRc'


class FreeMyTube(object):
    """FreeMyTube Client
    """
    def __init__(self, url=None):
        """
        """
        self.url = url
        if not url:
            self.url = DEFAULT_URL
        self._setup()

    def _setup(self):
        """Get YouTube video relevant informations via the Quvi library
        """
        q = quvi.Quvi()
        q.parse(self.url)
        #q.set_format('fmt05_240p')

        self.mediaobj = q
        self.mediaurl = q.get_properties()['mediaurl']
        self.pagetitle = q.get_properties()['pagetitle']
        self.mediacontenttype = q.get_properties()['mediacontenttype']

    def eval(self, dry_run=False):
        """Download YouTube video and evaluate the average bandwidth
        """
        r = requests.get(self.mediaurl, stream=True)
        self.size = int(r.headers['Content-Length'].strip())

        self.bytes = 0
        measurements = []

        self.start_time = time.time()
        last_update = 0

        if dry_run:
            measurements = [random.random() * 1000 for i in xrange(100)]
            self.elapsed_time = random.random() * 100
        else:
            for buf in r.iter_content(1024):
                if not buf:
                    break

                self.bytes += len(buf)
                cur_time = time.time()
                self.elapsed_time = cur_time - self.start_time

                if not self.elapsed_time:
                    continue

                if (cur_time - last_update) < 5:
                    continue
                last_update = cur_time

                speed = self.bytes / self.elapsed_time
                power = int(math.log(speed, 1000))
                scaled = speed / 1000. ** power

                measurements.append(scaled)
                ratio = int((float(self.bytes) / float(self.size)) * 100.)

                print ":: %6.2f kbits/s :: %3d%% :: %s (%s)\r" % (
                    scaled, ratio, self.pagetitle, self.mediacontenttype),

                sys.stdout.flush()

        self.average_bandwidth = sum(measurements) / len(measurements)
        self.measurements = measurements

        print "\nAverage bandwidth: %6.2f kbits/s" % self.average_bandwidth

    def push(self):
        """Push collected data to the freemytube server
        """
        pass


def main(argv=None):

    # CLI
    # Parse command line arguments
    arguments = docopt(
        __doc__,
        version='FreeMyTube Client %s' % __version__)

    fmt = FreeMyTube()
    fmt.eval(dry_run=arguments.get('-F'))

    return 1

if __name__ == "__main__":
    sys.exit(main())
