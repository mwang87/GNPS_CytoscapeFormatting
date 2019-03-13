build:
	docker build -t gnpscytoscape .

server:
	docker run -d -p 5051:5051 --memory=20G -p 1234:1234 --rm --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh

interactive:
	docker run -it -p 5051:5051 --memory=20G -p 1234:1234 --rm --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh

attach:
	docker exec -i -t gnpscytoscape  /bin/bash
