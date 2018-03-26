# -*- coding: utf-8 -*-

import os
import gzip
import logging
import math
from datetime import datetime
import argparse
import sys
import re
import collections

# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

TEMPLATES_DIR = "./templates"
MAX_PARSING_ERRORS = 200


def parse_config(conf_content, default_config):
    config = default_config
    for line in conf_content:
        key, value = line.split(":")
        if key == "REPORT_SIZE":
            config[key] = int(value)
        else:
            config[key] = value.replace('\"', '').strip()
    return config


def get_last_report_date(config):
    last_report_date = datetime(2000, 1, 1, 0, 0, 0)

    datepat = re.compile(r'report-(\d\d\d\d.\d\d.\d\d)')

    for name in os.listdir(config["REPORT_DIR"]):

        if datepat.match(name) is not None:
            date = datetime.strptime(datepat.match(name).group(1), "%Y.%m.%d")
            if date > last_report_date:
                last_report_date = date

    return last_report_date


def get_last_log(config):
    last_report_date = get_last_report_date(config)
    log_file_name = None
    log_date = None

    datepat = re.compile(r'nginx-access-ui.log-(\d+)')

    for name in os.listdir(config["LOG_DIR"]):

        if datepat.match(name) is not None:
            date = datetime.strptime(datepat.match(name).group(1), "%Y%m%d")

            if date > last_report_date:
                log_file_name = name
                log_date = date

    return log_file_name, log_date


def get_log_line(log_path):
    if log_path.endswith(".gz"):
        log = gzip.open(log_path, 'rb')
    else:
        log = open(log_path, 'rb')

    for line in log:
        yield line

    log.close()


def count_stats(log_path):
    url2times = collections.defaultdict(list)

    total_count = total_time = errors = 0

    for line in get_log_line(log_path):
        parsed_line = line.split()

        try:
            url2times[parsed_line[6].decode('utf-8')].append(float(parsed_line[-1]))
        except:
            logging.exception("String %d of %s didn't parsed" %
                              (total_count, log_path))
            errors += 1
            if errors > MAX_PARSING_ERRORS:
                logging.error("Too many parsing errors. Exiting parsing")
                return None

            continue

    for v in url2times.values():
        total_count += len(v)
        total_time += sum(v)

    stat = []

    for url, times_list in url2times.items():
        times_list.sort()
        stat.append({
            'url': url,
            'count': len(times_list),
            'count_perc': round(100 * len(times_list) / float(total_count), 3),
            'time_avg': round(sum(times_list) / len(times_list), 3),
            'time_max': round(max(times_list), 3),
            'time_sum': round(sum(times_list), 3),
            'time_perc': round(100 * sum(times_list) / total_time, 3),
            'time_med': median(times_list)
        })

    return stat


def create_json(stat, report_size):

    stat.sort(key=lambda x: x['time_sum'])

    slowest_links = stat[-report_size:]

    table_json = []

    for v in slowest_links:
        table_json.append({"count": v['count'],
                           "time_avg": v['time_avg'],
                           "time_max": v['time_max'],
                           "time_sum": v['time_sum'],
                           "url": v['url'],
                           "time_med": v['time_med'],
                           "time_perc": v['time_perc'],
                           "count_perc": v['count_perc']})

    return table_json


def median(sorted_list):

    list_len = len(sorted_list)
    if (list_len % 2) == 0:
        return sum(sorted_list[int((list_len / 2) - 1):int(list_len / 2)]) / 2.
    else:
        return sorted_list[int(math.floor(list_len / 2))]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str)

    config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./reports",
            "LOG_DIR": "./log",
            "LOG_PATH": "./log_analyzer.log",
            "TS_PATH": "./log_analyzer.ts"
        }

    try:
        args = parser.parse_args()

        if args.config is not None:
            if os.path.isfile(args.config):
                with open(args.config, 'r') as conf_file:
                    content = conf_file.readlines()
                    config = parse_config(content, config)
    except:
        pass

    return config


def main(config):
    log_filename, log_date = get_last_log(config)

    if log_filename is not None:

        logging.info("Parsing file %s" % log_filename)

        # create report json table
        stat = count_stats(os.path.join(config["LOG_DIR"], log_filename))

        report_table = create_json(stat, config["REPORT_SIZE"])

        if report_table is not None:
            # create report file
            with open(os.path.join(TEMPLATES_DIR, 'report.html'), 'r') as report:
                text = report.read()

            text = text.replace('$table_json', str(report_table))
            report_file = 'report-%s.html' % (log_date.strftime('%Y.%m.%d'))

            with open(os.path.join(config['REPORT_DIR'], report_file), 'w') as out:
                out.write(text)
            logging.info("File %s created successfully." % report_file)

            end_timestamp = datetime.now()

            with open(config["TS_PATH"], 'w') as ts:
                ts.write(str(int(end_timestamp.timestamp())))
                ts.mtime = int(end_timestamp.timestamp())
        else:
            logging.info("File %s was not processed." % log_filename)

    else:

        logging.info("No log files to parse")


if __name__ == "__main__":

    config = parse_args()

    # check path to log file, configure logger
    if (config.get('LOG_PATH', None) is not None) and (os.path.isfile(config['LOG_PATH'])):
        logging.basicConfig(
            format="[%(asctime)s] %(levelname).1s %(message)s",
            datefmt='%Y.%m.%d %H:%M:%S',
            level=logging.INFO,
            filename=config["LOG_PATH"])
    else:
        logging.basicConfig(
            format="[%(asctime)s] %(levelname).1s %(message)s",
            datefmt='%Y.%m.%d %H:%M:%S',
            level=logging.INFO,
            handlers=[logging.StreamHandler(sys.stdout)])

    try:
        main(config)
    except Exception as e:
        logging.exception(str(e))
