#/bin/bash

src_db="/tmp/home-assistant.db"
backup_db="$(cd `dirname $0`; pwd)/../backup.db"

sqlite3 $src_db "ATTACH '$backup_db' AS src; INSERT OR IGNORE INTO states SELECT * FROM src.states WHERE created >= date('now', '-3 days');"

