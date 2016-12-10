job "noc_web" {
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

  group "web" {

    count = 1

    restart {
      attempts = 10
      interval = "5m"
      delay = "25s"
      mode = "delay"
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
