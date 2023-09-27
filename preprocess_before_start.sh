#!/bin/bash

# Remove the app.json file
rm -rf snapshot/app.json

# MySQL commands
mysql <<EOF
DROP DATABASE IF EXISTS llm_account;
DROP DATABASE IF EXISTS llm_game0001;

CREATE DATABASE llm_game0001 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE llm_account DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

