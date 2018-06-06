#!/usr/bin/env bash
docker stop $(docker ps --format="{{.ID}}" | tr '\n' ' ')
