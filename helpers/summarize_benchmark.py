''' 
    Given a start_time and end_time, walk a directory of collectd cvs and
    compute the avg, 95th, and stddv of the metrics.
'''
import argparse
import os
import time
import re
import csv
import tempfile
from numpy import percentile, std, average
from math import isnan, isinf
from collections import defaultdict

class CollectdCSVProcessor(object):
    ''' A class responsible for processing CSV files full of collectd style measurements.
        Tested on collectd 4.x only -- should probably work with other versions.
    '''
    def __init__(self, metric_name, csvfiles, start_time, end_time):
        '''
            Params:
                metric_name - The name of the metric being processed.
                csvfiles - A list containing the full paths to csvfiless to process. If more than one is specified the 
                           values are merged and averaged into one csvfiles before processing.
                start_time - The beginning of the window to accept measurements for in epoch time.
                end_time - The end of the window to accept measurements for in epoch time.
        '''
        self.metric_name = metric_name
        self.start_time = start_time
        self.end_time = end_time
        self.csvfiles = csvfiles
        self.report = defaultdict(dict)

    def _combine_measurements(self):
        ''' Measurements such as those generated from the cpu plugin are per core. 
            Combine measurements that happened at the same time and average them in order
            to produce one measurement for the time period.

            Assumes that the metrics being combined do not have submetrics.
        '''
        measurements = defaultdict(list)

        # Aggregate each of the measurements for a given time
        for csvf in self.csvfiles:
            with open(csvf, 'rb') as cf:
                for row in csv.DictReader(cf, delimiter=','):
                    value = float(row['value'])
                    # Skip nan and inf
                    if not (isnan(value) or isinf(value)):
                        measurements[row['epoch']].append(value)

        # Average the measurements and write them out to a new csv
        self.csvfiles = [tempfile.NamedTemporaryFile().name]

        with open(self.csvfiles[0], 'wb') as f:
            csvwriter = csv.writer(f, delimiter=',')

            # Write keys
            csvwriter.writerow(['epoch', 'value'])

            # Write averaged values
            for time, values in measurements.items():
                csvwriter.writerow([time, average(values)])

    def process_file(self):
        ''' Open the csvfile and organize all of the measurements to make it easy to
            do some math on them. Only include measurements that were taken within the
            start_time and end_time windows.

            Some metrics only have a value, ie: cpuidle only shows one value for the percentage
            of the cpu that was idle. Other metrics have 'submetrics' such as interface has tx and rw.

            Normalize all of these to look like the following:

                processed_metric[submetric] = [ (timestamp, measurement), (timestamp+n, measurement+N) ... ]
        '''
        # If more than one csvfile is specified then combined the measurements
        if len(self.csvfiles) > 1:
            self._combine_measurements()

        self.processed_metric = defaultdict(list)

        with open(self.csvfiles[0], 'rb') as csvf:
            for row in csv.DictReader(csvf, delimiter=','):
                # row['epoch'] is the epoch time the measurement was taken
                measurement_time = int(row['epoch'])

                # Only include measurements within the window
                if measurement_time >= self.start_time and measurement_time <= self.end_time:
                    for submetric, value in row.items():
                        if submetric != 'epoch':
                            measurement = float(value)

                            # Skip nan and infinity measurements
                            if not (isnan(measurement) or isinf(measurement)):
                                # Format and insert the measurement tuple as described above
                                measurement_tuple = (measurement_time, measurement)
                                self.processed_metric[submetric].append(measurement_tuple)

    def _calc(self, calc_name, calc_fn):
        ''' Given a calculation name and function, write the result for each
            submetric into the report.

            Params:
                calc_name - The name of the calculation. (ie: avg)
                calc_fn - A function to pass a list of measurements to which 
                          returns the calculation result.
        '''
        for submetric, measurements in self.processed_metric.items():
            values = [ m[1] for m in measurements ]
            submetric_calc = calc_fn(values)
            self.report[submetric][calc_name] = submetric_calc

    def calc_avg(self):
        ''' Calc the average of all submetrics '''
        self._calc('avg', average)
        
    def calc_max(self):
        ''' Calc the max of all submetrics '''
        self._calc('max', max)

    def calc_min(self):
        ''' Calc the min of all submetrics '''
        self._calc('min', min)

    def calc_std(self):
        ''' Calc the standard deviation of all submetrics '''
        self._calc('stddev', std)

    def calc_95(self):
        ''' Calc the 95th percentile of all submetrics '''
        def p95_fn(values):
            return percentile(values, 95)

        self._calc('95th', p95_fn)

    def calculate_all(self):
        ''' Run all of the calculation functions '''
        self.calc_avg()
        self.calc_max()
        self.calc_min()
        self.calc_95()
        self.calc_std()

    def print_report(self):
        ''' Print a semi-formatted report to stdout '''
        for submetric, calc_items in self.report.items():
            # value means there were no submetrics, format the report accordingly
            if submetric != 'value':
                print 'Metric:\t%s-%s' % (self.metric_name, submetric)
            else:
                print 'Metric:\t%s' % self.metric_name

            for calc, result in calc_items.items():
                print "%s\t" % calc,
                print "%d" % result

if __name__ == '__main__':
    #
    # Settings
    #
    parser = argparse.ArgumentParser(description='Run the collectd summarization')
    parser.add_argument("--start-time", required=True, type=int)
    parser.add_argument("--end-time", required=True, type=int)
    parser.add_argument("--path-to-csvs", required=True)
    args = parser.parse_args()

    # Path to the csvs to be processed
    PATH_TO_COLLECTD_CSVS = args.path_to_csvs

    # Timeframe to process in epoch, assumes the benchmark and summarization 
    # started on the same day.
    START_TIME = args.start_time
    END_TIME = args.end_time
    START_DAY = time.strftime('%Y-%m-%d', time.gmtime(START_TIME))

    # The pattern to match on to group all of the measurements into specific hosts.
    # Only includes collectd files from the same day as START_DAY
    #
    # paths look like: 
    #   /dirname/csv/ip-10-196-51-15.ec2.internal/memory/memory-used-2013-06-11
    #
    COLLECTD_FILE_REGEX = re.compile(r".+/csv/(.+)/(.+)/(.+)-%s$" % START_DAY)

    # Metrics that we want to report on
    METRICS_TO_REPORT = [ 'cpu-idle', 'cpu-steal',
                          'load',
                          'disk_ops', 
                          'if_octets-eth0', 'if_errors-eth0',
                          'memory-free'
                         ]

    #
    # Walk the csv structure extracting the hostnames, and filenames that we're
    # going to process.
    #
    metrics_to_process = defaultdict(dict)
    for dirname, dirnames, filenames in os.walk(PATH_TO_COLLECTD_CSVS):
        for filename in filenames:
            # Absolute path to the file to be processed
            fullpath = os.path.join(dirname, filename)

            # Match only files from START_DAY
            m = re.match(COLLECTD_FILE_REGEX, fullpath)
            if m:
                # Add the filename to be processed for the host if its a metric
                # we want to generate a report for.
                host = m.group(1)
                metric_name = m.group(3)


                # Only include metrics that we care about.
                if metric_name in METRICS_TO_REPORT:

                    # disk metric names should be tied to each disk individually
                    if 'disk' in m.group(2):
                        metric_key = '%s-%s' % (m.group(2), metric_name)
                    else:
                        metric_key = metric_name

                    # Metrics such as cpu come in as each core individually in a separate csv file
                    # append the metrics to a list of files to combine when doing post-processing
                    # of the collectd metrics.
                    if metric_key in metrics_to_process[host]:
                        metrics_to_process[host][metric_key].append(fullpath)
                    else:
                        metrics_to_process[host][metric_key] = [fullpath]

    #
    # Calculate metrics for the timeframe for each of the hosts.
    #
    calculations_order = ['avg', '95th', 'stddev', 'min', 'max']

    resultsdir = '/tmp/results'
    if not os.path.exists(resultsdir):
        os.makedirs(resultsdir)

    for host_name, metric_files in metrics_to_process.items():
        for metric_name, file_list in metric_files.items():
            # Process and calc data for each metric
            csp = CollectdCSVProcessor(metric_name=metric_name, csvfiles=file_list, 
                                       start_time=START_TIME, end_time=END_TIME)
            csp.process_file()
            csp.calculate_all()

            # Write the results in a graph friendly format
            for submetric, calc_items in csp.report.items():
                if submetric == 'value':
                    results_filename = '%s/%s.csv' % (resultsdir, metric_name)
                else:
                    results_filename = '%s/%s-%s.csv' % (resultsdir, metric_name, submetric)

                # Write the labels for the csv
                if not os.path.exists(results_filename):
                    with open(results_filename, 'w') as f:
                        f.write( 'hostname,%s\n' % ','.join(calculations_order) )

                # Write the results
                c_results = [host_name]
                for calc_name in calculations_order:
                    c_results.append(str(calc_items[calc_name]))

                with open(results_filename, 'a') as f:
                    f.write( '%s\n' % ','.join(c_results) )
