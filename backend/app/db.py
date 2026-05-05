from neo4j import GraphDatabase
from app.config import settings

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            max_connection_pool_size=50,
            connection_timeout=30,
        )
        _driver.verify_connectivity()
    return _driver

def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None

def get_session():
    return get_driver().session(database=settings.NEO4J_DATABASE or None)
