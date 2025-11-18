#!/bin/bash

# 数据库连接参数
DB_HOST="aws-1-ap-southeast-1.pooler.supabase.com"
DB_PORT="6543"
DB_USER="postgres.emxqlkorzbrkdwkugfvm"
DB_NAME="postgres"
export PGPASSWORD="XUZcMFN5qfCNnKgN"

# 执行简单查询
/usr/pgsql-15/bin/psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1

# 记录执行
echo "Database keep-alive executed at: $(date)" >> /var/log/supabase.log
