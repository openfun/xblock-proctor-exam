# Get local user ids
USER_ID          = $(shell id -u)
GROUP_ID         = $(shell id -g)

# Docker
COMPOSE          = USER_ID=$(USER_ID) GROUP_ID=$(GROUP_ID) docker-compose
COMPOSE_RUN      = $(COMPOSE) run --rm
COMPOSE_EXEC     = $(COMPOSE) exec

# Django
MANAGE_LMS       = $(COMPOSE_EXEC) lms dockerize -wait tcp://mysql:3306 -timeout 60s python manage.py lms --settings=fun.docker_run_development
MANAGE_CMS       = $(COMPOSE_EXEC) cms dockerize -wait tcp://mysql:3306 -timeout 60s python manage.py cms --settings=fun.docker_run_development

default: help

bootstrap: tree build dev migrate superuser ## bootstrap the project

build:  ## build the XBlock image
	$(COMPOSE) build lms
.PHONY: build

config/settings.yml:
	cp config/settings.yml.dist config/settings.yml

dev: config/settings.yml  ## start the lms service (and its dependencies)
	$(COMPOSE) up -d cms
.PHONY: dev

down:  ## stop & remove all services
	$(COMPOSE) down
.PHONY: stop

migrate:  ## perform database migrations
	$(MANAGE_LMS) migrate
	$(MANAGE_CMS) migrate
.PHONY: migrate

status:  ## an alias for docker-compose ps
	$(COMPOSE) ps
.PHONY: status

stop:  ## stop running services
	$(COMPOSE) stop
.PHONY: stop

superuser:  ## create openedx superuser
	$(MANAGE_LMS) shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')";
.PHONY: superuser

tree:  ## create data directories mounted as volumes
	bash -c "mkdir -p data/{media,store}"
.PHONY: tree

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
