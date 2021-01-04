#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:54:19 2021

@author: thomas vinzenz
"""

import re
from math import sqrt

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row
from pyspark.sql import SQLContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans

conf = SparkConf().setAppName("Log Analyzer")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 10)
sqlContext = SQLContext(sc)

APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:\/]+\s)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+)'

SOCKET_HOST = '84.20.60.172'
SOCKET_PORT = 8080
FILE_TRAINING_DATA = '/Users/thomas/Downloads/logstream/apache2.log'

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

#train modell (based on REsponde Code and Content Size for simplicity)
trainingData = sc.textFile(FILE_TRAINING_DATA)\
  .map(parse_apache_log_line)\
  .map(lambda parsed_line: (parsed_line.response_code, parsed_line.content_size))\
  .map(lambda line: Vectors.dense([float(x) for x in line]))

clusters = KMeans.train(trainingData, 2, maxIterations=10, initializationMode="random")

def error(point):
    center = clusters.centers[clusters.predict(point)]
    return sqrt(sum([x**2 for x in (point - center)]))

access_logs = ssc.socketTextStream(SOCKET_HOST, SOCKET_PORT)
#access_logs = ssc.textFileStream('/Users/thomas/Downloads/logstream/')
struc_logs = access_logs.map(parse_apache_log_line)
struc_logs.pprint()
rc_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, 1)) 
rc_count = rc_dstream.reduceByKey(lambda x,y: x+y)
rc_count.pprint(num = 30)
cluster_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, parsed_line.content_size)) 
result = cluster_dstream.map(lambda point: error(point))
result.pprint()
ssc.start()
ssc.awaitTermination()
