terraform {
  required_providers {
    yandex = {
      source = "terraform-registry.storage.yandexcloud.net/yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token     = "AQAAAAAHFB-2AATuwf-OOIJbOEiammYR3k50VR4"
  cloud_id  = "b1gi9isncdv608aunpod"
  folder_id = "b1gupte6966brgu87rp5"
  zone      = "ru-central1-a"
}

resource "yandex_compute_instance" "vm-1" {
  name = "noc-node-ubuntu20-19"

  resources {
    cores         = 4
    memory        = 8
    core_fraction = 100
  }

  platform_id = "standard-v2"

  scheduling_policy {
    preemptible = true
  }

  boot_disk {
    initialize_params {
      image_id = "fd8ovo09vrcggmpqjm4v"
      size     = 20
    }
  }

  network_interface {
    subnet_id = "e9bbooro15b4mahufr34"
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("/tmp/temporary_ssh_key_pub")}",
    serial-port-enable = 1  }

  timeouts {
    create = "10m"
    delete = "10m"
  }
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface[0].ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface[0].nat_ip_address
}
