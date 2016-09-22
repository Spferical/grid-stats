docker network create grid
docker run --name cassandra --net=grid -v /var/lib/cassandra:/var/lib/cassandra -e "CASSANDRA_START_RPC=true" -e "MAX_HEAP_SIZE=64M" -e "HEAP_NEWSIZE=16M" -d cassandra:latest
docker run --name kairosdb -p 8080:8080 -e "CASS_HOSTS=cassandra:9160" --net=grid mesosphere/archlinux-kairosdb:master
