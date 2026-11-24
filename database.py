import os
from contextlib import closing, contextmanager

import mysql.connector


class DatabaseUnavailable(Exception):
    """The database connection could not be configured or opened."""


def connect():
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    if not database or not user or password is None:
        raise DatabaseUnavailable

    try:
        port = int(os.getenv("DB_PORT", "3306"))
    except ValueError as error:
        raise DatabaseUnavailable from error
    if not 1 <= port <= 65535:
        raise DatabaseUnavailable

    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            port=port,
            database=database,
            user=user,
            password=password,
            autocommit=False,
            connection_timeout=5,
        )
    except mysql.connector.Error as error:
        raise DatabaseUnavailable from error


@contextmanager
def database_cursor(*, write=False):
    with closing(connect()) as connection:
        with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
            try:
                yield cursor
                if write:
                    connection.commit()
            except Exception:
                if write:
                    connection.rollback()
                raise
