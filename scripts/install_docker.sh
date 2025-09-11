#!/usr/bin/env bash
set -euo pipefail
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER || true
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
docker compose version || true
echo "Re-login or run: newgrp docker"
