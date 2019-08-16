import datetime
import uuid
import logging

from cassandra.cluster import Cluster

logger = logging.getLogger('MnistServer.DB_Helper')


class DBHelper:
    def __init__(self):
        self._cluster = None
        self._session = None

    def init(self, address='127.0.0.1', port=9042):
        self._cluster = Cluster(contact_points=[address], port=port)
        self._session = self._cluster.connect()
        self._init_key_space()
        self._init_table()

    def _init_key_space(self):
        try:
            self._session.execute("""
                    CREATE KEYSPACE IF NOT EXISTS mnistserver
                    WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 2};""")
            self._session.set_keyspace('mnistserver')
        except Exception as e:
            logger.error("Init key space failed. details:{}".format(e))

    def _init_table(self):
        try:
            self._session.execute("""
                CREATE TABLE IF NOT EXISTS mnist_server(
                    id Text PRIMARY KEY,
                    image Text,
                    time timestamp,
                    identify Text);  
                    """)
        except Exception as e:
            logger.error("Init table failed, details:{}".format(e))

    def init_db(self):
        self._init_key_space()
        self._init_table()

    def insert_data(self, image, identify):
        try:
            self._session.execute("""
                      INSERT INTO mnist_server (id, image, time, identify) 
                      VALUES('{}', '{}', '{}', '{}');
                      """.format(str(uuid.uuid1()), image, int(datetime.datetime.utcnow().timestamp() * 1000),
                                 identify))

        except Exception as e:
            logger.error("Insert data failed, details;{}".format(e))

    def query_data(self):
        try:
            return self._session.execute("""
                SELECT * from mnist_server;""")
        except Exception as e:
            logger.error("Query data failed, details:{}".format(e))

    def reset_db(self):
        try:
            self._session.execute("""
                DROP KEYSPACE mnistserver;
                """)
        except Exception as e:
            logger.error("Reset db failed, details:{}".format(e))


db_helper = DBHelper()
