.PHONY: run build add remove qr

run:
	docker compose up \
		--build \
		--force-recreate \
		--remove-orphans

build:
	docker buildx build \
		--no-cache \
		--progress plain \
		--tag housetour .

add: build
	docker run --name housetour-add-tmp housetour poetry add $(package)
	docker cp housetour-add-tmp:/app/backend/pyproject.toml ./backend/pyproject.toml
	docker cp housetour-add-tmp:/app/backend/poetry.lock ./backend/poetry.lock
	docker rm housetour-add-tmp

remove: build
	docker run --name housetour-add-tmp housetour poetry remove $(package)
	docker cp housetour-add-tmp:/app/backend/pyproject.toml ./backend/pyproject.toml
	docker cp housetour-add-tmp:/app/backend/poetry.lock ./backend/poetry.lock
	docker rm housetour-add-tmp

qr:
	docker run -it --rm \
    -e WIFI_SSID=$(WIFI_SSID) \
    -e WIFI_PASSWORD=$(WIFI_PASSWORD) \
	-v $(PWD)/qr_codes:/app/qr_codes \
	-v $(PWD)/backend/qr_codes.py:/app/backend/qr_codes.py \
	-v $(PWD)/backend/area:/app/backend/area \
	-v $(PWD)/data:/app/data \
	housetour poetry run python qr_codes.py wifi=$(wifi)
