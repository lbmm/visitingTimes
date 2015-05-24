# -*- coding:utf-8 -*-

import argparse
import os
import sys
import csv
from collections import namedtuple

from datetime import datetime

import logging

FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


"""

Reads the entering and leaving time of customers from an input file. Find
the time range(s) when there were the maximum number of visitors in the
museum and how many of them there were.
As input takes a log file with time series entries of the following format.
   HH:MM,HH:MM
Output the time range(s) and number
of visitors found to standard output in the following format:
<start of time range>-<end of time range>;<number of visitors>.

To use
      $ python visitingTimes.py <path_of_your_file>

help
     $ python visitingTimes.py -h

      usage: visitingTimes.py [-h] FILE

      Count visitor in a museum.

      positional arguments:
      FILE        input file

      optional arguments:
      -h, --help  show this help message and exit
"""


class Visitor(object):

    """ Visitor class represents  a visitor  record. Each entry in the log corresponds to two visitor records.

    Attributes:
      time (str): time entry
      time_type (str): type of the time entry (could be a enter_time or a exit_time)

    """
    def __init__(self, time_str, time_type):

        self._time = datetime.strptime(time_str, '%H:%M').time()
        self.time_type = time_type

    def time(self):
        return self._time

def reader(file_name):

    """
    File reader and  parser.
    Performs the sanity checks for the record:
      1- len(record) == 2
      2- right formatting of each time record (HH:MM)
    In case record doesn't pass sanity checks, an error is logged while the parsing continue

    For each time entry yield a Visitor

    Args:
      param1: file to parser.

    Yield:
      Visitor: visitor with time entry and type.

    """

    with open(file_name, 'r') as f:
        # file can be treats as csv
        data = namedtuple('Data', ['in_time', 'out_time'])
        lines = csv.reader(f, delimiter=',')
        for row in lines:
            try:
                #sanity check: needs two entries per row
                if len(row) != 2:
                    raise ValueError
                data_recorded = data(*row)
                for key in data_recorded._fields:
                    yield (Visitor(getattr(data_recorded, key), key))
            except ValueError as e:
                #skipping data in wrong format
                log.error('entries not formatted correctly: %s ' % row)
                continue


def count_visitors(iterable):

    """
    Finds max_visitors, and corresponding interval.
    Sort all the times entries per type and time.
    Iterate over the sorted List and
    1- increase counter multipleVisitors if the type of the time_interval is a
        "enterTime" (in). Check if the maxVisitor is gt or eq to the maxVisitor counter.
         If gt : update maxVisitor with current multipleVisitors counter.
    2- decrease counter multipleVisitors if  the type of the time_interval is a
        "exitTime" (out)  and update the low bound timeInterval

    Args:
      iterable: iterable to analyze.

    return:
      dictionary: dictionary with information regarding max number of visitors and corresponding time interval .

    """

    #sort the list of visitor in time and type (of O(nlogn))
    count_visitors_list = sorted(list(iterable), key=lambda v: (v.time(), v.time_type))
    # counting the museum visitors
    visitors, max_visitors = 0, 0
    time_interval = {}
    new_time_interval = True
    for visitor_info in count_visitors_list:
        if visitor_info.time_type == 'in_time':
            visitors += 1
            if visitors >= max_visitors:
                if visitors > max_visitors:
                    max_visitors = visitors
                time_interval.update({'in': visitor_info.time()})
                new_time_interval = False
        elif visitor_info.time_type == 'out_time':
            visitors -= 1
            if not new_time_interval:
                time_interval.update({'out': visitor_info.time()})
            new_time_interval = True

    return {'in': time_interval['in'], 'out': time_interval['out'],
            'max_visitors': max_visitors}


def main():

    # define a command-line argument parser
    description = 'Count max visitors in a museum and select corresponding time period'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('file',
                        metavar='FILE',
                        help='input file')

    # parse arguments
    args = parser.parse_args()
    # sanity check arguments
    if not os.path.isfile(args.file):
        log.error('%s is not a file' % args.file)
        sys.exit(1)

    results = count_visitors(reader(args.file))
    #log result
    log.info(
        '%s - %s; %i' % (results['in'].strftime('%H:%M'), results['out'].strftime('%H:%M'), results['max_visitors']))


if __name__ == "__main__":
    main()

