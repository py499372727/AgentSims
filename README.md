# AgentSims

## dependency
```
Python: 3.9.x
MySQL: 8.0.31
```

## MySQL Init
```
use mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
flush privileges;

create database `llm_account` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game0001` default character set utf8mb4 collate utf8mb4_unicode_ci;
create database `llm_game0002` default character set utf8mb4 collate utf8mb4_unicode_ci;
```

## Install

```bash
pip install tornado
pip install mysql-connector-python
pip install websockets
pip install openai_async
```

or
```bash
pip install -r requirements.txt
```

## Run

start server:
```bash
./restart.sh
```

start tick:
```bash
python -u tick.py
```
