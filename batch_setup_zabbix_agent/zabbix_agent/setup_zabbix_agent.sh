#/bin/bash
# zabbix server的IP
ServerIP="10.180.100.100"

# 安装 zabbix agent
rpm -ivh zabbix-agent-4.2.1-1.el7.x86_64.rpm

# 配置
sed -i "s/Server=127.0.0.1/Server=$ServerIP/" /etc/zabbix/zabbix_agentd.conf
sed -i "s/ServerActive=127.0.0.1/ServerActive=$ServerIP/" /etc/zabbix/zabbix_agentd.conf
sed -i "s/Hostname=Zabbix server/Hostname=$HOSTNAME/" /etc/zabbix/zabbix_agentd.conf

# 设置磁盘IO监控
cat diskIO.txt >> /etc/zabbix/zabbix_agentd.conf
cp disk_scan.sh /etc/zabbix/zabbix_agentd.d/
chmod 777 /etc/zabbix/zabbix_agentd.d/disk_scan.sh
nohup iostat -m -x -d 30 >> /tmp/iostat_output &

# 关闭防火墙
systemctl stop firewalld
systemctl disable firewalld

# 启动zabbix agent
systemctl start zabbix-agent
systemctl enable zabbix-agent
systemctl status zabbix-agent
netstat -nltp | grep zabbix
