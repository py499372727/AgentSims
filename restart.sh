#/bin/bash
##echo "kill process provider"
PID=$(ps -ef|grep main.py|grep -v grep|awk '{print $2}')
if [ -z $PID ]; then
	echo "process python server not exist"
else
	echo "process id: $PID"
	kill -9 ${PID}
	echo "process python server killed"
fi
nohup python3 -u main.py > nohup.log 2>&1 &
echo "process python server restarted"
tail -f nohup.log