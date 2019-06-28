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

attach:
	docker exec -i -t gnpscytoscape  /bin/bash
