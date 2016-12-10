job "mongo" {
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
      sticky  = true
    }

    task "mongo" {
      driver = "docker"

      config {
        image = "registry.getnoc.com/infrastructure/mongo:master"
        port_map {
          mongodb = 27017
        }
        dns_servers = ["192.168.1.46"]
      }
      resources {
        cpu    = 500 # 500 MHz
        memory = 1500 # 256MB
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
      template {
        data          = <<EOH
        ---
        storage:
          dbPath: /local
          journal:
            enabled: true
          engine: wiredTiger
          wiredTiger:
            engineConfig:
              directoryForIndexes: true
        EOH
        destination   = "/data/configdb/mongod.conf"
      }
      service {
        name = "mongo"
        tags = ["global", "mongo"]
        port = "mongodb"
      }
    }
  }
}
