#!/usr/bin/env bash

parent_dir=$HOME/.local/share

function rm_backups() {
    rm --force --recursive --interactive=once /backup
}
function no_rm_backups() {
    echo Not removing backups. You can run this script
    echo again to remove them or remove /backup yourself.
}
function remove_cronjobs() {
    rm /etc/cron.*/backup_reverse_proxy.sh
    rm /etc/cron.*/backup_nextcloud.sh
}
function remove_containers() {
    echo -n removing $1...
    cd $parent_dir/Deployments/deployments/$2   \
        && docker-compose down > /dev/null      \
        && echo done.
}

for service in resume nextcloud reverse_proxy; do
    remove_containers $service
done
docker network prune
docker container prune
docker image prune -a
docker volume prune

rm --force --recursive $parent_dir/Deployments
echo Would you also like to remove the backups? (default NO)
select yn in YES NO; do
    case $yn in
        YES ) rm_backups; break;;
        * ) no_rm_backups; break;;
    esac
done

remove_cronjobs
