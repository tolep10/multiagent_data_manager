from psycopg2 import pool
from psycopg2.pool import SimpleConnectionPool

from ...utils import settings

class DBPoolConnection:
    __db_pool = None

    def __init__(self):
        pass

    @classmethod
    async def __create_pool_connection(cls) -> None:
        if not settings.validate_db_vars():
            raise RuntimeError("No estan definidas las credenciales para conectarse a la base de datos")

        db_config = {
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
        }

        DBPoolConnection.__db_pool = pool.SimpleConnectionPool(1, 10, **db_config)


    @staticmethod
    async def get_db_pool() -> SimpleConnectionPool:
        if not DBPoolConnection.__db_pool:
            await DBPoolConnection.__create_pool_connection()

        return DBPoolConnection.__db_pool





        
