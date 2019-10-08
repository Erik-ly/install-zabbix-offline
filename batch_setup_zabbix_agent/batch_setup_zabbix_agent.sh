#/bin/bash

IPList=$(cat ipList.txt)

for ip in $IPList
do
	echo "Setuping $ip"
	
	expect scp_expect.sh $ip root zabbix_agent /tmp/ $1
	expect ssh_expect.sh $ip $1
	
done

exit
