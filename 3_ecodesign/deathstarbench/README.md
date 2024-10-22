# Death Star Benchmark

Deploy DeathStarBench Social Network application ([link](https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation))

## Prerequisites

The following packages `git apt-transport-https git make jq ca-certificates curl gnupg libssl-dev lua-socket luarocks`

luasocket (`sudo luarocks install luasocket`)

[k3d](https://k3d.io/v5.5.1/)

```bash
wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
```

[Helm](https://helm.sh/)

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

[Git LFS](https://git-lfs.com/)

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
```

## Deploy app

```bash
make install
```

Retrieve the cluster IP using `kubectl get svc traefik -n kube-system | awk '{print $4}'`, then add the following entry to `/etc/hosts`

```bash
<IP> social.kubernetes grafana.kubernetes jaeger.kubernetes prometheus.kubernetes influxdb.kubernetes
```

## Grafana

Access at http://grafana.kubernetes

- Login: `admin`
- Password: `prom-operator`

### InfluxDB source

Add the following InfluxDB data source:

- Query Language: Flux
- URL: http://influxdb-influxdb2.powerapi.svc.cluster.local
- Deactivate Basic Auth
- Organization: influxdata
- Token: influxdbtoken
- Default bucket: power_consumption

To access Influx web interface, logins are:

- Login: admin
- Password: influxdpwd

Example Flux request:

```Flux
from(bucket: "power_consumption")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "power_consumption")
  |> filter(fn: (r) => r["_field"] == "power")
  |> filter(fn: (r) => r["sensor"] == "hwpc")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

## Workload

### Setup

It is necessary to build the workload generator tool. Thus, please assert that:

1. Your repository was cloned using `--recurse-submodules` or you pulled the submodules after the clone using `git submodule update --init --recursive`
2. You have the "luajit", "luasocket", "libssl-dev" and "make" packages installed.
3. You are not running inside arm

With the dependencies fulfilled, you can run:

```bash
# There are two wrk2 folders: one in the root of the repository and one inside the socialNetwork folder. This is the first one.
cd DeathStarBench/wrk2
# Compile
make
```

And then go back to the socialNetwork folder to run the wrk2 properly for the system.

```bash
# Back to socialNetwork, in the root folder.
cd DeathStarBench/socialNetwork
```

### Run tests

To launch performance tests, launch from socialNetwork

```bash
../wrk2/wrk -D exp -t 100 -c 100 -d 1m -L -s ./wrk2/scripts/social-network/compose-post.lua http://social.kubernetes/wrk2-api/post/compose -R 10000
```

The parameters are:

- `--dist exp`: Probability distribution
- `-t 100`: number of threads
- `-c 100`: number of connections
- `-d 1m`: test duration
- `--latency`: print overall latency
- `--script`: specify test script, hotel one in our case
- `--rate 1000`: Requests per second
- `--requests`: Print the number of sent requests

# Data

We use python to retrieve and explore the data.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```