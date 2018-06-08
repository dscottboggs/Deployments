#!/usr/bin/env python2
from jinja2                 import Template
from subprocess             import check_call
from time                   import sleep
from os                     import execlp as switch_to_cmd
from os.path                import join
from deployments.nextcloud  import occ, client, user_info, THIS_DIR
from deployments            import font
from deployments.misc       import wait

example_users = [
    {
        "display_name": "Full Name",
        "user_id":      "sign_in_name",
        "email":        "email@address.com",
        "password":     "random-pa$sw0rd",
    }, {
        "display_name": "Optional second admin",
        "user_id": "not_required",
        "email": "but_perfectly@valid.com",
        "password": "delete_if_not_used"
    }, {
        "display_name": "Same format",
        "user_id": "as_above",
        "email": "you@get.the",
        "password": "idea.jpg"
    }
]


class ContainerDidNotStartException(Exception): pass


def compose():
    """Create the docker-compose file from the template and call 'up' on it."""
    url = user_info['url']
    with open(join(THIS_DIR, "docker-compose.yml.j2"), 'r') as compose_file:
        composition_text = Template(compose_file.read()).render(
            {
                u"password":    user_info[u'database'],
                u"url":         url,
                u"admin_email": user_info[u'admin'][0]['email']
            }
        )
    with open(join(THIS_DIR, "docker-compose.yml"), 'w') as compose_file:
        compose_file.write(composition_text)
    check_call("docker-compose up -d", shell=True, cwd=THIS_DIR)
    wait(30)
    assert len(client.containers.list(filters={u"name": u"nextcloud_frontend_1"}))
    return client.containers.list(
        filters={u"name": u"nextcloud_frontend_1"}
    )[0]


def install_nextcloud(nextcloud_container):
    assert nextcloud_container.status == u"running"
    assert user_info[u'database'] != 'password'
    assert "localhost" not in user_info[u'urls'], \
        "Since this process automates SSL verification, you must use a valid"\
        + "URL."
    if not occ(
                None,
                "maintenance:install",
                '--database="mysql"',
                '--database-name="nextcloud"',
                '--database-user="nextcloud"',
                '--database-host="nextcloud_database_1"',
                '--database-pass="%s"' % user_info[u'database'],
                '--admin-user="%s"' % user_info[u'admin'][0][u'user_id'],
                '--admin-pass="%s"' % user_info[u'admin'][0][u'password']
            ):
        print("Install command failed.")
        exit(1)
    check_call(
        u'docker-compose down && docker-compose up -d',
        shell=True,
        cwd=THIS_DIR
    )
    return client.containers.list(
        filters={u"name": u"nextcloud_frontend_1"}
    )[0]

def set_trusted_domains(nextcloud_container):
    """Use sed(1) to change the URL of the config.php file.

    TODO handle more than one URL.
    """
    cmd_output = nextcloud_container.exec_run(
        "sed -i s/localhost/%s/ config/config.php" % user_info['urls'][0]
    )
    if cmd_output.exit_code:
        print("Error running the command to update the config:")
        print(cmd_output.output)
        exit(cmd_output.exit_code)


def setup_users():
    """Set up the info for each user specified in the user.yml file."""
    for admin in user_info['admin']:
        for key in admin.keys():
            for example_user in example_users:
                if admin[key] == example_user[key]:
                    raise ValueError(
                        "%s still uses the default value for %s; %s==%s",
                        admin['display_name'],
                        key,
                        admin[key],
                        example_user[key]
                    )
        if not occ(None, "user:info", admin['user_id']):
            occ(
                {"OC_PASS": admin['password']},
                'user:create', "--password-from-env",
                '--display-name="%s"' % admin['display_name'],
                '--group="admin"',
                admin['user_id'],
            )
            print(
                "Added user %s. Please remember to set email in the GUI."
                % admin['display_name']
            )
    if user_info.get('others'):
        for user in user_info.get('others'):
            for key in user.keys():
                for example_user in example_users:
                    if user[key] == example_user[key]:
                        raise ValueError(
                            "%s still uses the default value for %s; %s==%s",
                            user['display_name'],
                            key,
                            user[key],
                            example_user[key]
                        )
            if not occ(None, "user:info", user['user_id']):
                occ(
                    {"OC_PASS": user['password']},
                    'user:create', "--password-from-env",
                    '--display-name="%s"' % user['display_name'],
                    user['user_id'],
                )
                print("Added user %s." % user['display_name'])
                print("Please remember to set email in the GUI.")


def main():
    """Perform each of the installation steps.

    Compose the services, install nextcloud, set the trusted domains,
    and setup the users.
    """
    cont = compose()
    cont = install_nextcloud(cont)
    set_trusted_domains(cont)
    setup_users()


if __name__ == '__main__':
    main()
    print(
          font.build(FOREGROUND_COLOR=b"CYAN", WEIGHT=b"BOLD")
        + b"The nextcloud container should be ready now."
        + font.build(WEIGHT=b'NORMAL')
        + b"Switching to Apache log output..."
        + font.build(b'RESET')
    )
    switch_to_cmd(u"docker-compose", u"docker-compose", u'logs', u'-f')
