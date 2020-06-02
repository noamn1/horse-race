from datetime import datetime

from db.base_db_layer import BaseDBLayer
import mysql.connector
from decouple import config

from util import encode_auth_token


class MySqlDBLayer(BaseDBLayer):

    def get_user_by_id(self, user_id):
        try:
            user = self._get_from_cache("user_"+str(user_id))
            if user:
                return user
            else:
                cursor = self.__db.cursor()
                sql = "select id, name from users where id=%s"
                values = (user_id,)
                cursor.execute(sql, values)
                for (id, name, email, token) in cursor:
                    user = {"id": id, "name": name, "email": email, "token": token}
                    self._put_in_cache("user_"+str(id), user)
                    return user
        finally:
            cursor.close()

    def get_horse_by_id(self, horse_id):
        try:
            horse = self._get_from_cache("horse_"+str(horse_id))
            if horse:
                return horse
            else:
                cursor = self.__db.cursor()
                sql = "select id, name from horses where id=%s"
                values = (horse_id,)
                cursor.execute(sql, values)
                for (id, name) in cursor:
                    horse = {"id": id, "name": name}
                    return horse

                return None
        finally:
            cursor.close()

    def get_race_by_id(self, race_id):
        try:
            cursor = self.__db.cursor()
            sql = "select id, start_date, user_id from races where id=%s"
            values = (race_id,)
            cursor.execute(sql, values)
            record = cursor.fetchone()

            return {"id": race_id, "user_id": record[2], "start_date": record[1]}

        finally:
            cursor.close()

    def create_horse(self, name):
        try:
            cursor = self.__db.cursor()
            self.__db.start_transaction()
            sql = "insert into horse (name) values (%s)"
            values = (name,)
            cursor.execute(sql, values)
            self.__db.commit()

        except mysql.connector.Error as error:
            print("Failed to insert horse record to database rollback: {}".format(error))
            self.__db.rollback()  # reverting changes because of exception

        finally:
            cursor.close()

    def start_race(self, user_id, horses):
        try:
            cursor = self.__db.cursor()

            sql = "insert into races (user_id, start_date) values (%s, %s)"
            now = datetime.utcnow()
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            values = (user_id, now_str,)
            cursor.execute(sql, values)
            race_id = cursor.lastrowid

            for horse in horses:
                sql = "insert into race_horses (race_id, horse_id) values (%s, %s)"
                values = (race_id, horse,)
                cursor.execute(sql, values)

            self.__db.commit()
            return race_id
        except mysql.connector.Error as error:
            print("Failed to create race record to database rollback: {}".format(error))
            self.__db.rollback()  # reverting changes because of exception

        finally:
            cursor.close()

    def set_horse_finish_time(self, race_id, horse_id, finish_time, user_id):
        try:
            cursor = self.__db.cursor()
            sql = "select id, start_date, user_id from races where id=%s"
            values = (race_id,)
            cursor.execute(sql, values)
            record = cursor.fetchone()
            if record[2] != user_id:
                # user id mismatch! => validation err
                raise mysql.connector.Error

            sql = "update race_horses set finish_time=%s WHERE race_id=%s AND horse_id=%s"
            values = (finish_time, race_id, horse_id)
            cursor.execute(sql, values)
            race_horse_dict = {"finish_time": finish_time, "race_id": race_id, "horse_id": horse_id}
            self._put_in_cache("race_horse_" + str(cursor.lastrowid), race_horse_dict)
            self.__db.commit()
        except mysql.connector.Error as error:
            print("Failed to update horse finish time record: {}".format(error))
            self.__db.rollback()  # reverting changes because of exception

        finally:
            cursor.close()

    def signup(self, name, email, password):
        try:
            cursor = self.__db.cursor()
            self.__db.start_transaction()
            sql = "insert into users (name, email, password) values (%s, %s, %s)"
            ciphered_password = self.encrypt(password)
            values = (name, email, ciphered_password)
            cursor.execute(sql, values)
            user_id = cursor.lastrowid
            token = encode_auth_token(user_id)
            sql = "update users set token = %s WHERE id=%s"
            values = (token, user_id)
            cursor.execute(sql, values)
            self.__db.commit()
            user = {"id": user_id, "name": name, "email": email, "token": token}
            self._put_in_cache("user_" + str(user_id), user)
            return user

        except mysql.connector.Error as error:
            print("Failed to insert horse record to database rollback: {}".format(error))
            self.__db.rollback()  # reverting changes because of exception

        finally:
            cursor.close()

    def login(self, email, password):
        try:
            cursor = self.__db.cursor()
            # self.__db.start_transaction()
            sql = "select id, name, email, password from users where email=%s"
            values = (email,)
            cursor.execute(sql, values)
            record = cursor.fetchone()
            if record is None:
                return None

            decrypted_password = self.decrypt(record[3])
            if decrypted_password != password:
                return None

            token = encode_auth_token(record[0])
            sql = "update users set token = %s WHERE id=%s"
            values = (token, record[0])
            cursor.execute(sql, values)
            self.__db.commit()
            user_dict = {"id": record[0], "name": record[1], "email": record[2], "token": token}
            self._put_in_cache("user_"+str(record[0]), user_dict)
            return user_dict

        except mysql.connector.Error as error:
            print("Failed to fetch user record to database rollback: {}".format(error))
            self.__db.rollback()  # reverting changes because of exception

        finally:
            cursor.close()

    def shutdown_db(self):
        self.__db.close()

    def __connect(self):
        self.__db = mysql.connector.connect(
            host="localhost",
            user=config('MYSQL_USER'),
            passwd=config('PASSWORD'),
            database="Horse_Race"
        )

        self.__db.autocommit = False

    def __init__(self, cache):
        super(MySqlDBLayer, self).__init__(cache)
        self.__connect()
