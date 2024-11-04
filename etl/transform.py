from collections import defaultdict
from typing import Dict, List

from pydentic_model import FilmWorkModel, Person


class DataTransformer:
    def __init__(self, film_work_obj):
        self.film_work_obj=film_work_obj
        
    def transform(self):
       
        film_dict = defaultdict(lambda: {
        "id": None,
        "imdb_rating": None,
        "genres": [],
        "title": None,
        "description": None,
        "directors_names": [],
        "actors_names": [],
        "writers_names": [],
        "directors": [],
        "actors": [],
        "writers": []
        })    
        
        film_id=self.film_work_obj[0]
        
        if film_dict[film_id]["id"] is None:
            film_dict[film_id].update({
                "id": self.film_work_obj[0],
                "title": self.film_work_obj[3],
                "description": self.film_work_obj[4],
                "imdb_rating": self.film_work_obj[1],
                "genres": self.film_work_obj[2],
                "directors_names": self.film_work_obj[7],
                "actors_names": self.film_work_obj[5],
                "writers_names": self.film_work_obj[6],
                "directors": self.isNone_(self.film_work_obj[8]),
                "writers": self.isNone_(self.film_work_obj[9]),
                "actors": self.isNone_(self.film_work_obj[10]),
            })
        # Преобразуем словарь в список объектов FilmWorkModel
        return [FilmWorkModel(**data).model_dump() for data in film_dict.values()]
        
    def isNone_(self, obj):
        if isinstance(obj, list):
            return [Person(**person) for person in obj]
        else:
            return []
        
        