from pydantic import BaseModel, Field
from typing import List, Optional


class Person(BaseModel):
    id:str 
    name:str
    
class FilmWorkModel(BaseModel):
    id:str 
    imdb_rating: Optional[float]
    genres: List[str]
    title: str
    description: Optional[str]
    directors_names: List[str]=[]
    actors_names: List[str]=[]
    writers_names: List[str]=[]
    directors: List[Person]=[]
    actors: List[Person]=[]
    writers: List[Person]=[]
    
