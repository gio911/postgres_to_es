import time
import os

from extract import PostgresExtractor
from load import ElasticsearchLoader
from state import JsonFileStorage
from transform import DataTransformer 

state=None

def main():
    
    storage = JsonFileStorage('storage.json')
    state = storage.retrieve_state()
    last_processed_time=state.get('last_processed_time', 0)
    
    postgres_dsn = os.environ.get('POSTGRES_DSN')
    
    elastic_host = os.environ.get('ES_HOST')
    
    postgres_extractor = PostgresExtractor(dsn=postgres_dsn)
    elasticsearch_loader = ElasticsearchLoader(es_host=elastic_host)

    postgres_extractor.connect()
    
    while True:
        data_batch, latest_modified = postgres_extractor.extract_data(last_processed_time)
    
        if not data_batch:
            time.sleep(10) 
            continue
        
        for film_work_obj in data_batch:
            transformer = DataTransformer(film_work_obj)
            transformed_data=transformer.transform()
            elasticsearch_loader.load_data(transformed_data)
            last_processed_time=latest_modified.isoformat()
            storage.save_state({"last_processed_time":last_processed_time})
            
        time.sleep(1)
        
if __name__ == "__main__":
    main()