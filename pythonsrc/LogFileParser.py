from pyspark.sql import Row
import re
APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:\/]+\s)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'

def parse_apache_log_line(all_logs):

    logEntries = all_logs.split(',')



    log_rows = []


    for log_line in logEntries:
        match = re.search(APACHE_ACCESS_LOG_PATTERN, log_line)
        # print("Log-line" + str(all_logs))
        if match is None:
            raise Exception("Invalid logline: %s" % all_logs)
        row =  Row(
            ip_address    = match.group(1),
            client_identd = match.group(2),
            user_id       = match.group(3),
            date = (match.group(4)[:-6]).split(":", 1)[0],
            time = (match.group(4)[:-1]).split(":", 1)[1],
            method        = match.group(5),
            endpoint      = match.group(6),
            protocol      = match.group(7),
            response_code = int(match.group(8)),
            content_size  = int(match.group(9))
        )
        log_rows.append(row)

    return log_rows

# logLine = 'e78.93.0.76 - - [12/Jan/2021:19:56:22 ] "POST /news HTTP/1.0" 500 910591,118.140.28.98 - lb2 [12/Jan/2021:19:56:22 ] "POST /index.html HTTP/1.0" 200 978855,8.237.116.63 - lb1 [12/Jan/2021:19:56:23 ] "GET /contact HTTP/1.0" 200 592553,112.122.240.41 - - [12/Jan/2021:19:56:23 ] "GET /news HTTP/1.0" 200 20808,21.142.122.171 - - [12/Jan/2021:19:56:23 ] "POST /contact HTTP/1.0" 302 809530,91.19.157.99 - - [12/Jan/2021:19:56:23 ] "POST /contact HTTP/1.0" 201 138248,81.1.181.124 - lb2 [12/Jan/2021:19:56:23 ] "POST /login-page HTTP/1.0" 302 901391,77.107.129.170 - - [12/Jan/2021:19:56:24 ] "GET /my-account HTTP/1.0" 200 636666,241.178.114.57 - lb2 [12/Jan/2021:19:56:24 ] "POST /news HTTP/1.0" 200 950253,61.139.251.31 - - [12/Jan/2021:19:56:24 ] "GET /contact HTTP/1.0" 301 780995,136.85.11.152 - lb2 [12/Jan/2021:19:56:24 ] "POST /login-page HTTP/1.0" 201 100997,234.55.161.123 - - [12/Jan/2021:19:56:24 ] "GET /blog HTTP/1.0" 200 848641,248.73.244.147 - - [12/Jan/2021:19:56:25 ] "POST /blog HTTP/1.0" 302 883106,88.180.99.199 - lb2 [12/Jan/2021:19:56:25 ] "GET /contact HTTP/1.0" 200 602782,12.233.136.53 - lb1 [12/Jan/2021:19:56:25 ] "POST /news HTTP/1.0" 301 236524,243.128.16.144 - - [12/Jan/2021:19:56:25 ] "GET / HTTP/1.0" 200 483753,36.37.217.81 - - [12/Jan/2021:19:56:25 ] "POST /contact HTTP/1.0" 200 18656,100.244.252.238 - - [12/Jan/2021:19:56:26 ] "GET / HTTP/1.0" 200 365755,6.115.191.24 - lb2 [12/Jan/2021:19:56:26 ] "POST /contact HTTP/1.0" 200 784024,252.140.71.212 - - [12/Jan/2021:19:56:26 ] "GET /index.html HTTP/1.0" 200 686430,171.16.133.230 - lb2 [12/Jan/2021:19:56:26 ] "POST /contact HTTP/1.0" 200 665105,85.253.26.69 - - [12/Jan/2021:19:56:26 ] "GET /contact HTTP/1.0" 200 81266,107.229.74.166 - - [12/Jan/2021:19:56:27 ] "GET /index.html HTTP/1.0" 200 700524,146.223.101.100 - - [12/Jan/2021:19:56:27 ] "GET /contact HTTP/1.0" 200 871034,30.217.228.214 - - [12/Jan/2021:19:56:27 ] "POST /contact HTTP/1.0" 200 91985'
#
# result = parse_apache_log_line(logLine)
#
#
# print(result)
