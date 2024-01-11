echo START
cd docker
docker-compose down # --remove-orphans
cd ..
docker rmi acc-api
docker build . -t acc-api -f docker/Dockerfile #--no-cache
cd docker
./docker_compose.sh
cd ..
echo END
docker logs -f docker_acc-api_1
