# Makefile for local Docker Compose + kind Kubernetes workflow
# Usage:
#   make k8s-up
#   make fe-redeploy
#   make be-redeploy
#   make status

SHELL := /bin/bash

# ---- Config (adjust if your names differ) ----
NAMESPACE ?= sidequests
CLUSTER    ?= sidequests

FRONTEND_DIR ?= ./frontend
BACKEND_DIR  ?= ./backend

FRONTEND_IMAGE ?= sidequests-frontend:local
BACKEND_IMAGE  ?= sidequests-backend:local

FRONTEND_DOCKERFILE ?= $(FRONTEND_DIR)/Dockerfile.prod
BACKEND_DOCKERFILE  ?= $(BACKEND_DIR)/Dockerfile.prod

# Build-time Vite API base (used in Dockerfile.prod via ARG/ENV)
VITE_API_URL ?= /api

# K8s manifests folder
K8S_DIR ?= ./k8s

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
	@echo "  k8s-apply         Apply all Kubernetes manifests in ./k8s"
	@echo "  k8s-up            Build images, load into kind, apply manifests, restart fe/be"
	@echo "  k8s-down          Delete namespace (removes app resources)"
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
.PHONY: k8s-apply
k8s-apply:
	kubectl apply -f $(K8S_DIR)

# ---- Restarts (needed when image tag stays the same) ----
.PHONY: fe-restart be-restart restart
fe-restart:
	kubectl -n $(NAMESPACE) rollout restart deployment/frontend
	kubectl -n $(NAMESPACE) rollout status deployment/frontend

be-restart:
	kubectl -n $(NAMESPACE) rollout restart deployment/backend
	kubectl -n $(NAMESPACE) rollout status deployment/backend

restart: fe-restart be-restart

# ---- Redeploy shortcuts ----
.PHONY: fe-redeploy be-redeploy
fe-redeploy: fe-build fe-load fe-restart

be-redeploy: be-build be-load be-restart

# ---- Full local k8s bring-up ----
.PHONY: k8s-up
k8s-up: fe-build be-build load k8s-apply restart
	@echo ""
	@echo "Done. Open: http://app.localtest.me"
	@echo "(If ingress isn't ready yet, wait a few seconds and retry.)"

# ---- Tear down app resources (keeps cluster) ----
.PHONY: k8s-down
k8s-down:
	kubectl delete namespace $(NAMESPACE) --ignore-not-found=true

# ---- Status + logs ----
.PHONY: status logs-fe logs-be
status:
	@echo "Namespace: $(NAMESPACE)"
	kubectl -n $(NAMESPACE) get pods,svc,ingress

logs-fe:
	kubectl -n $(NAMESPACE) logs deployment/frontend -f --tail=200

logs-be:
	kubectl -n $(NAMESPACE) logs deployment/backend -f --tail=200