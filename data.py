import logging
import os

import psycopg2
from psycopg2 import extensions
from typing import Optional

import doesntCare

db: psycopg2.extensions.connection


def connect() -> bool:
    global db
    try:
        db = psycopg2.connect(os.environ.get('DATABASE_URL'))
        db.autocommit = True
        logging.info('Connected to database')
        return True
    except psycopg2.Error:
        logging.exception('Error while connecting to database')
        return False


def create_tables() -> bool:
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'CREATE TABLE IF NOT EXISTS \"DC_List\"'
                '('
                'id SERIAL,'
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

            cur.execute(
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
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'INSERT INTO \"DC_List\"(chat_id, not_important_id, doesnt_care_id, response_mode, '
                'response_mode_option, last_response_dt, response_counter) '
                'VALUES(%s, %s, %s, %s, %s, %s, %s)',
                (dc.chat_id, dc.not_important_id, dc.doesnt_care_id, dc.response_mode, dc.response_mode_option,
                 dc.last_response_dt, dc.response_counter)
            )
        return True
    except psycopg2.Error:
        logging.exception('Error while adding new entry to database')
        return False


def update(dc: doesntCare.DoesntCare) -> bool:
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'UPDATE \"DC_List\" SET '
                'last_response_dt = %s,'
                'response_counter = %s'
                'WHERE chat_id = %s AND '
                'not_important_id = %s AND '
                'doesnt_care_id = %s',
                (dc.last_response_dt, dc.response_counter, dc.chat_id, dc.not_important_id, dc.doesnt_care_id)
            )
        return True
    except psycopg2.Error:
        logging.exception('Error while adding new entry to database')
        return False


def remove(dc: doesntCare.DoesntCare) -> bool:
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'DELETE FROM \"DC_List\" WHERE '
                'chat_id = %s AND '
                'not_important_id = %s AND '
                'doesnt_care_id = %s',
                (dc.chat_id, dc.not_important_id, dc.doesnt_care_id)
            )
        return True
    except psycopg2.Error:
        logging.exception('Error while removing entry from database')
        return False


def remove_all_dci(doesnt_care_id: int, chat_id: int) -> bool:
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'DELETE FROM \"DC_List\" WHERE '
                'doesnt_care_id = %s AND '
                'chat_id = %s',
                (doesnt_care_id, chat_id)
            )
        return True
    except psycopg2.Error:
        logging.exception('Error while removing all for doesnt_care_id')
        return False


def find(chat_id: int, not_important_id: str, doesnt_care_id: int) -> Optional[doesntCare.DoesntCare]:
    global db
    try:
        with db.cursor() as cur:
            cur.execute(
                'SELECT response_mode, response_mode_option, last_response_dt, response_counter '
                'FROM \"DC_List\" WHERE '
                'chat_id = %s AND '
                'not_important_id = %s AND '
                'doesnt_care_id = %s',
                (chat_id, not_important_id, doesnt_care_id)
            )

            row = cur.fetchone()
            if row is None:
                return None  # Record not found

            return doesntCare.DoesntCare(
                chat_id=chat_id,
                not_important_id=not_important_id,
                doesnt_care_id=doesnt_care_id,
                response_mode=row[0],
                response_mode_option=row[1],
                last_response_dt=row[2],
                response_counter=row[3]
            )
    except psycopg2.Error:
        logging.exception('Error while querying data')
        raise


def find_by_nii_ci(not_important_id: str, chat_id: int) -> Optional[list]:
    global db
    dc_list = []
    try:
        with db.cursor() as cur:
            cur.execute(
                'SELECT doesnt_care_id, response_mode, response_mode_option, last_response_dt, response_counter '
                'FROM \"DC_List\" WHERE '
                'not_important_id = %s AND '
                'chat_id = %s',
                (not_important_id, chat_id)
            )

            res = cur.fetchall()

            for row in res:
                dc_list.append(doesntCare.DoesntCare(
                    chat_id=chat_id,
                    not_important_id=not_important_id,
                    doesnt_care_id=row[0],
                    response_mode=row[1],
                    response_mode_option=row[2],
                    last_response_dt=row[3],
                    response_counter=row[4]
                ))
        return dc_list
    except psycopg2.Error:
        logging.exception('Error while querying data')
        return None
