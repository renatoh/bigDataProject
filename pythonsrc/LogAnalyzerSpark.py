#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:24:58 2021

@author: thomas vinzenz

Run as: spark-submit LogAnalyzerSpark.py
spark-submit is from Apache Spark (https://spark.apache.org/downloads.html)
"""

import re
from pyspark.sql import Row
from pyspark.sql import SparkSession

APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:\/]+\s)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'

SOCKET_HOST = '84.20.60.172'
SOCKET_PORT = 8080

def parse_apache_log_line(logline):
    match = re.search(APACHE_ACCESS_LOG_PATTERN, logline)
    if match is None:
        raise Exception("Invalid logline: %s" % logline)
    return Row(
        ip_address    = match.group(1),
        client_identd = match.group(2),
        user_id       = match.group(3),
        date = (match.group(4)[:-6]).split(":", 1)[0],
        time = (match.group(4)[:-6]).split(":", 1)[1],
        method        = match.group(5),
        endpoint      = match.group(6),
        protocol      = match.group(7),
        response_code = int(match.group(8)),
        content_size  = int(match.group(9))
    )

spark = SparkSession.builder.appName("Log Analyzer").getOrCreate()

df = spark.readStream.format("socket").option("host", SOCKET_HOST).option("port", SOCKET_PORT).load()

streamingQuery =\
df \
  .writeStream \
  .format("console") \
  .queryName("myQuery") \
  .outputMode('append') \
  .start() \
  .awaitTermination()

#  .foreach(lambda row: parse_apache_log_line(row.value)) \
