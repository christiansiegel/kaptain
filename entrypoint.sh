#!/bin/sh

# https://docs.openshift.com/container-platform/3.3/creating_images/guidelines.html
if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  fi
fi

uwsgi --http :8080 --threads 10 -w app
