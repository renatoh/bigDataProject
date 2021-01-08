#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:54:19 2021

@author: thomas vinzenz
"""

import re
from math import sqrt
from numpy import array

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row
from pyspark.sql import SQLContext
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

from pythonsrc.LogFileParser import parse_apache_log_line

conf = SparkConf().setAppName("Log Analyzer")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 10)
sqlContext = SQLContext(sc)

SOCKET_HOST = '84.20.60.172'
SOCKET_PORT = 8080

def error(point, cluster_center):
    return sqrt(sum([x**2 for x in (point - cluster_center)]))

access_logs = ssc.socketTextStream(SOCKET_HOST, SOCKET_PORT)
#access_logs = ssc.textFileStream('/Users/thomas/Downloads/logstream/')
struc_logs = access_logs.map(parse_apache_log_line)
struc_logs.pprint()
rc_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, 1)) 
rc_count = rc_dstream.reduceByKey(lambda x,y: x+y)
rc_count.pprint(num = 30)
cluster_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, parsed_line.content_size)) 
#result = cluster_dstream.map(lambda point: error(point))
#result.pprint()
ssc.start()
ssc.awaitTermination()
