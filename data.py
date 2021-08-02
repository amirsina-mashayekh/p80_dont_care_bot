import logging
import os
import psycopg2

dbCursor = None


def connect() -> bool:
    global dbCursor
    try:
        db = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
        db.autocommit = True
        dbCursor = db.cursor()
        logging.info('Connected to database')
        return True
    except psycopg2.Error:
        logging.exception('Error while connecting to database')
        return False


def create_tables() -> bool:
    global dbCursor
    try:
        dbCursor.execute(
            'CREATE TABLE IF NOT EXISTS \"DC_List\"'
            '('
            'id integer,'
            'chat_id bigint NOT NULL,'
            'not_important_id bigint NOT NULL,'
            'doesnt_care_id bigint NOT NULL,'
            'response_mode bigint NOT NULL,'
            'response_mode_option real NOT NULL,'
            'last_response_dt timestamp without time zone NOT NULL,'
            'response_counter smallint NOT NULL,'
            'PRIMARY KEY (id)'
            ');'
        )
        logging.info('Tables checked successfully')

        dbCursor.execute(
            'CREATE UNIQUE INDEX IF NOT EXISTS \"DC_Index\"'
            'ON \"DC_List\"('
            'chat_id,'
            'not_important_id,'
            'doesnt_care_id'
            ')'
        )
        logging.info('Indexes checked successfully')

        return True
    except psycopg2.Error:
        logging.exception('Error while creating tables')
        return False
