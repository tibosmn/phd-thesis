# Gitlab cluster deployment and perf tools deployment

Ease the deployment and performance testing of Gitlab helm chart, using [k3d](https://k3d.io/) (k3s running on docker).

Using the [Makefile](Makefile), the Gitlab application can be deployed and testing according to a number of users defined by _USERS_.

## Prerequisites

Before using the [Makefile](Makefile), the following are required:

- make
- [docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- kubectl
- [k3d](https://k3d.io/)

The other requirements can be fulfilled using the make target `install-prerequesites`.

## Setup

When prerequesite are fulfilled, the complete k3d cluster creation, Gitlab helm chart deployment and monitoring setup (grafana, prometheus and influxdb) can be done via:

```bash
make install
```

Retrieve the cluster IP using `kubectl get ingress | awk '{print $4}'`, then add the following entry to `/etc/hosts`

```bash
<IP> gitlab.some.domain registry.some.domain minio.some.domain prometheus.some.domain grafana.some.domain influxdb.some.domain
```

# Grafana

Logins for grafana are `admin` and `prom-operator`

# Performance testing

## Data creation

To run Gitlab performance test, data should be created using:

```bash
make create-data
```

In case token creation failed and it does not work, create it manually:

```bash
# Retrieve the toolbox pod
kubectl get pods -lapp=toolbox
# Open a rails console session
kubectl exec -it <toolbox-pod-name> -- /srv/gitlab/bin/rails console

# Create the token
user = User.find_by_username('root');
token = user.personal_access_tokens.create(scopes: ['api','read_user','read_api','read_repository','write_repository','sudo','admin_mode'], name: 'Automation token', expires_at: 365.days.from_now);
token.set_token('i-am-a-token123'); token.save!;
```

_Note: This is a long process (half an hour for 1k users)_

## Run

With data created, perf tests can be launched using [test.sh](tesh.sh). It takes floats as inputs, representing the thousands of users expected at given time points, ordered by the args order.
For example, for a 4 hours period with 200 user the first hour, 500 the second, a 1000 the third and 3400 the last hour the command would be:

```bash
./test.sh 0.2 0.5 1 3.4
```

# Some helpers commands

> Ce qui est appelé _rps_ par les fichier options de tests k6 sont en réalité de nombre de virtual users

View nginx conf

```bash
kubectl get pods -n ingress-nginx
kubectl exec nginx-nginx-ingress-controller-7fc8d47549-nfqmz -n ingress-nginx -- nginx -T
```

Retrieve gitlab password

```bash
make get-root-password
```

To correct _Import failed with 413 Request Entity Too Large error_ as we use the [official NGINX Ingress](https://docs.nginx.com/nginx-ingress-controller/configuration/ingress-resources/advanced-configuration-with-annotations/) and not the [the official Kubernetes Ingress based on NGINX](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#custom-max-body-size), the correct annotation to avoid error is `nginx.org/client-max-body-size: "0"` and NOT `nginx.ingress.kubernetes.io/proxy-body-size` as explained in [Gitlab doc](https://gitlab.com/gitlab-org/quality/performance/-/blob/main/docs/environment_prep.md#import-failed-with-413-request-entity-too-large-error).

# Test using two machines

Using **host** as the machine running gitlab, and **test** as the machine running the tests.

- Retrieve the local ip from **host**, which we consider as `$HOST_IP`
- Generate the certificate from **host** using `make retrieve-certificate`
- Copy `gitlab.some.domain.crt` and `gitlab.some.domain.key.pem` from **host** to **test** in app folder
- On **test**, run `make add-certificate`
- On **test**, map to `HOST_IP` the following in `/etc/hosts`: `gitlab.some.domain registry.some.domain minio.some.domain`
