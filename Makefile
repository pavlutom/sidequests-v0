# Makefile for local Docker Compose + kind Kubernetes workflow
# Usage:
#   make k8s-up
#   make fe-redeploy
#   make be-redeploy
#   make status

SHELL := /bin/bash

# ---- Config (adjust if your names differ) ----
HELM_CHART = ./helm/sidequests
HELM_RELEASE = sidequests
NAMESPACE = sidequests
CLUSTER    ?= sidequests

FRONTEND_DIR ?= ./frontend
BACKEND_DIR  ?= ./backend

FRONTEND_IMAGE ?= sidequests-frontend:latest
BACKEND_IMAGE  ?= sidequests-backend:latest

FRONTEND_DOCKERFILE ?= $(FRONTEND_DIR)/Dockerfile.prod
BACKEND_DOCKERFILE  ?= $(BACKEND_DIR)/Dockerfile.prod

# Build-time Vite API base (used in Dockerfile.prod via ARG/ENV)
VITE_API_URL ?= /api

# K8s manifests folder
# K8S_DIR ?= ./k8s # Replaced by HELM_CHART

# ---- Helpers ----
.PHONY: help
help:
	@echo "Targets:"
	@echo "  compose-up        Run docker compose (build + up)"
	@echo "  compose-down      Stop docker compose"
	@echo ""
	@echo "  kind-create       Create kind cluster (expects kind-config.yaml)"
	@echo "  kind-delete       Delete kind cluster"
	@echo ""
	@echo "  k8s-validate      Lints the Helm chart"
	@echo "  k8s-tls           Generate self-signed TLS certs and create k8s secret"
	@echo "  k8s-ingress       Install Nginx Ingress Controller for kind"
	@echo "  k8s-apply         Deploy the application using Helm"
	@echo "  k8s-up            Build, load, and deploy everything (including Ingress)"
	@echo "  k8s-down          Stop workloads (preserves PVCs/Secrets)"
	@echo "  k8s-purge         Delete namespace (removes EVERYTHING including data)"
	@echo ""
	@echo "  fe-build          Build frontend image"
	@echo "  fe-load           Load frontend image into kind"
	@echo "  fe-restart        Restart frontend deployment"
	@echo "  fe-redeploy       Build + load + restart frontend"
	@echo ""
	@echo "  be-build          Build backend image"
	@echo "  be-load           Load backend image into kind"
	@echo "  be-restart        Restart backend deployment"
	@echo "  be-redeploy       Build + load + restart backend"
	@echo ""
	@echo "  status            Show pods/services/ingress"
	@echo "  logs-fe           Tail frontend logs"
	@echo "  logs-be           Tail backend logs"

# ---- Docker Compose ----
.PHONY: compose-up compose-down
compose-up:
	docker compose up --build

compose-down:
	docker compose down

# ---- kind cluster ----
.PHONY: kind-create kind-delete kind-info
kind-create:
	kind create cluster --name $(CLUSTER) --config kind-config.yaml

kind-delete:
	kind delete cluster --name $(CLUSTER)

kind-info:
	kubectl cluster-info --context kind-$(CLUSTER)

# ---- Build images ----
.PHONY: fe-build be-build
fe-build:
	docker build --progress=plain -t $(FRONTEND_IMAGE) \
		-f $(FRONTEND_DOCKERFILE) \
		--build-arg VITE_API_URL=$(VITE_API_URL) \
		$(FRONTEND_DIR)

be-build:
	docker build --progress=plain -t $(BACKEND_IMAGE) \
		-f $(BACKEND_DOCKERFILE) \
		$(BACKEND_DIR)

# ---- Load images into kind ----
.PHONY: fe-load be-load load
fe-load:
	kind load docker-image $(FRONTEND_IMAGE) --name $(CLUSTER)

be-load:
	kind load docker-image $(BACKEND_IMAGE) --name $(CLUSTER)

load: fe-load be-load

# ---- Apply manifests ----
.PHONY: k8s-apply k8s-validate
k8s-validate:
	helm lint $(HELM_CHART)
	helm template $(HELM_RELEASE) $(HELM_CHART) --namespace $(NAMESPACE)

k8s-tls:
	@kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	@if ! kubectl -n $(NAMESPACE) get secret sidequests-tls >/dev/null 2>&1; then \
		echo "Generating self-signed TLS certificates..."; \
		openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
			-keyout /tmp/tls.key -out /tmp/tls.crt \
			-subj "/CN=app.localtest.me"; \
		kubectl -n $(NAMESPACE) create secret tls sidequests-tls \
			--key /tmp/tls.key --cert /tmp/tls.crt; \
		rm /tmp/tls.key /tmp/tls.crt; \
	else \
		echo "TLS secret 'sidequests-tls' already exists."; \
	fi

k8s-ingress:
	@echo "Installing Nginx Ingress Controller..."
	@kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
	@echo "Waiting for Ingress Controller to be ready..."
	@kubectl wait --namespace ingress-nginx \
		--for=condition=ready pod \
		--selector=app.kubernetes.io/component=controller \
		--timeout=90s

k8s-apply:
	helm upgrade --install $(HELM_RELEASE) $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--create-namespace

# ---- Restarts (needed when image tag stays the same) ----
.PHONY: fe-restart be-restart restart
fe-restart:
	kubectl -n $(NAMESPACE) rollout restart deployment/$(HELM_RELEASE)-frontend
	kubectl -n $(NAMESPACE) rollout status deployment/$(HELM_RELEASE)-frontend

be-restart:
	kubectl -n $(NAMESPACE) rollout restart deployment/$(HELM_RELEASE)-backend
	kubectl -n $(NAMESPACE) rollout status deployment/$(HELM_RELEASE)-backend

restart: fe-restart be-restart

# ---- Redeploy shortcuts ----
.PHONY: fe-redeploy be-redeploy
fe-redeploy: fe-build fe-load fe-restart

be-redeploy: be-build be-load be-restart

# ---- Full local k8s bring-up ----
.PHONY: k8s-up
k8s-up: fe-build be-build load k8s-ingress k8s-tls k8s-apply restart
	@echo ""
	@echo "Done. Open: https://app.localtest.me"
	@echo "(If ingress isn't ready yet, wait a few seconds and retry.)"

# ---- Stop app workloads (keeps data/secrets) ----
.PHONY: k8s-stop k8s-down
k8s-down: k8s-stop
k8s-stop:
	kubectl -n $(NAMESPACE) delete deployment,statefulset,hpa,ingress --all --ignore-not-found=true

# ---- Full cleanup (removes everything including data) ----
.PHONY: k8s-purge
k8s-purge:
	-helm uninstall $(HELM_RELEASE) --namespace $(NAMESPACE)
	kubectl delete namespace $(NAMESPACE) --ignore-not-found=true

# ---- Status + logs ----
.PHONY: status logs-fe logs-be
status:
	@echo "Namespace: $(NAMESPACE)"
	kubectl -n $(NAMESPACE) get pods,svc,ingress,hpa,pdb

logs-fe:
	kubectl -n $(NAMESPACE) logs deployment/$(HELM_RELEASE)-frontend -f --tail=200

logs-be:
	kubectl -n $(NAMESPACE) logs deployment/$(HELM_RELEASE)-backend -f --tail=200