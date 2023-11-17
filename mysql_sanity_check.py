import mysql.connector
from mysql.connector import pooling
import json

with open('config/app.json') as f:
    app_cfg = json.load(f)
dbname = "llm_account"
# MySQL 数据库连接配置
db_config = {
    "host": app_cfg["db_account_host"],        # 数据库主机
    "user": 'root',    # 数据库用户名
    "password": "",  # 数据库密码
    "database": dbname,  # 数据库名
    "charset": 'utf8'
}

try:
    # 连接到 MySQL 数据库
    #connection = mysql.connector.connect(**db_config)
    connection = pooling.MySQLConnectionPool(
                   **db_config 
                ).get_connection()

    if connection.is_connected():
        print("成功连接到 MySQL 数据库")

        # 创建游标对象
        cursor = connection.cursor()

        # SQL query to create a new table
        create_table_query = """
                CREATE TABLE IF NOT EXISTS your_table_name (
                    column1 INT,
                    column2 INT,

                    PRIMARY KEY (column1)
                )
                """
        # Execute the table creation query
        cursor.execute(create_table_query)

        # 执行一个查询示例
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()
        print(f"MySQL 版本: {db_version[0]}")

        query = f""" SELECT `npcpair` FROM `find_npc_id` WHERE `hashid`=137557 """ 
        row = cursor.execute(query)
        row = cursor.fetchone()
        print(row)

        # 执行一个插入示例
        insert_query = "INSERT INTO find_user_id (hashid, userpair ) VALUES (%s, %s)"
        data_to_insert = (5 , 'testplayer1')
        cursor.execute(insert_query, data_to_insert)
        connection.commit()
        print("数据插入成功")

except mysql.connector.Error as error:
    print(f"连接到 MySQL 数据库时发生错误: {error}")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("数据库连接已关闭")

