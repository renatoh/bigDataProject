from pyspark.mllib.clustering import KMeans, KMeansModel

import re

from pyspark import SparkContext, SparkConf
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans
import pathlib
import os

import shutil
from pythonsrc.LogFileParser import parse_apache_log_line

conf = SparkConf().setAppName("Log Analyzer")

sc = SparkContext(conf=conf)

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

# train_and_save_model(sc)
# model = load_saved_model(sc,MODEL_LOCATION)
