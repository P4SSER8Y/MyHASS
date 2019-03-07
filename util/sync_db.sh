#/bin/bash

tmp_db="/tmp/home-assistant-dump.db"
backup_db="$(cd `dirname $0`; pwd)/backup.db"

if [ -f "$tmp_db" ]; then
    rm $tmp_db
fi

cp /tmp/home-assistant.db $tmp_db
sqlite3 $backup_db "ATTACH '$tmp_db' AS src; INSERT OR IGNORE INTO states SELECT * FROM src.states;"
rm $tmp_db

