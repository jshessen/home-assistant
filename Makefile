.DEFAULT_GOAL := help
# --------------------------
-include .env
export
# --------------------------
COMPOSE_HASS := -f docker-compose.yml
HASS_SERVICE := homeassistant

COMPOSE_ALL_FILES := ${COMPOSE_HASS}
ALL_SERVICES := ${HASS_SERVICE}

.PHONY: setup plex all up down orphan stop restart rm images update

setup:    ## Build .env from config.d/*.env files
ifdef CLEAN
	@set -a && . ./config.d/hass.env &&	set +a && \
  for f in `find ./config.d -type f -name "*.env" -print 2>/dev/null` ; do set -a && . "$$f" && set +; done && \
  env|sort > .env
else
	@env -i PATH="$$PATH" CLEAN=1 sh -c "make setup"
endif

plex:   ## 'Start' Home Assistant - 'docker-compose ... up -d'
	docker-compose ${COMPOSE_HASS} up -d --build ${HASS_SERVICE}

all:        ## 'Start' Home Assistant, and all applicable components - 'docker-compose ... up -d'
	docker-compose ${COMPOSE_ALL_FILES} up -d --build ${ALL_SERVICES}



up:   ## 'Up' Home Assistant, and all applicable components - 'docker-compose ... up -d'
	@make all

down:   ## 'Down' Home Assistant, and all applicable components - 'docker-compose ... down'
	docker-compose ${COMPOSE_ALL_FILES} down

orphan: ## "Remove 'orphan' containers - 'docker-compose ... --remove-orphans'
	@docker-compose ${COMPOSE_ALL_FILES} down --remove-orphans

stop:			## 'Stop' Home Assistant, and all applicable components - 'docker-compose ... stop'
	@docker-compose ${COMPOSE_ALL_FILES} stop ${ALL_SERVICES}
	
restart:			## 'Restart' Home Assistant, and all applicable components - 'docker-compose ... up -d'
	@docker-compose ${COMPOSE_ALL_FILES} restart ${ALL_SERVICES}

rm:			## 'Remove' Home Assistant, and all applicable components - 'docker-compose ... rm =f'
	@docker-compose ${COMPOSE_ALL_FILES} rm -f ${ALL_SERVICES}

images:			## 'Show' Home Assistant, and all applicable components - 'docker-compose ... images'
	@docker-compose ${COMPOSE_ALL_FILES} images ${ALL_SERVICES}

update:			## 'Update' Home Assistant, and all applicable components - 'docker-compose ... pull/up'
	@docker-compose ${COMPOSE_ALL_FILES} pull
	@make all

# --------------------------
help:       	## Show this 'help'
	@echo "Make Application Docker Images and Containers using Docker-Compose files in 'docker' Dir."
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m (default: help)\n\nTargets:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
