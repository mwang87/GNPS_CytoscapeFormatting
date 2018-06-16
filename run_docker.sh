docker rm gnpscytoscape
docker run -d -p 5050:5050 --name gnpscytoscape gnpscytoscape /app/run_server.sh
