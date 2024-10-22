#!/usr/bash

install: add-helms clone-repo cluster-create traefik-setup deploy-hotel resource-limits hotel-ingress test-path monitoring-install launch-docker-registry push-powerapi-registry powerapi-install deploy-hwpc deploy-smartwatts

add-helms:
	# Setup helm repositories
	helm repo add influxdata https://helm.influxdata.com/
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update

clone-repo:
	# Clone death star repo if it does not exists
	# Replace consul docker image
	if [ ! -d "DeathStarBench" ] ; then \
		git clone "https://github.com/delimitrou/DeathStarBench.git"; \
		./DeathStarBench/hotelReservation/kubernetes/scripts/build-docker-images.sh \
		# sed -i 's|consul:latest|hashicorp/consul:latest|' DeathStarBench/hotelReservation/kubernetes/consul/consul-deployment.yaml; \
	fi;
	#./DeathStarBench/hotelReservation/kubernetes/scripts/build-docker-images.sh

cluster-create: 
	# Create the k3d registry
	k3d registry delete myregistry.localhost
	k3d registry create myregistry.localhost --port 12345 # name will be krd-myregistry.localhost
	# Delete the old cluster, create a new one
	k3d cluster delete DeathStarBench
	k3d cluster create DeathStarBench \
		-p '80:80@loadbalancer' \
		-p '443:443@loadbalancer' \
		 --registry-use k3d-myregistry.localhost:12345
  		# --registry-config "$$PWD/k3d/k3d-registries.yaml" \

traefik-setup:
	# Install Traefik Resource Definitions for CORS middleware
	kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9.10/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml

	# Install RBAC for Traefik:
	kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v2.9.10/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml

deploy-hotel:
	# Retrieve repo if not already done
	git clone https://github.com/delimitrou/DeathStarBench.git || true # Ignore folder already exists
	cd DeathStarBench && git submodule update --init --recursive # Update depencies
	# Install helm
	helm upgrade --install hotel $$PWD/DeathStarBench/socialNetwork/helm-chart/socialnetwork
	#kubectl apply -Rf $$PWD/DeathStarBench/hotelReservation/kubernetes/

resource-limits:
	helm upgrade --install hotel $$PWD/DeathStarBench/socialNetwork/helm-chart/socialnetwork \
	--set-string global.resources.requests.memory="64Mi" \
	--set-string global.resources.requests.cpu="250m" \
	--set-string global.resources.limits.memory="128Mi" \
	--set-string global.resources.limits.cpu="2"

hotel-ingress:
	# Add ingress routes
	kubectl apply -f $$PWD/social_ingress.yaml

test-path:
	# Update tests with the right url
	sed -i 's|http://localhost:8080|http://social.kubernetes|' \
	./DeathStarBench/socialNetwork/wrk2/scripts/social-network/compose-post.lua

	sed -i 's|http://localhost:8080|http://social.kubernetes|' \
	./DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua

	sed -i 's|http://localhost:8080|http://social.kubernetes|' \
	./DeathStarBench/socialNetwork/wrk2/scripts/social-network/read-home-timeline.lua

	sed -i 's|http://localhost:8080|http://social.kubernetes|' \
	./DeathStarBench/socialNetwork/wrk2/scripts/social-network/read-user-timeline.lua

monitoring-install:	
	# Install influxdb
	# helm upgrade --install influxdb influxdata/influxdb \
	# 	--set image.tag=1.8.0-alpine \
  	# 	--set persistence.enabled=true,persistence.size=50Gi \
	# 	--namespace monitoring --create-namespace

	kubectl create namespace monitoring || true # Ignore namespace already exists

	# Install prometheus and grafana
	helm upgrade --install prometheus-stack \
		prometheus-community/kube-prometheus-stack  \
		--namespace monitoring
	# -f $$PWD/../monitoring_stack/config/monitoring.yaml \

	# Add grafana ingress route
	kubectl apply -f $$PWD/monitoring_stack/grafana_ingress.yaml

	# Add grafana dashboard
	# kubectl -n monitoring apply -f $$PWD/../monitoring_stack/config/dashboard_configmap.yaml

monitoring-remove: 
	helm delete prometheus-stack --namespace monitoring
	helm delete influxdb --namespace monitoring

launch-docker-registry:
	# # We use our own docker registry to use more up-to-date versions than DockerHub ones

	# # Run the registry locally
	# docker stop registry.localhost || true && docker rm registry.localhost || true

	# docker volume create local_registry
	# docker container run -d --name registry.localhost -v local_registry:/var/lib/registry --restart always -p 12345:5000 registry:2
	# docker network connect k3d-DeathStarBench registry.localhost


push-powerapi-registry:
	# hwpc-sensor and smartwatts-formula projects should be in powerapi folder

	# Create links
	rm -rf powerapi/smartwatts-formula/powerapi || true
	cp -r powerapi/powerapi powerapi/smartwatts-formula/powerapi

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
		-f $$PWD/powerapi_helm/influxdb.yaml \
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
