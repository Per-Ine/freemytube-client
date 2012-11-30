#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""FreeMyTube

Push your YouTube bandwidth stats to freemytube.fr
"""

import sys
import time
import math
import argparse
import quvi
import requests


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

    def eval(self):
        """Download YouTube video and evaluate the average bandwidth
        """
        r = requests.get(self.mediaurl, prefetch=False)
        self.size = int(r.headers['Content-Length'].strip())

        self.bytes = 0
        self.measurements = []

        self.start_time = time.time()
        last_update = 0
        for buf in r.iter_content(1024):
            if buf:
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

                self.measurements.append(scaled)
                ratio = int((float(self.bytes) / float(self.size)) * 100.)

                print ":: %6.2f kbits/s :: %3d%% :: %s (%s)\r" % (
                    scaled, ratio, self.pagetitle, self.mediacontenttype),

                sys.stdout.flush()

        self.average_bandwidth = sum(self.measurements) / len(self.measurements)

        print "\nAverage bandwidth: %6.2f kbits/s" % self.average_bandwidth

    def push(self):
        """Push collected data to the freemytube server
        """
        pass


def main(argv=None):

    # CLI
    parser = argparse.ArgumentParser(
        description='Evaluate your YouTube bandwidth')
    args = parser.parse_args()

    fmt = FreeMyTube()
    fmt.eval()

    return 1

if __name__ == "__main__":
    sys.exit(main())
