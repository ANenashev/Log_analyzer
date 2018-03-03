# -*- coding: utf-8 -*-

import os
import gzip
import logging
import math
from operator import itemgetter
from datetime import datetime
import argparse
import sys
import re

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

    for name in os.listdir(config["REPORT_DIR"]):

        if name.startswith("report-"):
            date = datetime.strptime(name[7:17], "%Y.%m.%d")
            if date > last_report_date:
                last_report_date = date

    return last_report_date


def get_log_list(config):
    last_report_date = get_last_report_date(config)
    log_file_names = []
    log_dates = []

    datepat = re.compile(r'nginx-access-ui.log-(\d+)')

    for name in os.listdir(config["LOG_DIR"]):

        if datepat.match(name) is not None:
            date = datetime.strptime(datepat.match(name).group(1), "%Y%m%d")

            if date > last_report_date:
                log_file_names.append(name)
                log_dates.append(date)

    return log_file_names, log_dates


def get_log_line(log_path):
    if log_path.endswith(".gz"):
        log = gzip.open(log_path, 'rb')
    else:
        log = open(log_path, 'rb')

    for line in log:
        yield line

    log.close()


def count_stats(log_path, report_size):
    count = {}
    times = {}
    links = []
    count_processed = 0
    count_total = -1
    time_total = 0
    errors = 0

    for line in get_log_line(log_path):
        parsed_line = line.split()
        count_total += 1
        try:
            link = parsed_line[6].decode('utf-8')
            links.append(link)
            count[link] = count.get(link, 0) + 1
            current_time = float(parsed_line[-1])
            times[link] = times.get(link, list())
            times[link].append(current_time)

            count_processed += 1
            time_total += current_time

        except:
            logging.exception("String %d of %s didn't parsed" %
                              (count_total, log_path))
            errors += 1
            if errors > MAX_PARSING_ERRORS:
                logging.error("Too many parsing errors. Exiting parsing")
                return None

            continue



    unique_links = set(links)

    time_avg = dict.fromkeys(unique_links)
    time_med = dict.fromkeys(unique_links)
    time_max = dict.fromkeys(unique_links)
    count_perc = dict.fromkeys(unique_links)
    time_perc = dict.fromkeys(unique_links)
    time_sum = dict.fromkeys(unique_links)

    for link in unique_links:

        time_sum[link] = sum(times[link])
        time_avg[link] = time_sum[link] / count[link]

        times_len = len(times[link])
        sorted_times = sorted(times[link])

        if (times_len % 2) == 0:
            time_med[link] = sum(sorted_times[int((times_len / 2) - 1):int(times_len / 2)]) / 2.
        else:
            time_med[link] = sorted_times[int(math.floor(times_len / 2))]

        time_max[link] = max(times[link])
        time_perc[link] = time_sum[link] / time_total
        count_perc[link] = count[link] / count_processed

    slowest_links = [x[0] for x in sorted(time_sum.items(), key=itemgetter(1))[-report_size:]]

    table_json = []

    for link in slowest_links:
        table_json.append({"count": count[link],
                           "time_avg": time_avg[link],
                           "time_max": time_max[link],
                           "time_sum": time_sum[link],
                           "url": link,
                           "time_med": time_med[link],
                           "time_perc": time_perc[link],
                           "count_perc": count_perc[link]})

    return table_json


'''
def count_stats(log_path, report_size):
    links_stat = {}
    col_map = {"count":0,
               "time_avg":1,
               "time_max":2,
               "time_sum":3,
               "time_med":4,
               "time_perc":5,
               "count_perc":6,
               "times_list":7}
    default_link_stat = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    default_link_stat[col_map["times_list"]] = list()
    count_total = 0
    time_total = 0

    for line in get_log_line(log_path):
        parsed_line = line.split()

        try:
            link = parsed_line[6].decode('utf-8')
            cur_link_stat = links_stat.get(link, default_link_stat)
            cur_link_stat[col_map["count"]] += 1
            count_total += 1
            current_time = float(parsed_line[-1])
            time_total += current_time
            cur_link_stat[col_map["times_list"]].append(current_time)
            cur_link_stat[col_map["time_sum"]] += current_time
            # cur_link_stat["time_avg"] = cur_link_stat["time_sum"] / cur_link_stat["count"]
            if current_time > cur_link_stat[col_map["time_max"]]:
                cur_link_stat[col_map["time_max"]] = current_time
            # cur_link_stat["time_perc"] = cur_link_stat["time_sum"] / time_total
            # cur_link_stat["count_perc"] = cur_link_stat["count"] / count_total

            # times_len = len(cur_link_stat["times_list"])
            # sorted_times = sorted(cur_link_stat["times_list"])
            #
            # if (times_len % 2) == 0:
            #     cur_link_stat["time_med"] = sum(sorted_times[int((times_len / 2) - 1):int(times_len / 2)]) / 2.
            # else:
            #     cur_link_stat["time_med"] = sorted_times[int(math.floor(times_len / 2))]

            links_stat[link] = cur_link_stat

        except:
            logging.exception("String %d of %s didn't parsed" %
                              (count_total, log_path))
            continue

    for link, cur_link_stat in links_stat.items():
        cur_link_stat[col_map["time_avg"]] = cur_link_stat[col_map["time_sum"]] / cur_link_stat[col_map["count"]]
        cur_link_stat[col_map["time_perc"]] = cur_link_stat[col_map["time_sum"]] / time_total
        cur_link_stat[col_map["count_perc"]] = cur_link_stat[col_map["count"]] / count_total
        times_len = len(cur_link_stat[col_map["times_list"]])
        sorted_times = sorted(cur_link_stat[col_map["times_list"]])

        if (times_len % 2) == 0:
            cur_link_stat[col_map["time_med"]] = sum(sorted_times[int((times_len / 2) - 1):int(times_len / 2)]) / 2.
        else:
            cur_link_stat[col_map["time_med"]] = sorted_times[int(math.floor(times_len / 2))]

        links_stat[link] = cur_link_stat

    slowest_links = [x[0] for x in sorted(links_stat.items(), key=lambda k: k[1][col_map["time_avg"]])[-report_size:]]

    table_json = []

    for link in slowest_links:
        table_json.append({"count": links_stat[link][col_map["count"]],
                           "time_avg": links_stat[link][col_map["time_avg"]],
                           "time_max": links_stat[link][col_map["time_max"]],
                           "time_sum": links_stat[link][col_map["time_sum"]],
                           "url": link,
                           "time_med": links_stat[link][col_map["time_med"]],
                           "time_perc": links_stat[link][col_map["time_perc"]],
                           "count_perc": links_stat[link][col_map["count_perc"]]})

    return table_json
'''


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
    log_filenames, log_dates = get_log_list(config)

    if len(log_filenames) > 0:

        for i, log_to_parse in enumerate(log_filenames):
            logging.info("Parsing file %s" % log_to_parse)

            # create report json table
            report_table = count_stats(os.path.join(config["LOG_DIR"], log_to_parse), config["REPORT_SIZE"])

            if report_table is not None:
                # create report file
                report = open(os.path.join(TEMPLATES_DIR, 'report.html'), 'r')
                text = report.read()
                report.close()

                text = text.replace('$table_json', str(report_table))
                report_file = 'report-%s.html' % (log_dates[i].strftime('%Y.%m.%d'))

                with open(os.path.join(config['REPORT_DIR'], report_file), 'w') as out:
                    out.write(text)
                logging.info("File %s created successfully." % report_file)

                end_timestamp = datetime.now()

                with open(config["TS_PATH"], 'w') as ts:
                    ts.write(str(int(end_timestamp.timestamp())))
                    ts.mtime = int(end_timestamp.timestamp())
            else:
                logging.info("File %s was not processed." % log_to_parse)

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
