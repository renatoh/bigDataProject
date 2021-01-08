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
from pyspark.ml import Pipeline

from pythonsrc.LogFileParser import parse_apache_log_line

conf = SparkConf().setAppName("Log Analyzer")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 10)
sqlContext = SQLContext(sc)

RDD_LOCATION = '../resources/'

SOCKET_HOST = '84.20.60.172'
SOCKET_PORT = 8080

def error(point, cluster_center):
    return sqrt(sum([x**2 for x in (point - cluster_center)]))

def calc_error(rdd):
    now = datetime.now()
    data = trainingData.toDF()
    
    indexers = [ StringIndexer(inputCol=c, 
                           outputCol="{0}_indexed".format(c)) for c in ['endpoint','method'] ]
    encoders = [ OneHotEncoder(inputCol=indexer.getOutputCol(),
                 outputCol="{0}_encoded".format(indexer.getOutputCol()))
                 for indexer in indexers ]
    assembler = VectorAssembler(inputCols=['response_code', 'content_size'] + [encoder.getOutputCol() for encoder in encoders], 
                                outputCol='features')
    pipeline = Pipeline(stages=indexers + encoders + [assembler])
    modelTransform=pipeline.fit(data)
    output = modelTransform.transform(data)
    predictions = model.transform(output)
  
    wssse = predictions.select(['features','prediction'])\
      .rdd\
      .map(lambda line: error(line[0],clusterCenters[line[1]]))\
      .filter(lambda x: x > 125100.0)
    if wssse.count() > 0:
        wssse.saveAsTextFile(RDD_LOCATION+str(now))
    return wssse

access_logs = ssc.socketTextStream(SOCKET_HOST, SOCKET_PORT)
struc_logs = access_logs.map(lambda line: parse_apache_log_line(line, re))
struc_logs.pprint()
rc_dstream = struc_logs.map(lambda parsed_line: (parsed_line.response_code, 1)) 
rc_count = rc_dstream.reduceByKey(lambda x,y: x+y)
rc_count.pprint(num = 30)
struc_logs.foreachRDD(calc_error)
ssc.start()
ssc.awaitTermination()
