#/bin/bash
shellFolder=$(dirname $(readlink -f "$0"))

cd $shellFolder
unzip -o setuptools-[0-9]*.zip
setuptoolsName=$(ls -d -F setuptools-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $setuptoolsName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf pycparser-[0-9]*.tar.gz
pycparserName=$(ls -d -F pycparser-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $pycparserName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf cffi-[0-9]*.tar.gz
cffiName=$(ls -d -F cffi-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $cffiName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf ipaddress-[0-9]*.tar.gz
ipaddressName=$(ls -d -F ipaddress-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $ipaddressName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
unzip -o enum34-[0-9]*.zip
enum34Name=$(ls -d -F enum34-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $enum34Name
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf six-[0-9]*.tar.gz
sixName=$(ls -d -F six-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $sixName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf asn1crypto-[0-9]*.tar.gz
asn1cryptoName=$(ls -d -F asn1crypto-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $asn1cryptoName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf cryptography-[0-9]*.tar.gz
cryptographyName=$(ls -d -F cryptography-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $cryptographyName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf bcrypt-[0-9]*.tar.gz
bcryptName=$(ls -d -F bcrypt-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $bcryptName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf PyNaCl-[0-9]*.tar.gz
PyNaClName=$(ls -d -F PyNaCl-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $PyNaClName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi

cd $shellFolder
tar -zxvf paramiko-[0-9]*.tar.gz
paramikoName=$(ls -d -F paramiko-[0-9]* | grep '/$' | awk -F '/' '{print $1}')
cd $paramikoName
python setup.py install
if [ $? -ne '0' ]; then
 exit 1
fi