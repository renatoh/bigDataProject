#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:54:19 2021

@author: thomas vinzenz
"""

import re
from math import sqrt
from numpy import array
from datetime import datetime

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import Row
from pyspark.sql import SQLContext
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder, Normalizer
from pyspark.ml.clustering import KMeans, KMeansModel
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml import Pipeline, PipelineModel

from pythonsrc.LogFileParser import parse_apache_log_line

conf = SparkConf().setAppName("Log Analyzer")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 60)
sqlContext = SQLContext(sc)

RDD_LOCATION = '../resources/'
MODEL_LOCATION = '../resources/savedModel'
TRANSFORM_MODEL_LOCATION = '../resources/savedModelTransform'

SOCKET_HOST = '84.20.60.172'
SOCKET_PORT = 8080

def error(point, cluster_center):
    return sqrt(sum([x**2 for x in (point - cluster_center)]))

def calc_error(rdd):
    now = datetime.now()
    data = rdd.toDF()

    output = transform_model.transform(data)
    predictions = model.transform(output)
  
    wssse = predictions.select(['features','prediction'])\
      .rdd\
      .map(lambda line: error(line[0],clusterCenters[line[1]]))\
      .filter(lambda x: x > 125100.0)
    if wssse.count() > 0:
        wssse.saveAsTextFile(RDD_LOCATION+str(now))
    return wssse

model = KMeansModel.load(MODEL_LOCATION)
transform_model = PipelineModel.load(TRANSFORM_MODEL_LOCATION)
clusterCenters = model.clusterCenters()

access_logs = ssc.socketTextStream(SOCKET_HOST, SOCKET_PORT)
struc_logs = access_logs.map(lambda line: parse_apache_log_line(line, re))
struc_logs.pprint()
rc_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, 1)) 
rc_count = rc_dstream.reduceByKey(lambda x,y: x+y)
rc_count.pprint(num = 30)
struc_logs.foreachRDD(calc_error)
ssc.start()
ssc.awaitTermination()
