import logging
import os

import psycopg2
from typing import Optional

import doesntCare

# This won't run. Just to suppress IDE warnings and help code auto-complete
db_cursor = psycopg2.connect('').cursor()


def connect() -> bool:
    global db_cursor
    try:
        db = psycopg2.connect(os.environ.get('DB_URI'))
        db_cursor = db.cursor()
        logging.info('Connected to database')
        return True
    except psycopg2.Error:
        logging.exception('Error while connecting to database')
        return False


def create_tables() -> bool:
    global db_cursor
    try:
        db_cursor.execute(
            'CREATE TABLE IF NOT EXISTS \"DC_List\"'
            '('
            'id INTEGER,'
            'chat_id BIGINT NOT NULL,'
            'not_important_id TEXT NOT NULL,'
            'doesnt_care_id BIGINT NOT NULL,'
            'response_mode SMALLINT NOT NULL,'
            'response_mode_option REAL NOT NULL,'
            'last_response_dt TIMESTAMP NOT NULL,'
            'response_counter INTEGER NOT NULL,'
            'PRIMARY KEY (id)'
            ');'
        )
        logging.info('Tables checked successfully')

        db_cursor.execute(
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


def insert(dc: doesntCare.DoesntCare) -> bool:
    global db_cursor
    try:
        db_cursor.execute(
            'INSERT INTO \"DC_List\"(chat_id, not_important_id, doesnt_care_id, response_mode, '
            'response_mode_option, last_response_dt, response_counter) '
            'VALUES(?, ?, ?, ?, ?, ?, ?)',
            (dc.chat_id, dc.not_important_id, dc.doesnt_care_id, dc.response_mode, dc.response_mode_option,
             dc.last_response_dt, dc.response_counter)
        )
        return True
    except psycopg2.Error:
        logging.exception('Error while adding new entry to database')
        return False


def update(dc: doesntCare.DoesntCare) -> bool:
    global db_cursor
    try:
        db_cursor.execute(
            'UPDATE \"DC_List\" SET '
            'last_response_dt = ?,'
            'response_counter = ?'
            'WHERE chat_id = ? and '
            'not_important_id = ? and '
            'doesnt_care_id = ?',
            (dc.last_response_dt, dc.response_counter, dc.chat_id, dc.not_important_id, dc.doesnt_care_id)
        )
        return True
    except psycopg2.Error:
        logging.exception('Error while adding new entry to database')
        return False


def remove(dc: doesntCare.DoesntCare) -> bool:
    global db_cursor
    try:
        db_cursor.execute(
            'DELETE FROM \"DC_List\" WHERE '
            'chat_id = ? and '
            'not_important_id = ? and '
            'doesnt_care_id = ?',
            (dc.chat_id, dc.not_important_id, dc.doesnt_care_id)
        )
        return True
    except psycopg2.Error:
        logging.exception('Error while removing entry from database')
        return False


def remove_all_dci(doesnt_care_id: int, chat_id: int) -> bool:
    global db_cursor
    try:
        db_cursor.execute(
            'DELETE FROM \"DC_List\" WHERE '
            'doesnt_care_id = ? and '
            'chat_id = ?',
            (doesnt_care_id, chat_id)
        )
        return True
    except psycopg2.Error:
        logging.exception('Error while removing all for doesnt_care_id')
        return False


def find(chat_id: int, not_important_id: str, doesnt_care_id: int) -> Optional[doesntCare.DoesntCare]:
    global db_cursor
    try:
        db_cursor.execute(
            'SELECT * FROM \"DC_List\" WHERE '
            'chat_id = ? and '
            'not_important_id = ? and '
            'doesnt_care_id = ?',
            (chat_id, not_important_id, doesnt_care_id)
        )

        res = db_cursor.fetchone()
        if res is None:
            return None  # Record not found

        return doesntCare.DoesntCare(
            chat_id=chat_id,
            not_important_id=not_important_id,
            doesnt_care_id=doesnt_care_id,
            response_mode=res['response_mode'],
            response_mode_option=res['response_mode_option'],
            last_response_dt=res['last_response_dt'],
            response_counter=res['response_counter']
        )
    except psycopg2.Error:
        logging.exception('Error while querying data')
        raise


def find_by_nii_ci(not_important_id: str, chat_id: int) -> Optional[list]:
    global db_cursor
    dc_list = []
    try:
        db_cursor.execute(
            'SELECT * FROM \"DC_List\" WHERE '
            'not_important_id = ? and '
            'chat_id = ?',
            (not_important_id, chat_id)
        )

        res = db_cursor.fetchall()

        for row in res:
            dc_list.append(doesntCare.DoesntCare(
                chat_id=row['chat_id'],
                not_important_id=not_important_id,
                doesnt_care_id=row['doesnt_care_id'],
                response_mode=row['response_mode'],
                response_mode_option=row['response_mode_option'],
                last_response_dt=row['last_response_dt'],
                response_counter=row['response_counter']
            ))
        return dc_list
    except psycopg2.Error:
        logging.exception('Error while querying data')
        return None


def vacuum() -> bool:
    global db_cursor
    try:
        db_cursor.execute('VACUUM')
        logging.info('VACUUM done.')
        return True
    except psycopg2.Error:
        logging.exception('Error while performing VACUUM')
        return False
