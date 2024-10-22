#!/usr/bash

##########################################################################
# 
# This makefile helps to deploy, populate and performance test a Gitlab
# k3d cluster
#
# Gilab Helm chart doc: https://docs.gitlab.com/charts/
#
##########################################################################

TOKEN="i-am-a-token123"
DOMAIN=some.domain

install: add-helms cluster-create ingress-install traefik-setup gitlab-install monitoring-install push-powerapi-registry powerapi-install deploy-hwpc deploy-smartwatts retrieve-certificate add-certificate create-token

add-helms:
	# Setup helm repositories
	helm repo add influxdata https://helm.influxdata.com/
	# helm repo add gitlab https://charts.gitlab.io/
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

cluster-create:
	# Create the k3d registry
	k3d registry delete myregistry.localhost
	k3d registry create myregistry.localhost --port 12345 # name will be krd-myregistry.localhost

	# Delete the old cluster, create a new one
	# Do not use the traefik ingress provided by k3s by default,
	# we will use the nginx one provided by Gitlab
	k3d cluster delete GitlabLimits
	k3d cluster create GitlabLimits \
		-p '80:80@loadbalancer' \
		-p '443:443@loadbalancer'\
		--k3s-arg "--disable=traefik@server:*"\
		--registry-use k3d-myregistry.localhost:12345

traefik-setup:
	# Install Traefik Resource Definitions for CORS middleware
	kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9.10/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml

	# Install RBAC for Traefik:
	kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9.10/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml

ingress-install:
	# Deploy nginx, as we do not use K3d built-in traefik
	# nor the gitlab included nginx
	# see https://docs.gitlab.com/charts/advanced/external-nginx/
	# We use kubernetes nginx, not official nginx
	helm upgrade --install ingress-nginx ingress-nginx \
		--repo https://kubernetes.github.io/ingress-nginx \
		--namespace ingress-nginx --create-namespace \
		--set tcp.22="gitlab/gitlab-gitlab-shell:22" 
	kubectl apply -f $$PWD/helm-values/nginx-configmap.yaml
	
gitlab-install:
	# Deploy gitlab helm using hel-values.yaml
	# using the DOMAIN var
	# Do not set a static ip, we retrieve it
	# in update-dns target
	#kubectl create secret tls tls-secret-custom --cert=host.cert --key=host.key

	# Update the local helm chart
	# cd gitlab-helm && helm dependency build
	
	helm upgrade --install gitlab ./gitlab-helm \
		--timeout 600s \
		--set global.hosts.domain=$(DOMAIN) \
		-f $$PWD/helm-values/gitlab-helm-values.yaml

gitlab-limits-install:
	# Deploy gitlab helm using hel-values.yaml
	# using the DOMAIN var
	# Do not set a static ip, we retrieve it
	# in update-dns target
	#kubectl create secret tls tls-secret-custom --cert=host.cert --key=host.key

	# Update the local helm chart
	# cd gitlab-helm && helm dependency build
	
	helm upgrade --install gitlab ./gitlab-helm-limits \
		--timeout 600s \
		--set global.hosts.domain=$(DOMAIN) \
		-f $$PWD/helm-values/gitlab-helm-values.yaml

gitlab-remove:
	helm delete gitlab

retrieve-certificate:
	# Retrieve certificate from kubectl
	kubectl get secret gitlab-wildcard-tls-chain -o json \
                | jq -r '.data."gitlab.$(DOMAIN).crt"' \
                | base64 --decode > gitlab.$(DOMAIN).crt
	
	kubectl get secret gitlab-wildcard-tls -o json \
		| jq -r '.data."tls.key"' \
                | base64 --decode > gitlab.$(DOMAIN).key.pem

add-certificate:
	# Adding self-signed certificate to system is mandatory to run perf tools

	# Delete the old certificate 
	sudo rm /etc/ssl/certs/gitlab.some.domain.pem || true
	sudo rm -rf /usr/local/share/ca-certificates/gitlab.$(DOMAIN).* || true
	sudo update-ca-certificates
	
	# Add new certificate 
	sudo cp gitlab.$(DOMAIN).crt /usr/local/share/ca-certificates
	sudo cp gitlab.$(DOMAIN).key.pem /usr/local/share/ca-certificates
	sudo update-ca-certificates

create-token:
	# Create the access token for the root user with all api permissions
	# Find the right pods, then execute rails command
	# Only add the token if it does not exist
	# Find the pod name, wait for it to be ready
	# and then execute token creation
	# If token creation fails due to backend not being ready,
	# sleep 10 secondes then try again
	ERROR=10;\
	until [ $$ERROR -eq 12 ]; do\
		POD_NAME=$$(kubectl get pods -lapp=toolbox -o name);\
		kubectl wait $$POD_NAME --for condition=Ready --timeout=5m;\
		ERROR=$$(kubectl exec -it $$POD_NAME -- /srv/gitlab/bin/rails runner \
			"if PersonalAccessToken.find_by_token('$(TOKEN)').nil?; user = User.find_by_username('root');token=user.personal_access_tokens.create(scopes: ['api','read_user','read_api','read_repository','write_repository','sudo','admin_mode'], name: 'Automation token', expires_at: 365.days.from_now);token.set_token('$(TOKEN)'); token.save!; end; puts '12'");\
		sleep 1;\
		if [ $$ERROR -eq 10 ]; then \
			echo "Backend not ready to create token, sleeping 10 seconds";\
			sleep 10;\
		fi; \
	done

create-data:
	# Clone performance git
	git clone https://gitlab.com/gitlab-org/quality/performance || true
	# Create the generation file from 1k example

	# Delete the old one, ignore error if does not exist
	rm performance/k6/config/environments/test.json || true
	cp performance/k6/config/environments/2k.json \
		performance/k6/config/environments/test.json
	# Replace domain name
	sed -i 's/2k.testbed.gitlab.net/gitlab.some.domain/' \
		performance/k6/config/environments/test.json
	# Replace test name
	sed -i 's/2k/test/' performance/k6/config/environments/test.json

	# Launch data generation with docker
	# Network="host" to reach self-hosted gitlab
	# --force to skip user prompts
	IP=$$(kubectl get ingress -lrelease=gitlab | grep gitlab.$(DOMAIN) | awk '{print $$4}');\
	docker run -e\
		ACCESS_TOKEN=$(TOKEN)\
		-v $$PWD/performance/k6/config:/config\
		-v $$PWD/results:/results\
		--network="host"\
		--add-host="gitlab.some.domain registry.some.domain minio.some.domain":$$IP \
		gitlab/gpt-data-generator\
		--environment test.json --force
		

monitoring-install:	
	# Install influxdb
	helm upgrade --install influxdb influxdata/influxdb \
		-f $$PWD/helm-values/influxdb-values.yaml \
  		--set persistence.enabled=true,persistence.size=500Gi \
		--namespace monitoring --create-namespace

	kubectl create namespace monitoring || true # Ignore namespace already exists

	# Install prometheus and grafana
	helm upgrade --install prometheus-stack \
		-f $$PWD/helm-values/prometheus-stack-helm-values.yaml \
		prometheus-community/kube-prometheus-stack  \
		--namespace monitoring

	# Add grafana ingress route
	kubectl apply -f $$PWD/../monitoring_stack/config/grafana_ingress.yaml

	# Add grafana dashboard
	# kubectl -n monitoring apply -f $$PWD/../monitoring_stack/config/dashboard_configmap.yaml

monitoring-remove: 
	helm delete prometheus-stack --namespace monitoring
	helm delete influxdb --namespace monitoring

push-powerapi-registry:
	# Download projects
	if [ ! -d $$PWD/../monitoring_stack/powerapi/powerapi ] ; then \
		git clone "https://github.com/powerapi-ng/powerapi" $$PWD/../monitoring_stack/powerapi/powerapi; \
		cd $$PWD/../monitoring_stack/powerapi/powerapi && git reset --hard 0a147cb; \
	fi;
	if [ ! -d $$PWD/../monitoring_stack/powerapi/hwpc-sensor ] ; then \
		git clone "https://github.com/powerapi-ng/hwpc-sensor" $$PWD/../monitoring_stack/powerapi/hwpc-sensor; \
		cd $$PWD/../monitoring_stack/powerapi/hwpc-sensor && git reset --hard f8a4510; \
	fi;
	if [ ! -d $$PWD/../monitoring_stack/powerapi/smartwatts-formula ] ; then \
		git clone "https://github.com/powerapi-ng/smartwatts-formula" $$PWD/../monitoring_stack/powerapi/smartwatts-formula; \
		cd $$PWD/../monitoring_stack/powerapi/smartwatts-formula && git reset --hard ff34eda; \
	fi;

	# Create links
	rm -rf $$PWD/../monitoring_stack/powerapi/smartwatts-formula/powerapi || true
	cp -r $$PWD/../monitoring_stack/powerapi/powerapi $$PWD/../monitoring_stack/powerapi/smartwatts-formula/powerapi

	# Push smartwatt to the registry
	docker build --no-cache -t smartwatts-formula $$PWD/../monitoring_stack/powerapi/smartwatts-formula/
	docker tag smartwatts-formula k3d-myregistry.localhost:12345/smartwatts-formula
	docker push k3d-myregistry.localhost:12345/smartwatts-formula

	# Push hwpc-sensor to the registry
	docker build -t hwpc-sensor $$PWD/../monitoring_stack/powerapi/hwpc-sensor/
	docker tag hwpc-sensor k3d-myregistry.localhost:12345/hwpc-sensor
	docker push k3d-myregistry.localhost:12345/hwpc-sensor

powerapi-install:
	# Install influxdb2
	helm upgrade --install influxdb influxdata/influxdb2 \
		--set image.tag=2.7.4-alpine \
		-f $$PWD/../monitoring_stack/powerapi_helm/influxdb.yaml \
		--namespace powerapi --create-namespace

	# Add influx ingress route
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/influx_ingress.yaml
	# Add prometheus ingress route
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/prometheus_ingress.yaml

	# cat ~/.kube/config > kubeconfig.yaml

	# kubectl create namespace powerapi || true # Ignore namespace already exists

	# Deploy mongo database for PowerReports
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/mongo.yaml -n powerapi

deploy-hwpc:
	# Deploy hwpc sensor in a pod
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/hwpc_pod.yaml -n powerapi

deploy-smartwatts:
	# Deploy smartwatt in a pod
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/smartwatts_pod.yaml -n powerapi


reinstall-smartwatt:
	# Delete pod, ignore if not found
	kubectl delete pod smartwatts -n powerapi || true
	kubectl apply -f $$PWD/../monitoring_stack/powerapi_helm/smartwatts_pod.yaml -n powerapi


get-root-password:
	kubectl get secret gitlab-gitlab-initial-root-password -ojsonpath='{.data.password}' | base64 --decode