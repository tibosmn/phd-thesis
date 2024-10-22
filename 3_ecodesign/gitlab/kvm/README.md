# Gitlab install vith vms and linux packages

Following [docs](https://docs.gitlab.com/omnibus/installation/) for a [2000 users architecture](https://docs.gitlab.com/ee/administration/reference_architectures/2k_users.html)

## Setup kvm

```bash
# Install required packages
sudo apt install qemu qemu-kvm libvirt-daemon-system libvirt-clients virt-manager libguestfs-tools xorriso sed curl gpg isolinux

# Setup kvm
# Add libvirt user
sudo usermod -aG kvm $USER
sudo usermod -aG libvirt $USER

# Reboot
sudo reboot
```

## Create ubuntu iso

We create a ubuntu autoinstall iso to ease virtual machines setup.
Login is `ubuntu` and password is `ubuntu`, hostname is `ubuntu-server`.
It contains the host's ssh public key.

```bash
# Create required folders
mkdir isos disks
cd isos
# Download img
wget http://releases.ubuntu.com/20.04/ubuntu-20.04.6-live-server-amd64.iso

# Create the default files
echo '#cloud-config
autoinstall:
  version: 1
  locale: en_US
  identity:
    hostname: ubuntu-server
    password: "$6$exDY1mhS4KUYCE/2$zmn9ToZwTKLhCw.b4/b.ZRTIZM30JZ4QrOQ2aOXJ8yk96xpcCof0kxKwuX1kqLG/ygbJ1f8wxED22bTL4F46P0"
    username: ubuntu
  ssh:
    install-server: yes
    authorized-keys:
      - '$(cat ~/.ssh/id_ed25519.pub) > user-data

touch meta-data

# Generate autoinstall iso
cd ..
bash ubuntu-autoinstall-generator.sh -s ./isos/ubuntu-20.04.6-live-server-amd64.iso -a -k -u ./isos/user-data -m ./isos/meta-data -d ./isos/ubuntu-autoinstall.iso
```

## Create virtual machines

```bash
./create_vm.sh load_balancer 2 1717 && \
./create_vm.sh postgresql 2 7153 && \
./create_vm.sh redis 2 3577 && \
./create_vm.sh gitaly 4 14306 && \
./create_vm.sh rails_1 8 6676 && \
./create_vm.sh rails_2 8 6676 && \
./create_vm.sh monitoring 2 4096 \
./create_vm.sh influx 2 2048
```

Memory is in MiB, Gitlab recommendations are multiplied by 953.67431640625

load_balancer 1.8 GB = 1717 MiB
postgresql 7.5 GB = 7153 MiB
redis 3.75 GB = 3577 MiB
gitaly 15 GB = 14306 MiB
rails_1 7.2 GB = 6676 MiB
rails_2 7.2 GB = 6676 MiB

## Postgresql

[Docs](https://docs.gitlab.com/ee/administration/reference_architectures/2k_users.html#configure-postgresql)

```bash
ssh $(./connect.sh postgresql) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y curl openssh-server ca-certificates tzdata perl
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://gitlab.example.com" apt-get install gitlab-ce=16.2.3-ce.0

# Config file
echo "
# Disable all components except PostgreSQL related ones
roles(['postgres_role'])

# Set the network addresses that the exporters used for monitoring will listen on
node_exporter['listen_address'] = '0.0.0.0:9100'
postgres_exporter['listen_address'] = '0.0.0.0:9187'
postgres_exporter['dbname'] = 'gitlabhq_production'
postgres_exporter['password'] = '14c2e7f093006ac7edf1af9b4fb8cc0d'

# Set the PostgreSQL address and port
postgresql['listen_address'] = '0.0.0.0'
postgresql['port'] = 5432

# Replace POSTGRESQL_PASSWORD_HASH with a md5 'ubuntu
postgresql['sql_user_password'] = '14c2e7f093006ac7edf1af9b4fb8cc0d'

# Replace APPLICATION_SERVER_IP_BLOCK with the CIDR address of the application node
postgresql['trust_auth_cidr_addresses'] = %w(192.168.122.2/24 192.168.122.254/24)

# Prevent database migrations from running on upgrade automatically
gitlab_rails['auto_migrate'] = false
" | sudo tee -a /etc/gitlab/gitlab.rb

# Same secrets for all nodes
TODO

# Reconfigure to load changes
sudo gitlab-ctl reconfigure
```

## Redis

```bash
ssh $(./connect.sh redis) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y curl openssh-server ca-certificates tzdata perl
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://gitlab.example.com" apt-get install gitlab-ce=16.2.3-ce.0

# Config file
echo "
## Enable Redis
roles(['redis_master_role'])

redis['bind'] = '0.0.0.0'
redis['port'] = 6379
redis['password'] = 'redis'

gitlab_rails['enable'] = false

# Set the network addresses that the exporters used for monitoring will listen on
node_exporter['listen_address'] = '0.0.0.0:9100'
redis_exporter['listen_address'] = '0.0.0.0:9121'
redis_exporter['flags'] = {
      'redis.addr' => 'redis://0.0.0.0:6379',
      'redis.password' => 'redis',
}" | sudo tee -a /etc/gitlab/gitlab.rb


# Same secrets for all nodes
sudo vim /etc/gitlab/gitlab-secrets.json

# Reconfigure to load changes
sudo gitlab-ctl reconfigure
```

## Gitaly

```bash
ssh $(./connect.sh gitaly) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y curl openssh-server ca-certificates tzdata perl
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo apt-get install gitlab-ce=16.2.3-ce.0
echo "
   # Avoid running unnecessary services on the Gitaly server
   postgresql['enable'] = false
   redis['enable'] = false
   nginx['enable'] = false
   puma['enable'] = false
   sidekiq['enable'] = false
   gitlab_workhorse['enable'] = false
   prometheus['enable'] = false
   alertmanager['enable'] = false
   grafana['enable'] = false
   gitlab_exporter['enable'] = false
   gitlab_kas['enable'] = false

   # Prevent database migrations from running on upgrade automatically
   gitlab_rails['auto_migrate'] = false

   # Configure the gitlab-shell API callback URL. Without this, `git push` will
   # fail. This can be your 'front door' GitLab URL or an internal load
   # balancer.
   gitlab_rails['internal_api_url'] = 'http://gitlab.example.com'

   # Gitaly
   gitaly['enable'] = true

   # The secret token is used for authentication callbacks from Gitaly to the GitLab internal API.
   # This must match the respective value in GitLab Rails application setup.
   gitlab_shell['secret_token'] = 'shellsecret'

   # Set the network addresses that the exporters used for monitoring will listen on
   node_exporter['listen_address'] = '0.0.0.0:9100'

   gitaly['configuration'] = {
      # ...
      #
      # Make Gitaly accept connections on all network interfaces. You must use
      # firewalls to restrict access to this address/port.
      # Comment out following line if you only want to support TLS connections
      listen_addr: '0.0.0.0:8075',
      prometheus_listen_addr: '0.0.0.0:9236',
      # Gitaly Auth Token
      # Should be the same as praefect_internal_token
      auth: {
         # ...
         #
         # Gitaly's authentication token is used to authenticate gRPC requests to Gitaly. This must match
         # the respective value in GitLab Rails application setup.
         token: 'gitalysecret',
      },
      # Gitaly Pack-objects cache
      # Recommended to be enabled for improved performance but can notably increase disk I/O
      # Refer to https://docs.gitlab.com/ee/administration/gitaly/configure_gitaly.html#pack-objects-cache for more info
      pack_objects_cache: {
         # ...
         enabled: true,
      },
      storage: [
         {
            name: 'default',
            path: '/var/opt/gitlab/git-data',
         },
      ],
   }
" | sudo tee -a /etc/gitlab/gitlab.rb

# Same secrets for all nodes
sudo vim /etc/gitlab/gitlab-secrets.json

# Reconfigure to load changes
sudo gitlab-ctl reconfigure

# Confirm that Gitaly can perform callbacks to the internal API
sudo /opt/gitlab/embedded/bin/gitaly check /var/opt/gitlab/gitaly/config.toml
```

## Rails 1 and 2

````bash
# Retrieve these ip addresses
./connect.sh postgresql
./connect.sh redis
./connect.sh gitaly

# Install gitlab
# Specify which node to
ssh $(./connect.sh rails_<NODE_NUMBER>) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y curl openssh-server ca-certificates tzdata perl
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://gitlab.example.com" apt-get install gitlab-ce=16.2.3-ce.0

# Set the ip address
postgre_ip=<RETRIEVED_POSTGRE_IP>
redis_ip=<RETRIEVED_REDIS_IP>
gitaly_ip=<RETRIEVED_GITALY_IP>

echo "
external_url 'http://gitlab.example.com'

# Gitaly and GitLab use two shared secrets for authentication, one to authenticate gRPC requests
# to Gitaly, and a second for authentication callbacks from GitLab-Shell to the GitLab internal API.
# The following two values must be the same as their respective values
# of the Gitaly setup
gitlab_rails['gitaly_token'] = 'gitalysecret'
gitlab_shell['secret_token'] = 'shellsecret'

git_data_dirs({
  'default' => { 'gitaly_address' => 'tcp://${gitaly_ip}:8075' },
})

## <Disable components that will not be on the GitLab application server
roles(['application_role'])
gitaly['enable'] = false
nginx['enable'] = true

## PostgreSQL connection details
gitlab_rails['db_adapter'] = 'postgresql'
gitlab_rails['db_encoding'] = 'unicode'
gitlab_rails['db_host'] = '${postgre_ip}' # IP/hostname of database server
gitlab_rails['db_password'] = '14c2e7f093006ac7edf1af9b4fb8cc0d'

## Redis connection details
gitlab_rails['redis_port'] = '6379'
gitlab_rails['redis_host'] = '${redis_ip}' # IP/hostname of Redis server
gitlab_rails['redis_password'] = 'redis'

# Set the network addresses that the exporters used for monitoring will listen on
node_exporter['listen_address'] = '0.0.0.0:9100'
gitlab_workhorse['prometheus_listen_addr'] = '0.0.0.0:9229'
puma['listen'] = '0.0.0.0'
sidekiq['listen_address'] = '0.0.0.0'

# Configure Sidekiq with 2 workers and 20 max concurrency
sidekiq['max_concurrency'] = 20
sidekiq['queue_groups'] = ['*'] * 2

# Disable object store
gitlab_rails['object_store']['enabled'] = false
" | sudo tee -a /etc/gitlab/gitlab.rb

# Same secrets for all nodes
sudo vim /etc/gitlab/gitlab-secrets.json

# Reconfigure to load changes
sudo gitlab-ctl reconfigure

# Initialize database
sudo gitlab-rake gitlab:db:configure

# Confirm the node can connect to Gitaly
sudo gitlab-rake gitlab:gitaly:check

# Create the token 'i-am-a-token123' for the root user
# ONLY ON ONE RAILS NODE
# One liner doees not work, need to go into rails console
```bash
sudo gitlab-rails console
user = User.find_by_username('root')
token = user.personal_access_tokens.create(scopes: ['api','read_user','read_api','read_repository','write_repository','sudo','admin_mode'], name: 'Automation token', expires_at: 365.days.from_now)
token.set_token('i-am-a-token123'); token.save!;
```
#PersonalAccessToken.find_by_token('i-am-a-token123').destroy!

# Update the root password
# For example password378 respect rules
sudo gitlab-rake gitlab:password:reset
````

## Load balancer

```bash
# Retrieve gitlab rails servers ip
./connect.sh rails_1
./connect.sh rails_2

#Connect to load balancer_server
ssh $(./connect.sh load_balancer) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y haproxy net-tools

rails_1_ip=<SET_HERE IP RETRIEVED>
rails_2_ip=<SET_HERE IP RETRIEVED>
self_ip=$(ifconfig enp1s0 | grep -w inet | awk '{print $2}')

echo "
frontend frontend-base
  bind ${self_ip}:80
  default_backend    backend-base

backend backend-base
  balance leastconn
  mode http
  server rails_1 ${rails_1_ip}:80 check
  server rails_2 ${rails_2_ip}:80 check
" | sudo tee -a /etc/haproxy/haproxy.cfg

sudo systemctl restart haproxy
sudo systemctl enable haproxy
```

## Monitoring

### Prometheus

```bash
# We need to retrieve all nodes ips
./connect.sh load_balancer
./connect.sh postgresql
./connect.sh redis
./connect.sh gitaly
./connect.sh rails_1
./connect.sh rails_2
./connect.sh monitoring

ssh $(./connect.sh monitoring) -l ubuntu -o StrictHostKeyChecking=no

# Install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER

# Restart vm
sudo reboot now
ssh $(./connect.sh monitoring) -l ubuntu -o StrictHostKeyChecking=no

postgresql_ip=<SET_HERE IP RETRIEVED>
redis_ip=<SET_HERE IP RETRIEVED>
gitaly_ip=<SET_HERE IP RETRIEVED>
rails_1_ip=<SET_HERE IP RETRIEVED>
rails_2_ip=<SET_HERE IP RETRIEVED>

echo "
global:
  scrape_interval:     5s
scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['${postgresql_ip}:9187']
  - job_name: 'redis'
    static_configs:
      - targets: ['${redis_ip}:9121']
  - job_name: 'gitaly'
    static_configs:
      - targets: ['${gitaly_ip}:9236']
  - job_name: 'gitlab-nginx'
    static_configs:
      - targets: ['${rails_1_ip}:8060', '${rails_2_ip}:8060']
  - job_name: 'gitlab-workhorse'
    static_configs:
      - targets: ['${rails_1_ip}:9229', '${rails_2_ip}:9229']
  - job_name: 'gitlab-rails'
    metrics_path: '/-/metrics'
    static_configs:
      - targets: ['${rails_1_ip}:8080', '${rails_2_ip}:8080']
  - job_name: 'gitlab-sidekiq'
    static_configs:
      - targets: ['${rails_1_ip}:8082', '${rails_2_ip}:8082']
  - job_name: 'node'
    static_configs:
      - targets: ['${postgresql_ip}:9100', '${redis_ip}:9100', '${gitaly_ip}:9100', '${rails_1_ip}:9100', '${rails_2_ip}:9100']
" > prometheus.yml

# Create a named volume
docker volume create prom-vol

docker run \
   -p 9090:9090 \
   --volume prom-vol:/prometheus \
   -v ./prometheus.yml:/etc/prometheus/prometheus.yml \
   --network="host"\
   -d \
   --restart always \
   prom/prometheus

# Grafana
docker run \
   -d \
   --restart always \
   --network="host"\
   -p 3000:3000 \
   grafana/grafana
```

```bash

# Install gitlab
ssh $(./connect.sh monitoring) -l ubuntu -o StrictHostKeyChecking=no
sudo su -
apt-get update && apt-get install -y curl openssh-server ca-certificates tzdata perl
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://gitlab.example.com" apt-get install gitlab-ce=16.2.3-ce.0

# Setp ips
postgresql_ip=<SET_HERE IP RETRIEVED>
redis_ip=<SET_HERE IP RETRIEVED>
gitaly_ip=<SET_HERE IP RETRIEVED>
rails_1_ip=<SET_HERE IP RETRIEVED>
rails_2_ip=<SET_HERE IP RETRIEVED>

echo "
roles(['monitoring_role'])

external_url 'http://gitlab.example.com'

# Prometheus
prometheus['listen_address'] = '0.0.0.0:9090'
prometheus['monitor_kubernetes'] = false

# Grafana
grafana['enable'] = true
grafana['admin_password'] = 'grafana'
grafana['disable_login_form'] = true

# Enable futured deprecated grafana
grafana['enable_deprecated_service'] = true

# Nginx - For Grafana access
nginx['enable'] = true

prometheus['scrape_configs'] = [
  {
     'job_name': 'postgres',
     'static_configs' => [
     'targets' => ['${postgresql_ip}:9187'],
     ],
  },
  {
     'job_name': 'redis',
     'static_configs' => [
     'targets' => ['${redis_ip}:9121'],
     ],
  },
  {
     'job_name': 'gitaly',
     'static_configs' => [
     'targets' => ['${gitaly_ip}:9236'],
     ],
  },
  {
     'job_name': 'gitlab-nginx',
     'static_configs' => [
     'targets' => ['${rails_1_ip}:8060', '${rails_2_ip}:8060'],
     ],
  },
  {
     'job_name': 'gitlab-workhorse',
     'static_configs' => [
     'targets' => ['${rails_1_ip}:9229', '${rails_2_ip}:9229'],
     ],
  },
  {
     'job_name': 'gitlab-rails',
     'metrics_path': '/-/metrics',
     'static_configs' => [
     'targets' => ['${rails_1_ip}:8080', '${rails_2_ip}:8080'],
     ],
  },
  {
     'job_name': 'gitlab-sidekiq',
     'static_configs' => [
     'targets' => ['${rails_1_ip}:8082', '${rails_2_ip}:8082'],
     ],
  },
  {
     'job_name': 'node',
     'static_configs' => [
     'targets' => ['${postgresql_ip}:9100', '${redis_ip}:9100', '${gitaly_ip}:9100', '${rails_1_ip}:9100', '${rails_2_ip}:9100'],
     ],
  },
]
" | sudo tee -a /etc/gitlab/gitlab.rb

# Reconfigure to load changes
sudo gitlab-ctl reconfigure

#In the GitLab UI, set admin/application_settings/metrics_and_profiling > Metrics - Grafana to /-/grafana to http[s]://<MONITOR NODE>/-/grafana
```

## Influxdb

```bash
ssh $(./connect.sh influx) -l ubuntu -o StrictHostKeyChecking=no
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list


sudo systemctl enable --now influxdb
sudo influx setup

# login: admin
# passwd: prom-operator
# organization: gitlab
# bucket: gitlab
# retention: 0 (infinite)
```

# Tests setup

Launch data creation

```bash
make create-data
```

To lauch test perf, 192.168.122.107
