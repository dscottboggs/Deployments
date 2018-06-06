#!/usr/bin/env bash
all=$(docker ps --format="{{.ID}}" | tr '\n' ' ')
docker stop $all
docker rm $all
