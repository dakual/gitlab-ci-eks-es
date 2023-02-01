import prometheus_client as prom
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from prometheus_client import start_http_server, Gauge, Summary, Counter, Histogram, Info, Enum
import prometheus_client
import logging
import sys, time, os
import yaml
import json

prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)


ES_URI        = os.getenv("ES_URI")
ES_APIKEY     = os.getenv("ES_APIKEY")
APP_PORT      = os.getenv('APP_PORT')

logging.basicConfig(
  level    = logging.INFO,
  format   = "%(asctime)s [%(levelname)s] %(message)s",
  handlers = [
    logging.StreamHandler(sys.stdout)
  ]
)

class ESCollector():

  def __init__(self):
    try:
      if ES_URI is None:
        raise Exception("Environment variables missing! ES_URI is required!")
      
      if ES_APIKEY is None:
        raise Exception("Environment variables missing! ES_APIKEY is required!")

      if APP_PORT is None:
        raise Exception("Environment variables missing! APP_PORT is required!")

      with open("inventories.yaml", "r") as stream:
        try:
          self.inventory = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
          print(exc)
          raise Exception("Inventory file error!")

      self.ERRORCODE = Gauge("ERROR", "Description of gauge", ["Code", "Index", "Brand"])
      self.ERRORCODE_TOTAL = Gauge("ERROR_TOTAL", "Description of gauge", ["Code"])

      self.es = Elasticsearch(ES_URI, api_key=ES_APIKEY)    
    except Exception as e:
      logging.error(e)
      exit(1)

  def get_metric_data(self):    
    query = {
      "bool": {
        "must": [{
          "range": {
            "@timestamp": {
              "gte": "now-1m",
              "lte": "now"
            }
          }
        }],
        "should": [],
        "minimum_should_match": 1
      }
    }

    for errorCode in self.inventory["ErrorCodes"]:
      query["bool"]["should"].append({
          "match": {
              "errorCode": errorCode
          }
      })

    result = self.es.search(
      index = "index_*",
      query = query,
      size  = 1000
    )   

    self.ERRORCODE.clear()
    self.ERRORCODE_TOTAL.clear()
    allHits = result['hits']['hits']
    for num, doc in enumerate(allHits):
      errorCode = doc["_source"]["errorCode"]
      
      self.ERRORCODE.labels(Code=errorCode, Index=doc["_index"], Brand=doc["_source"]["brand"]).inc()
      self.ERRORCODE_TOTAL.labels(Code=errorCode).inc()


if __name__ == '__main__':
  logging.info(f'Starting exporter service on port {APP_PORT}')

  collector = ESCollector()
  start_http_server(int(APP_PORT))
  while True:
    collector.get_metric_data()
    time.sleep (60)

    