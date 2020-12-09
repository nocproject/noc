Infrastructure FAQ:
----
Q: What is `docker-compose-infra.yml`?

A: These are several services that collect and visualize 
   metrics from running `noc` microservices, crash reports, alerts.
   * Grafana: http://<ip>:3000
   * Alertmanager: http://<ip>:9093
   * Sentry: http://<ip>:9000
   * VictoriaMetrics: http://<ip>:8880

Q: Sentry not work after first run. 

A: You need run 
   ```
   docker exec -ti docker_sentry_1 sentry upgrade
   ```
   Setup admin user and password.

   Go to https://0.0.0.0:9000 to login in Sentry
