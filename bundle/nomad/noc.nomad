job "noc" {
  region = "global"

  datacenters = ["dc1"]

  type = "service"

  constraint {
    attribute = "${attr.kernel.name}"
    value     = "linux"
  }

  update {
    stagger = "10s"

    max_parallel = 1
  }

  group "mongo" {

    count = 1

    restart {
      attempts = 10
      interval = "5m"
      delay = "25s"
      mode = "delay"
    }

    ephemeral_disk {
      size = 300
    }

    task "mongo" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/infrastructure/mongo:master"
        port_map {
          mongodb = 27017
        }
        logging {
          type = "journald"
        }
        volumes = [
          "/home/shirokih/projects/noc_data/mongo:/data/db",
          "/home/shirokih/projects/noc/bundle/config/mongo:/data/configdb"
          ]
        dns_servers = ["192.168.1.46"]
      }
      resources {
        cpu    = 500 # 500 MHz
        memory = 200 # 256MB
        network {
          mbits = 1
          port "mongodb" {
            static = 27017
          }
        }
      }

      env {
        "NOC_CONFIG"= "consul://192.168.1.46/noc"
      }
      constraint {
        attribute = "${node.class}"
        value = "db"
      }
      service {
        name = "mongo"
        tags = ["global", "mongo"]
        port = "mongodb"
        check {
          name     = "alive"
          type     = "tcp"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
  group "postgres" {

    count = 1

    restart {
      attempts = 1
      interval = "5m"
      delay = "25s"
      mode = "delay"
    }

    ephemeral_disk {
      size = 300
    }

    task "postgres" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/infrastructure/postgres:master"
        port_map {
          postgresdb = 5432
        }
        logging {
          type = "journald"
        }
        volumes = [
          "/home/shirokih/projects/noc_data/postgres:/var/lib/postgresql/data",
          "/home/shirokih/projects/noc/bundle/scripts/postgres_init.sh:/docker-entrypoint-initdb.d/init-user-db.sh"
        ]
        dns_servers = ["192.168.1.46"]
      }
      resources {
        cpu    = 500 # 500 MHz
        memory = 256 # 256MB
        network {
          mbits = 1
          port "postgresdb" {
            static = 5432
          }
        }
      }
      env {
        "NOC_CONFIG"= "consul://192.168.1.46/noc"
        "NOC_PG_DB"="noc"
        "NOC_PG_USER"="noc"
        "NOC_PG_PASSWORD"="noc"
        "LC_ALL"= "C.UTF-8"
      }
      constraint {
        attribute = "${node.class}"
        value = "db"
      }
      service {
        name = "postgres"
        tags = ["global", "postgres"]
        port = "postgresdb"
        check {
          name     = "alive"
          type     = "tcp"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
  group "web" {

    count = 1

    restart {
      attempts = 10
      interval = "5m"
      delay = "25s"
      mode = "delay"
    }

    ephemeral_disk {
      size = 300
    }

    task "web" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/noc/noc-docker:master"
        port_map {
          web = 1200
        }
        command = "/usr/bin/python"
        args = ["/opt/noc/services/web/service.py"]
        volumes = [
          "/home/shirokih/projects/noc/:/opt/noc"
        ]
        work_dir = "/opt/noc"
        logging {
          type = "journald"
        }
        dns_servers = ["192.168.1.46"]
      }
      resources {
        cpu    = 500 # 500 MHz
        memory = 256 # 256MB
        network {
          mbits = 10
          port "web" {}
        }
      }
      env {
        "NOC_CONFIG"= "consul://192.168.1.46/noc/"
      }
      service {
        name = "web"
        tags = ["global", "web"]
        port = "web"
        check {
          name     = "alive"
          type     = "http"
          path     = "/mon/"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
