docker rm gnpscytoscape
docker run -d -p 5051:5051 -p 1234:1234 --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh
#docker run -p 5051:5051 -p 1234:1234 --name gnpscytoscape gnpscytoscape /app/run_server_in_docker.sh
