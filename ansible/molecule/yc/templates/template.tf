provider "yandex" {
  token     = "{{ molecule_yml.driver.token }}"
  cloud_id  = "{{ molecule_yml.driver.cloud_id }}"
  folder_id = "{{ molecule_yml.driver.folder_id }}"
  zone      = "{{ molecule_yml.driver.zone }}"
}

resource "yandex_compute_instance" "vm-1" {
  name = "noc-node-{{ item.distr }}"

  resources {
    cores         = 4
    memory        = 4
    core_fraction = 100
  }

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
    ssh-keys = "{{ item.ssh_user }}:${file("{{ molecule_yml.driver.ssh_identity_file_pub }}")}"
  }
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface[0].ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface[0].nat_ip_address
}
