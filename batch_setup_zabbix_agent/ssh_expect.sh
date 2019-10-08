#!/usr/bin/expect
set timeout 30
set host [lindex $argv 0]
set password [lindex $argv 1]
spawn ssh $host
expect "password:"
send "$password\n"

expect "*#"
send "cd /tmp/zabbix_agent\n"

expect "*#"
send "nohup sh setup_zabbix_agent.sh > log_setup_zabbix_agent.txt 2>&1 &\n"

expect "*#"
send "exit\n"

interact


