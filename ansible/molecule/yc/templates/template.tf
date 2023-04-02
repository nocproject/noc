terraform {
  required_providers {
    yandex = {
      source = "terraform-registry.storage.yandexcloud.net/yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token     = "{{ molecule_yml.driver.token }}"
  cloud_id  = "{{ molecule_yml.driver.cloud_id }}"
  folder_id = "{{ molecule_yml.driver.folder_id }}"
  zone      = "{{ molecule_yml.driver.zone }}"
}

resource "yandex_compute_instance" "vm-1" {
  name = "noc-node-{{ item.distr }}-{{ lookup('env','CI_JOB_ID') | default(60|random,true) }}"

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
      image_id = "{{ molecule_yml.driver.image_id }}"
      size     = 20
    }
  }

  network_interface {
    subnet_id = "{{ molecule_yml.driver.subnet_id }}"
    nat       = true
  }

  metadata = {
    serial-port-enable = 1,
    user-data = "#cloud-config\nusers:\n  - name: redos\n    groups: sudo\n    shell: /bin/bash\n    sudo: ['ALL=(ALL) NOPASSWD:ALL']\n    ssh-authorized-keys:\n      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCaNNNqSmM3d36JU1k5Iu+KE3+g7Obfpcl6xvpui0VDpYMlNHXb2Z6v8G/lIJvUrnD3mJhKGORw2D0s5yJBFbw5tHeNoeCFHeEtJhsP1U9h2JBLdsjx75aFDbvPR3h3R+xI8u1ZbEuFUMmJgGd7Zw7XUp6obJ0TdkTJigKUgsMWcob3jvsHy40KZCq4rKUBcwCddKQrQQjv94a2k5TbZHvkteYwQx+uJnxETv3kjtOQHtgeJbDsvpTqk0K8r3B7Bk5Pkd1RXEqROj0iKbKw4w4Zbpbz3FYbjO82DEUvO69ju+4BOR2Ci1WGWDmVppMDpHPVy+upwxHWa8n+GzN8yshAMmn1gQd/VPeP9KtW+ElHDVn8gFWHENAnyPOU90bJpcnz+uXBcmLYabV5/1iiq8z1im79T5Jb8WzAPF7w9NCE8YqaET07/+kswcflEZ9hkkHD9A4EoC8ZScLs7ey4VMXFicB9DhLE/mozq9Lq3Iwk2fc2oYePiLtG1kuXMfrRYMc= yuriy@jh"
  }

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
