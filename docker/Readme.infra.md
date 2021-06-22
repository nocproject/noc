Infrastructure FAQ:
----
Q: What is `docker-compose-infra.yml`?

A: These are several services that collect and visualize 
   metrics from running `noc` microservices, crash reports, alerts.
   * Grafana: http://<ip>:3000
   * Alertmanager: http://<ip>:9093
   * Sentry: http://<ip>:9000
   * VictoriaMetrics: http://<ip>:8880

Q: how can i start using this?

A: You need run 
   ```
   docker-compose -f docker-compose-infra.yml up -d  
   ```

Q: Sentry not work after first run. 

A: You need run 
   ```
   docker exec -ti docker_sentry_1 sentry upgrade
   ```
   Setup admin user and password.

   Go to https://0.0.0.0:9000 to login in Sentry

Q: Can I use the file to monitor other NOC installations?

A: Yes. Edit *./var/docker-vmagent/etc/prometheus.yml*:
   ```
     - job_name: 'prod_consul'
    consul_sd_configs:
      - server: 'consul:8500'

   ```
   to 
   ```
     - job_name: 'prod_consul'
    consul_sd_configs:
      - server: '<consul bootstrap IP NOC installations>:8500'

   ```
   and restart container *vmagent*
   ```
   docker-compose -f docker-compose-infra.yml restart vmagent
   ```
