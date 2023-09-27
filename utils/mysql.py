from mysql.connector import pooling, connect, OperationalError, Error, errorcode
import traceback


class Mysql:

    # Connection pools.
    pools = {}

    def __init__(self, app, host, port, user, pwd, dbname):
        self.app = app
        self.config = self.app.config
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.dbname =dbname

        self.conn = None
        self.last_errno = None
        self.last_rowid = None
        self.affected_rows = None


        try:
            key = (host, port, user, pwd, dbname)
            if key not in Mysql.pools:
                Mysql.pools[key] = pooling.MySQLConnectionPool(
                    pool_name=dbname,
                    pool_size=self.config.db_pool_size,
                    pool_reset_session=True,
                    host=host,
                    port=port,
                    user=user,
                    password=pwd,
                    database=dbname,
                )
            pool = Mysql.pools[key]
            self.conn = pool.get_connection()
        except Error as err:
            self.app.log(f"{err}")
            self.last_errno = err.errno

    def __repr__(self):
        return  f'''Mysql(
                        app = {self.app} \n
                        host = {self.host}\n
                        port = {self.port}\n
                        user = {self.user}\n
                        pwd = {self.pwd}\n
                        dbname = {self.dbname}\n
                    )   
                '''
    def __del__(self):
        self.close()

    def close(self):
        if self.conn is None:
            return
        self.conn.close()
        self.conn = None

    # For actions that will change the database.
    def execute(self, query, ignore_notable=False, need_rowid=False, need_affected_rows=False):
        if self.conn is None:
            return False

        cursor = self.cursor()
        try:
            cursor.execute(query)
        except Error as err:
            # print(traceback.format_exc())
            if err.errno != errorcode.ER_NO_SUCH_TABLE or not ignore_notable:
                self.app.log(f"{err}")
            self.last_errno = err.errno
            return False

        # Save lastrowid
        if need_rowid:
            self.last_rowid = cursor.lastrowid

        # Save affected rows
        if need_affected_rows:
            self.affected_rows = cursor.rowcount

        self.conn.commit()
        cursor.close()
        return True

    def fetchone(self, query, ignore_notable=False, func_name='not provided'):
        if self.conn is None:
            return False

        cursor = self.cursor()
        try:
            cursor.execute(query)
        except Error as err:
            # print(traceback.format_exc())
            if err.errno != errorcode.ER_NO_SUCH_TABLE or not ignore_notable:
                self.app.log(f"{err}")
            self.last_errno = err.errno
            return False

        row = cursor.fetchone()
        self.conn.commit()
        cursor.close()
        return row

    def fetchall(self, query, ignore_notable=False):
        if self.conn is None:
            return False

        cursor = self.cursor()
        try:
            cursor.execute(query)
        except Error as err:
            # print(traceback.format_exc())
            if err.errno != errorcode.ER_NO_SUCH_TABLE or not ignore_notable:
                self.app.log(f"{err}")
            self.last_errno = err.errno
            return False

        rows = cursor.fetchall()
        self.conn.commit()
        cursor.close()
        return rows

    def cursor(self):
        try:
            return self.conn.cursor(dictionary=True)
        except OperationalError:
            self.conn.reconnect()
            return self.conn.cursor(dictionary=True)
