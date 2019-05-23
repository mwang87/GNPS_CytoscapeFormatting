build:
	docker build -t gnpscytoscape .

build-no-cache:
	docker build --no-cache -t gnpscytoscape .

server:
	docker rm gnpscytoscape || true
	docker run -d -p 5051:5051 --restart=unless-stopped --memory=20G --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh

interactive:
	docker run -it -p 5051:5051 --memory=20G --rm --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh

attach:
	docker exec -i -t gnpscytoscape  /bin/bash
