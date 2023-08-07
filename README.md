# AgentSims
How to evaluate the ability of large language models (LLM) is an open question after ChatGPT-like LLMs prevailing the community. Existing evaluation methods suffer from following shortcomings: (1) constrained evaluation abilities, (2) vulnerable benchmarks, (3) unobjective metrics. We suggest that task-based evaluation, where LLM agents complete tasks in a simulated environment, is a one-for-all solution to solve above problems. 

We present AgentSims, an easy-to-use infrastructure for researchers from all disciplines to test the specific capacities they are interested in. Researchers can build their evaluation tasks by adding agents and buildings on an interactive GUI or deploy and test new support mechanisms, i.e. memory system and planning system, by a few lines of codes.  

## dependency
```
Python: 3.9.x
MySQL: 8.0.31
```

To use our system, please follow these steps:

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
