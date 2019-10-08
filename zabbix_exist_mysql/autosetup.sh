#/bin/bash
#zabbix数据库密码
DPassword="Zabbix-123"
shellFolder=$(dirname $(readlink -f "$0"))
rpm -iUvh --test --force ./packages/* > $shellFolder/error 2>&1
if [ $? -ne '0' ]; then
 cat $shellFolder/error
 exit 1
fi
echo "rpm test success"
rpm -iUvh --force ./packages/*
# service mariadb restart
mysql -uroot -p$1 -e "create database zabbix character set utf8 collate utf8_bin;"
mysql -uroot -p$1 -e "grant all privileges on zabbix.* to'zabbix'@'localhost' identified by '$DPassword';"
mysql -uroot -p$1 -e "grant all privileges on zabbix.* to'zabbix'@'%' identified by '$DPassword';"
mysql -uroot -p$1 -e "flush privileges;"
#![]
chmod 766 /usr/share/doc/zabbix-server-mysql-*/create.sql.gz
zcat /usr/share/doc/zabbix-server-mysql-*/create.sql.gz | mysql -h 127.0.0.1 -uzabbix -p$DPassword zabbix;
setenforce 0
service firewalld stop
chkconfig firewalld off
#![cp /etc/zabbix/zabbix_server.conf]
#![cp /etc/zabbix/zabbix_agentd.conf]
#![cp /etc/zabbix/web/zabbix.conf.php]
sed -i "/# DBHost=localhost/s/# DBHost=localhost/DBHost=localhost/" /etc/zabbix/zabbix_server.conf
sed -i "/# DBPassword=/s/# DBPassword=/DBPassword=$DPassword/" /etc/zabbix/zabbix_server.conf
sed -i "/# DBPort=/s/# DBPort=/DBPort=3306/" /etc/zabbix/zabbix_server.conf
sed -i "/# ListenIP=127.0.0.1/s/# ListenIP=127.0.0.1/ListenIP=0.0.0.0/" /etc/zabbix/zabbix_server.conf
sed -i "/# JavaGateway=/s/# JavaGateway=/JavaGateway=127.0.0.1/" /etc/zabbix/zabbix_server.conf
sed -i "/# JavaGatewayPort=10052/s/# JavaGatewayPort=10052/JavaGatewayPort=10052/" /etc/zabbix/zabbix_server.conf
sed -i "/# StartJavaPollers=0/s/# StartJavaPollers=0/StartJavaPollers=5/" /etc/zabbix/zabbix_server.conf
\cp ./zabbix.conf /etc/httpd/conf.d/zabbix.conf
sed -i "/SELINUX=enforcing/s/SELINUX=enforcing/SELINUX=disabled/" /etc/selinux/config
\cp ./zabbix.conf.php /etc/zabbix/web/
sed -i "/123.com/s/123.com/$DPassword/" /etc/zabbix/web/zabbix.conf.php
\cp ./simkai.ttf /usr/share/zabbix/fonts/
sed -i "/ZBX_GRAPH_FONT_NAME/s/graphfont/simkai/" /usr/share/zabbix/include/defines.inc.php
sed -i "/ZBX_FONT_NAME/s/graphfont/simkai/" /usr/share/zabbix/include/defines.inc.php
\cp ./snmptrap/zabbix_trap_receiver.pl /usr/bin/
chmod a+x /usr/bin/zabbix_trap_receiver.pl
sed -i "/# authCommunity   log,execute,net public/s/# authCommunity   log,execute,net public/authCommunity   log,execute,net public/" /etc/snmp/snmptrapd.conf
sed -i "/zabbix_trap_receiver.pl/d" /etc/snmp/snmptrapd.conf
echo "perl do \"/usr/bin/zabbix_trap_receiver.pl\"" >> /etc/snmp/snmptrapd.conf
sed -i "/# SNMPTrapperFile=\/tmp\/zabbix_traps.tmp/s/# SNMPTrapperFile=\/tmp\/zabbix_traps.tmp/SNMPTrapperFile=\/tmp\/zabbix_traps.tmp/" /etc/zabbix/zabbix_server.conf
sed -i "/^SNMPTrapperFile=\/var\/log\/snmptrap\/snmptrap.log/s/SNMPTrapperFile=\/var\/log\/snmptrap\/snmptrap.log/# SNMPTrapperFile=\/var\/log\/snmptrap\/snmptrap.log/" /etc/zabbix/zabbix_server.conf
sed -i "/# StartSNMPTrapper=0/s/# StartSNMPTrapper=0/StartSNMPTrapper=1/" /etc/zabbix/zabbix_server.conf
#![]
systemctl start zabbix-server
systemctl enable zabbix-server
systemctl start zabbix-agent
systemctl enable zabbix-agent
systemctl start zabbix-java-gateway
systemctl enable zabbix-java-gateway
systemctl start zabbix-proxy
systemctl enable zabbix-proxy
systemctl start httpd
systemctl enable httpd
systemctl enable mariadb
unzip -o ./grafana/alexanderzobnin-grafana-zabbix-*.zip -d /var/lib/grafana/plugins
systemctl daemon-reload
systemctl restart grafana-server
systemctl status grafana-server
systemctl enable grafana-server.service
systemctl start snmptrapd
systemctl enable snmptrapd
netstat -nltp | grep zabbix
