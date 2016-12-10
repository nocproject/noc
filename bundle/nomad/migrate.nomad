job "migrate" {
  region = "global"

  datacenters = ["dc1"]

  type = "batch"

  constraint {
    attribute = "${attr.kernel.name}"
    value     = "linux"
  }

  group "migrate" {

    count = 1

    task "migrate" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/noc/noc-docker:dev"
        port_map {
          postgresdb = 5432
        }
        command = "/opt/noc/bundle/scripts/migrate.sh"
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
        "NOC_CONFIG"="consul://192.168.1.46/noc"
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
