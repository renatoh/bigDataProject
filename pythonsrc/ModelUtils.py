import re
from numpy import array
from math import sqrt

from pyspark import SparkContext, SQLContext, SparkConf
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans, KMeansModel
import pathlib
import os

import pyspark.ml.clustering
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder, Normalizer
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml import Pipeline

import shutil
from pythonsrc.LogFileParser import parse_apache_log_line

conf = SparkConf().setAppName("Log Analyzer")

sc = SparkContext(conf=conf)

sqlContext = SQLContext(sc)

MODEL_LOCATION = '../resources/savedModel'

FILE_TRAINING_DATA = '../resources/10k_train.log'


def remove_existing_model(path):
    if os.path.exists(path) and os.path.isdir(path):
        shutil.rmtree(path)

def train_and_save_model(sc_local):
    trainingData = sc_local.textFile(FILE_TRAINING_DATA) \
        .map(lambda line: parse_apache_log_line(line, re)) \
        .map(lambda parsed_line: (parsed_line.response_code, parsed_line.content_size)) \
        .map(lambda line: Vectors.dense([float(x) for x in line]))
    model = KMeans.train(trainingData, 2, maxIterations=10, initializationMode="random")

    remove_existing_model(MODEL_LOCATION)
    pathlib.Path(MODEL_LOCATION).mkdir(parents=True, exist_ok=True)
    model.save(sc_local, MODEL_LOCATION)


def load_saved_model(sc_local, path):
    return KMeansModel.load(sc_local, path)

def train_and_save_model_df(sc_local):
    trainingData = sc_local.textFile(FILE_TRAINING_DATA) \
        .map(lambda line: parse_apache_log_line(line, re)) 
    data = trainingData.toDF()
    
    indexers = [ StringIndexer(inputCol=c, 
                           outputCol="{0}_indexed".format(c)) for c in ['endpoint','method'] ]
    encoders = [ OneHotEncoder(inputCol=indexer.getOutputCol(),
                 outputCol="{0}_encoded".format(indexer.getOutputCol()))
                 for indexer in indexers ]
    assembler = VectorAssembler(inputCols=['response_code', 'content_size'] + [encoder.getOutputCol() for encoder in encoders], 
                                outputCol='features')
    pipeline = Pipeline(stages=indexers + encoders + [assembler])
    model=pipeline.fit(data)
    output = model.transform(data)
    
    #normalizer = Normalizer(inputCol="features", outputCol="normFeatures", p=1.0)
    #output = normalizer.transform(output)

    kmeans = pyspark.ml.clustering.KMeans().setK(2).setSeed(1)
    model = kmeans.fit(output)
    
    remove_existing_model(MODEL_LOCATION)
    #pathlib.Path(MODEL_LOCATION).mkdir(parents=True, exist_ok=True)
    model.save(MODEL_LOCATION)

    predictions = model.transform(output)
    evaluator = ClusteringEvaluator()
    silhouette = evaluator.evaluate(predictions)
    
    print('Silhouette: ',silhouette)
    costs = model.computeCost(output)
    print('Costs: ',costs)

# train_and_save_model(sc)
# model = load_saved_model(sc,MODEL_LOCATION)
train_and_save_model_df(sc)