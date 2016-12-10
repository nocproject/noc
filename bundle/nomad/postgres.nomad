job "postgres" {
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
      sticky  = true
    }

    task "postgres" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/infrastructure/postgres:master"
        port_map {
          postgresdb = 5432
        }
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
      }
    }
  }
}
