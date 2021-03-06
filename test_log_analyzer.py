# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from datetime import datetime
from log_analyzer import parse_config, get_last_report_date, get_last_log, count_stats


class FunctionsTest(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./reports",
            "LOG_DIR": "./log",
            "TS_PATH": "./log_nalyzer.ts"
        }
    
    def test_parse_config(self):

        # Empty config
        content = []
        self.assertEqual(parse_config(content, self.config), self.config)

        # Override and add values
        content = ['REPORT_SIZE: 100\n', 
                   'REPORT_DIR: "./reports"\n',
                   'LOG_DIR: "./log"',
                   'LOG_PATH: "./new_folder/log_analyzer.log"',
                   'TS_PATH: "./log_nalyzer.ts"']

        result = {
            "REPORT_SIZE": 100,
            "REPORT_DIR": "./reports",
            "LOG_DIR": "./log",
            "LOG_PATH": "./new_folder/log_analyzer.log",
            "TS_PATH": "./log_nalyzer.ts"
        }
        self.assertEqual(parse_config(content, self.config), result)

    def test_get_last_report_date(self):
        with patch('os.listdir') as mocked_listdir:
            mocked_listdir.return_value = ['report-2017.06.30.html',
                                           'report-2017.07.01.html']
            self.assertEqual(get_last_report_date(self.config), datetime(2017, 7, 1, 0, 0, 0))
            
    def test_get_last_log(self):
        with patch('log_analyzer.get_last_report_date') as mocked_report_date:
            with patch('os.listdir') as mocked_listdir:
                mocked_report_date.return_value = datetime(2000, 1, 1, 0, 0, 0)
                mocked_listdir.return_value = ['other_log.log-20170630.gz',
                                               'nginx-access-ui.log-20170701.gz',
                                               'nginx-access-ui.log-20170702',
                                               'file.txt']
                log_file_name, log_date = get_last_log(self.config)
                self.assertEqual(log_file_name, 'nginx-access-ui.log-20170702')
                self.assertEqual(log_date, datetime(2017, 7, 2, 0, 0, 0))
                
    def test_count_stats(self):
        result = [{'url': '/api/v2/banner/25019354', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.39, 'time_max': 0.39, 'time_sum': 0.39, 'time_perc': 6.04, 'time_med': 0.39},
         {'url': '/api/1/photogenic_banners/list/?server_name=WIN7RB4', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.133, 'time_max': 0.133, 'time_sum': 0.133, 'time_perc': 2.06, 'time_med': 0.133},
         {'url': '/api/v2/banner/16852664', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.199, 'time_max': 0.199, 'time_sum': 0.199, 'time_perc': 3.082, 'time_med': 0.199},
         {'url': '/api/v2/slot/4705/groups', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.704, 'time_max': 0.704, 'time_sum': 0.704, 'time_perc': 10.903, 'time_med': 0.704},
         {'url': '/api/v2/internal/banner/24294027/info', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.146, 'time_max': 0.146, 'time_sum': 0.146, 'time_perc': 2.261, 'time_med': 0.146},
         {'url': '/api/v2/group/1769230/banners', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.628, 'time_max': 0.628, 'time_sum': 0.628, 'time_perc': 9.726, 'time_med': 0.628},
         {'url': '/api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.067, 'time_max': 0.067, 'time_sum': 0.067, 'time_perc': 1.038, 'time_med': 0.067},
         {'url': '/api/v2/banner/1717161', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.138, 'time_max': 0.138, 'time_sum': 0.138, 'time_perc': 2.137, 'time_med': 0.138},
         {'url': '/export/appinstall_raw/2017-06-29/', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.003, 'time_max': 0.003, 'time_sum': 0.003, 'time_perc': 0.046, 'time_med': 0.003},
         {'url': '/api/v2/slot/4822/groups', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.157, 'time_max': 0.157, 'time_sum': 0.157, 'time_perc': 2.431, 'time_med': 0.157},
         {'url': '/api/v2/banner/24987703', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.726, 'time_max': 0.726, 'time_sum': 0.726, 'time_perc': 11.244, 'time_med': 0.726},
         {'url': '/export/appinstall_raw/2017-06-30/', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.001, 'time_max': 0.001, 'time_sum': 0.001, 'time_perc': 0.015, 'time_med': 0.001},
         {'url': '/api/v2/banner/25020545', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.738, 'time_max': 0.738, 'time_sum': 0.738, 'time_perc': 11.429, 'time_med': 0.738},
         {'url': '/api/v2/banner/7763463', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.181, 'time_max': 0.181, 'time_sum': 0.181, 'time_perc': 2.803, 'time_med': 0.181},
         {'url': '/api/v2/banner/16168711', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.19, 'time_max': 0.19, 'time_sum': 0.19, 'time_perc': 2.943, 'time_med': 0.19},
         {'url': '/api/v2/banner/25023278', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.841, 'time_max': 0.841, 'time_sum': 0.841, 'time_perc': 13.025, 'time_med': 0.841},
         {'url': '/api/v2/group/7786682/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.068, 'time_max': 0.068, 'time_sum': 0.068, 'time_perc': 1.053, 'time_med': 0.068},
         {'url': '/api/v2/banner/25013431', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.917, 'time_max': 0.917, 'time_sum': 0.917, 'time_perc': 14.202, 'time_med': 0.917},
         {'url': '/api/v2/internal/banner/24288647/info', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.072, 'time_max': 0.072, 'time_sum': 0.072, 'time_perc': 1.115, 'time_med': 0.072},
         {'url': '/api/v2/banner/21456892', 'count': 1, 'count_perc': 5.0, 'time_avg': 0.158, 'time_max': 0.158, 'time_sum': 0.158, 'time_perc': 2.447, 'time_med': 0.158}]
        
        with patch('log_analyzer.get_log_line') as mocked_get_log_line:
            mocked_get_log_line.return_value = [b'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752759" "dc7161be3" 0.390\n',
                                   b'1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1" 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n',
                                   b'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752745" "2a828197ae235b0b3cb" 0.704\n',
                                   b'1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628\n',
                                   b'1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138\n',
                                   b'1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003\n',
                                   b'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157\n',
                                   b'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/24987703 HTTP/1.1" 200 883 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752753" "dc7161be3" 0.726\n',
                                   b'1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-30/ HTTP/1.0" 404 162 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.001\n',
                                   b'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/25020545 HTTP/1.1" 200 969 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752761" "dc7161be3" 0.738\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/7763463 HTTP/1.1" 200 1018 "-" "Configovod" "-" "1498697422-2118016444-4708-9752774" "712e90144abee9" 0.181\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/16168711 HTTP/1.1" 200 16478 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752775" "712e90144abee9" 0.190\n',
                                   b'1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25023278 HTTP/1.1" 200 924 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752762" "dc7161be3" 0.841\n',
                                   b'1.194.135.240 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/group/7786682/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697423-3979856266-4708-9752778" "8a7741a54297568b" 0.068\n',
                                   b'1.196.116.32 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/25013431 HTTP/1.1" 200 948 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393-4708-9752758" "dc7161be3" 0.917\n',
                                   b'1.168.65.96 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/internal/banner/24288647/info HTTP/1.1" 200 351 "-" "-" "-" "1498697423-2539198130-4708-9752780" "89f7f1be37d" 0.072\n',
                                   b'1.169.137.128 -  - [29/Jun/2017:03:50:23 +0300] "GET /api/v2/banner/21456892 HTTP/1.1" 200 70795 "-" "Slotovod" "-" "1498697423-2118016444-4708-9752779" "712e90144abee9" 0.158\n']
            stat = count_stats("test_path")
            self.assertEqual(stat, result)
        
if __name__ == '__main__':
    unittest.main()

