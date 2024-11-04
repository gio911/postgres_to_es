import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError

import backoff
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresExtractor:
    def __init__(self, dsn:str):
        self.dsn=dsn
        
    @backoff.on_exception(backoff.expo, OperationalError, max_tries=5)
    def connect(self):
        try:
            logger.info("Попытка подключения к базе данных...")
            self.conn = psycopg2.connect(self.dsn)
            self.conn.autocommit=True
            logger.info("Подключение к базе данных успешно!")
        except OperationalError as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
        
    def extract_data(self, last_processed_time):
        where_block = (
            f"""
            WHERE
                GREATEST(
                    content.film_work.modified,
                    content.genre.modified,
                    pers.modified
                ) >= '{last_processed_time}'
            """
            if last_processed_time else ""
        )

        query = f"""
                SELECT
                    content.film_work.id::VARCHAR AS id,
                    content.film_work.rating AS imdb_rating,
                    COALESCE(
                        ARRAY_AGG(DISTINCT content.genre.name),
                        ARRAY[]::text[]) AS genres,
                    content.film_work.title AS title,
                    COALESCE(content.film_work.description, '') AS description,
                    COALESCE(
                        ARRAY_AGG(DISTINCT pers.full_name)
                        FILTER (WHERE p.role = 'actor'),
                        ARRAY[]::text[]) AS actors_names,
                    COALESCE(
                        ARRAY_AGG(DISTINCT pers.full_name)
                        FILTER (WHERE p.role = 'writer'),
                        ARRAY[]::text[]) AS writers_names,
                    COALESCE(
                        ARRAY_AGG(DISTINCT pers.full_name)
                        FILTER (WHERE p.role = 'director'),
                        ARRAY[]::text[]) AS directors_names,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', pers.id, 'name', pers.full_name)
                        ) FILTER (WHERE p.role = 'director'),
                    '[]') AS directors,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', pers.id, 'name', pers.full_name)
                        ) FILTER (WHERE p.role = 'writer'),
                    '[]') AS writers,
                    COALESCE(
                        json_agg(DISTINCT jsonb_build_object(
                            'id', pers.id, 'name', pers.full_name)
                        ) FILTER (WHERE p.role = 'actor'),
                    '[]') AS actors,
                    GREATEST(
                        MAX(content.film_work.modified),
                        MAX(content.genre.modified),
                        MAX(pers.modified)
                    ) AS latest_modified -- Получаем последнее изменение
                FROM content.film_work
                LEFT OUTER JOIN content.genre_film_work
                    ON (content.film_work.id = content.genre_film_work.film_work_id)
                LEFT OUTER JOIN content.genre
                    ON (content.genre_film_work.genre_id = content.genre.id)
                LEFT OUTER JOIN content.person_film_work
                    ON (content.film_work.id = content.person_film_work.film_work_id)
                LEFT OUTER JOIN content.person AS pers
                    ON (content.person_film_work.person_id = pers.id)
                LEFT OUTER JOIN content.person_film_work AS p
                    ON (pers.id = p.person_id)
                {where_block}
                GROUP BY content.film_work.id
                ORDER BY latest_modified ASC
            """

        with self.conn.cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()

        # Получаем последнее время модификации
        latest_modified = max([record[-1] for record in records]) if records else last_processed_time
        # Возвращаем данные и последнее время модификации
        return records, latest_modified
    