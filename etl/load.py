import logging
from elasticsearch import Elasticsearch, exceptions, helpers
from typing import Dict
import backoff

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ElasticsearchLoader:
    def __init__(self, es_host:str):
        """
        Инициализация подключения к Elasticsearch
        """
        self.es_host=es_host
        self.es=self.connect_to_es()
        self.create_index()
        
    @backoff.on_exception(backoff.expo, (exceptions.ConnectionError,), max_tries=10, logger=logging.getLogger())
    def connect_to_es(self) -> Elasticsearch:
        logging.info("Попытка конекта к Elasticsearch...")

        """
        Подключение к Elasticsearch с использованием backoff.
        """
        es = Elasticsearch(self.es_host)
        if not es.info():
            raise ConnectionError("Ожидается подключение...")
        return es
    
    def create_index(self):
        index_name = "movies"
        # time.sleep(30)
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(
                index=index_name,
                body={
                    "settings": {
                        "refresh_interval": "1s",
                        "analysis": {
                            "filter": {
                                "english_stop": {
                                    "type": "stop",
                                    "stopwords": "_english_"
                                },
                                "english_stemmer": {
                                    "type": "stemmer",
                                    "language": "english"
                                },
                                "english_possessive_stemmer": {
                                    "type": "stemmer",
                                    "language": "possessive_english"
                                },
                                "russian_stop": {
                                    "type": "stop",
                                    "stopwords": "_russian_"
                                },
                                "russian_stemmer": {
                                    "type": "stemmer",
                                    "language": "russian"
                                }
                            },
                            "analyzer": {
                                "ru_en": {
                                    "tokenizer": "standard",
                                    "filter": [
                                        "lowercase",
                                        "english_stop",
                                        "english_stemmer",
                                        "english_possessive_stemmer",
                                        "russian_stop",
                                        "russian_stemmer"
                                    ]
                                }
                            }
                        }
                    },
                    "mappings": {
                        "dynamic": "strict",
                        "properties": {
                            "id": {"type": "keyword"},
                            "imdb_rating": {"type": "float"},
                            "genres": {"type": "keyword"},
                            "title": {
                                "type": "text",
                                "analyzer": "ru_en",
                                "fields": {"raw": {"type": "keyword"}}
                            },
                            "description": {"type": "text", "analyzer": "ru_en"},
                            "directors_names": {"type": "text", "analyzer": "ru_en"},
                            "actors_names": {"type": "text", "analyzer": "ru_en"},
                            "writers_names": {"type": "text", "analyzer": "ru_en"},
                            "directors": {
                                "type": "nested",
                                "dynamic": "strict",
                                "properties": {
                                    "id": {"type": "keyword"},
                                    "name": {"type": "text", "analyzer": "ru_en"}
                                }
                            },
                            "actors": {
                                "type": "nested",
                                "dynamic": "strict",
                                "properties": {
                                    "id": {"type": "keyword"},
                                    "name": {"type": "text", "analyzer": "ru_en"}
                                }
                            },
                            "writers": {
                                "type": "nested",
                                "dynamic": "strict",
                                "properties": {
                                    "id": {"type": "keyword"},
                                    "name": {"type": "text", "analyzer": "ru_en"}
                                }
                            }
                        }
                    }
                }
            )
            logging.info(f"Индекс '{index_name}' был создан.")
        else:
            logging.info(f"Индекс '{index_name}' уже существует.")    


    def load_data(self, data:Dict):
        
        data_to_insert=[
            {
                "_index": "movies",  
                "_id": film['id'],    
                "_source": film 
            }
            for film in data
        ]
        
        helpers.bulk(self.es, data_to_insert, chunk_size=100)