terraform {
  required_providers {
    yandex = {
      source = "terraform-providers/yandex"
    }
  }
}

provider "yandex" {
  token     = "t1.9euelZqez53Gy4nIk46XlIuXy5uWm-3rnpWal8_JmJGMjM2VjM2Yx4_Pm4_l8_dmNk1v-e9QT3lt_d3z9yZlSm_571BPeW39.Ug08CTSc1Y7CEWt4s-gvkB3IVGL5n5GjNjWH59uW51v0o6q9AzgP5tdEi2FpZHCEkV0B7C6fAQHdMSye507vCw"
  cloud_id  = "b1gi9isncdv608aunpod"
  folder_id = "b1gupte6966brgu87rp5"
  zone      = "ru-central1-a"
}

resource "yandex_compute_instance" "vm-1" {
  name = "noc-node-centos7-57"

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
      image_id = "fd8qtvk4h4eqqn6i658b"
      size     = 20
    }
  }

  network_interface {
    subnet_id = "e9bbooro15b4mahufr34"
    nat       = true
  }

  metadata = {
    ssh-keys = "centos:${file("/tmp/temporary_ssh_key_pub")}",
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
