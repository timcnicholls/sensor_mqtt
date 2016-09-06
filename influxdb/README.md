Create directories to map volumes:

mkdir -p var/lib/influxdb
mkdir -p etc/influxdb

To generate config file:

$ docker run --rm influxdb influxd config > etc/influxdb/influxdb.conf

To run influxdb server in container with volume persistence for DB and configuration:

$ docker run -d --name=influxdb -p 8083:8083 -p 8086:8086 \
    -v $PWD/etc/influxdb:/etc/influxdb \
    -v $PWD/var/lib/influxdb:/var/lib/influxdb \
    influxdb -config /etc/influxdb/influxdb.conf

(This maps local config and DB runtime volumes for persistence from current dir)

To run client against running server in container:

$ docker run --rm --net=container:influxdb -it influxdb influx

GRAFANA:

docker pull grafana/grafana

mkdir -p var/lib/grafana
mkdir -p etc/grafana

Copied grafana.ini into etc/grafana from Github sample at https://raw.githubusercontent.com/grafana/grafana/master/conf/sample.ini

Edited admin password in config file

To run:

$ docker run -d --name=grafana -p 3000:3000 \
    -v $PWD/etc/grafana:/etc/grafana \
    -v $PWD/var/lib/grafana:/var/lib/grafana grafana/grafana

To back up influxDB running in existing container (e.g. from compose):

docker run --rm \
    -v $PWD/etc/influxdb:/etc/influxdb -v $PWD/var/lib/influxdb:/var/lib/influxdb -v $PWD/tmp/backup:/tmp/backup \
    --link influxdb_influxdb_1 influxdb influxd backup -database mydb -host influxdb_influxdb_1:8088 /tmp/backup

