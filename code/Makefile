build:
	docker build -t gnpscytoscape .

build-no-cache:
	docker build --no-cache -t gnpscytoscape .

bash:
	docker run -it -p 5051:5051 -v $(PWD)/static:/app/static --memory=20G --rm --name gnpscytoscape gnpscytoscape /bin/bash

server:
	docker rm gnpscytoscape || true
	docker run -d -p 5051:5051 -v $(PWD)/static:/app/static --restart=unless-stopped --memory=20G --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh

interactive:
	docker run -it -p 5051:5051 -v $(PWD)/static:/app/static --memory=20G --rm --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh


server-compose-build:
	docker-compose build

	
server-compose-interactive:
	docker-compose --compatibility build
	docker-compose --compatibility up

server-compose:
	docker-compose --compatibility build
	docker-compose --compatibility up -d

server-compose-production-interactive:
	docker-compose --compatibility build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml --compatibility up

server-compose-production:
	docker-compose --compatibility build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml --compatibility up -d

attach:
	docker exec -i -t gnpscytoscape  /bin/bash

attach-worker:
	docker exec -i -t gnpscytoscape_worker1  /bin/bash