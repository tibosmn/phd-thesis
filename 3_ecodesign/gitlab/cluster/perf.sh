#!/bin/bash
TOKEN="i-am-a-token123"
DOMAIN=some.domain
IP=127.0.0.1
export LC_NUMERIC="en_US.UTF-8" # Set float with . rather than ,
for var in "$@"
do
	rps=$(echo "$var * 20" | bc -l)
	#Replace floating point in rps by _
	filename=60s_${rps/"."/"_"}rps.json
	# Remove decimals
	rps=$(printf "%.0f" $rps)
	cp performance/k6/config/options/60s_10rps.json performance/k6/config/options/${filename}
	# Replace requests per second
	sed -i "s/10/$rps/g" performance/k6/config/options/${filename}
	# Lower test duration
	#sed -i "s/50/10/g" performance/k6/config/options/${filename}
	echo "============================================================================"
	echo "Launching perf test with $rps rps"
        docker run -e\
                ACCESS_TOKEN=$TOKEN\
				-e K6_INFLUXDB_OUTPUT=http://influxdb.monitoring\
				-v /etc/ssl/certs/:/etc/ssl/certs/\
                -v $PWD/performance/k6/config:/config\
                -v $PWD/results:/results\
                --network="host"\
                --add-host="gitlab.$DOMAIN kas.$DOMAIN registry.$DOMAIN minio.$DOMAIN":$IP \
                gitlab/gitlab-performance-tool\
                --environment test.json \
				--options ${filename}\
                --influxdb-url http://influxdb.monitoring/k6
	echo "============================================================================="
	echo "Done $var sleeping 15"
	sleep 15m
done
