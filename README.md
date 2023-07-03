# kube-updater
Automatically pull latest docker image and restart deployment/stateful set. It's mainly useful for homelab, where people often use `latest` tag on all images. This simple python script will check if currently running `latest` image is up-to-date and if it is not, it will restart deployment/delete pod of a stateful set, so new pod can be started with a new image.
```
[INFO] No update available for image ghcr.io/goauthentik/server:latest. Skipping
[INFO] No update available for image vaultwarden/server:latest. Skipping
[INFO] No update available for image collabora/code:latest. Skipping
[INFO] No update available for image nextcloud:latest. Skipping
[INFO] No update available for image mariadb:latest. Skipping
[INFO] No update available for image gitlab/gitlab-ce:latest. Skipping
[INFO] No update available for image registry.gitlab.com/gitlab-org/cluster-integration/gitlab-agent/agentk:latest. Skipping
[INFO] No update available for image homeassistant/home-assistant:latest. Skipping
[INFO] No update available for image eclipse-mosquitto:latest. Skipping
[INFO] No update available for image requarks/wiki:latest. Skipping
[INFO] No update available for image ghcr.io/benphelps/homepage:latest. Skipping
[INFO] No update available for image pihole/pihole:latest. Skipping
[INFO] No update available for image haugene/transmission-openvpn:latest. Skipping
[INFO] No update available for image benbusby/whoogle-search:latest. Skipping
[INFO] No update available for image ghcr.io/docker-mailserver/docker-mailserver:latest. Skipping
[INFO] No update available for image roundcube/roundcubemail:latest. Skipping
[INFO] No update available for image ghcr.io/gotify/server:latest. Skipping
[INFO] No update available for image grafana/grafana:latest. Skipping
[INFO] No update available for image kubernetesui/dashboard:latest. Skipping
[INFO] No update available for image louislam/uptime-kuma:latest. Skipping
[INFO] No update available for image ghcr.io/linuxserver/jackett:latest. Skipping
[INFO] No update available for image ghcr.io/linuxserver/lidarr:latest. Skipping
[INFO] No update available for image deluan/navidrome:latest. Skipping
[INFO] No update available for image sctx/overseerr:latest. Skipping
[INFO] No update available for image plexinc/pms-docker:latest. Skipping
[INFO] No update available for image ghcr.io/linuxserver/radarr:latest. Skipping
[INFO] No update available for image ghcr.io/linuxserver/sonarr:latest. Skipping
[INFO] No update available for image tautulli/tautulli:latest. Skipping
```
It also allows to specify a Gotify URL where list of updated deployments will be sent. To use that, just configure `GOTIFY_URL` environment variable. You can run it as a CronJob inside a cluster to get updates periodically. 
