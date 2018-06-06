from subprocess                         import check_call, CalledProcessError
from os                                 import access, F_OK as file_exists
from os                                 import R_OK as file_is_readable
from os                                 import environ, getuid, getgid
from os.path                            import abspath, dirname, join
from time                               import sleep
from deployments.reverse_proxy.backup   import BackupReverseProxy
from deployments.misc                   import random_words
from pytest                             import main as pytest
from sys                                import stdout
from re                                 import search, match
from getpass                            import getpass
from yaml                               import dump

THIS_DIR = dirname(abspath(__file__))


def ask_for_admin_user():
    """Request input for user details."""
    def offer2edit_userconf():
        response = raw_input("Would you like to edit the user config? (y/N)  ")
        if response.lower()[0] == "y":
            if environ.get('EDITOR'):
                check_call("%s %s" % (
                    environ.get('EDITOR'),
                    join(THIS_DIR, "deployments", "nextcloud", "user.yml")
                ), shell=True)
            else:
                try:
                    check_call("nano %s" % join(
                        THIS_DIR, "deployments", "nextcloud", "user.yml"
                    ), shell=True)
                except CalledProcessError as e:
                    if e.returncode == 127:
                        check_call("vi %s" % join(
                            THIS_DIR, "deployments", "nextcloud", "user.yml"
                        ), shell=True)
                    else:
                        raise
    if access(
        join(THIS_DIR, "deployments", "nextcloud", "user.yml"),
        file_exists
    ):
        if access(
            join(THIS_DIR, "deployments", "nextcloud", "user.yml"),
            file_is_readable
        ):
            print("We'll be using this for the user configuration:")
            with open(join(
                        THIS_DIR, "deployments", "nextcloud", "user.yml"
                    ), 'r') as userconf:
                print(userconf.read())
            offer2edit_userconf()
        else:
            raise OSError(
                "I don't have access to %s." % join(
                    THIS_DIR, "deployments", "nextcloud", "user.yml"
                )
            )
    else:
        display_name    = raw_input("What's your full name?    ")
        user_id         = raw_input("Pick a unique user ID:    ")
        assert not search(r'\W', user_id), \
            "User ID can only contain alphanumeric characters and _"
        email           = raw_input("What's your email?        ")
        assert match(r'^\w[\w\.\-]*\w@\w[\w\.\-]*\w\.\w[\w\.]*\w$', email),\
            "Please enter a valid email."
        print("Pick an account password, or leave this blank to get a")
        password        = getpass("generated one:            ")
        if not password:
            password = random_words(3)
        db_password     = random_words(3)
        site_url        = raw_input("What's the nextcloud URL? ")
        assert match(r'^\w[\w\.-]*\w$', site_url),\
            "Please enter a valid URL."
        assert not match(r'^https?://', site_url), \
            "Don't specify the protocol."
        with open(join(
                    THIS_DIR, "deployments", "nextcloud", "user.yml"
                ), 'w') as user_file:
            dump(
                {
                    'admin': [
                        {
                            'display_name': display_name,
                            'user_id': user_id,
                            'email': email,
                            'password': password,
                        }
                    ],
                    "database": db_password,
                    "urls": [site_url]
                },
                user_file
            )
        with open(
                    join(
                        THIS_DIR, "deployments", "nextcloud", "user.yml"
                    ), 'r'
                ) as user_file:
            print(
                  "I've stored the following under nextcloud/user.yml:\n"
                + user_file.read()
            )
        offer2edit_userconf()


def run_tests_at(filepath):
    """Run pytest on the tests stored in filepath.

    Raises assertion error if the command fails.
    """
    assert pytest(args=[filepath]) == 0


def bring_up_service_at(filepath):
    check_call(
        "docker-compose --project-directory {0} --file {0}/".format(
            filepath
        ) + "docker-compose.yml up -d",
        shell=True
    )


def wait(time=10, msg=None, sep=" -- "):
    """Display a message for a while."""
    while time:     # (remains)
        if msg:
            stdout.write("%s%s%d seconds.    \r" % ( msg, sep, time))
            stdout.flush()
        else:
            stdout.write("Wait %d seconds.    \r" % time)
            stdout.flush()
        time -= 1
        sleep(1)


def setup_nextcloud():
    """Setup the nextcloud service."""
    ask_for_admin_user()
    from deployments.nextcloud.first_run import main as install_nextcloud
    from deployments.nextcloud.backup import BackupNextcloud
    nextcloud_dir = join(
        THIS_DIR,
        "deployments",
        "nextcloud"
    )
    install_nextcloud()
    bring_up_service_at(nextcloud_dir)
    wait(30,
        msg="Unfortunately, the reverse proxy generation and letsencrypt "
            "setup takes some time, including an actual timer. Please wait ",
        sep=""
    )
    run_tests_at(nextcloud_dir)
    brp = BackupReverseProxy()
    bnc = BackupNextcloud()
    brp.do_backup()
    bnc.do_backup('daily', join(nextcloud_dir, "backup.py"))


def setup_resume():
    """Setup my resume site."""
    resume_filepath = join(
        abspath(dirname(__file__)),
        "deployments",
        "resume"
    )
    bring_up_service_at(resume_filepath)
    wait(30,
        msg="Unfortunately, the reverse proxy generation and letsencrypt "
            "setup takes some time, including an actual timer. Please wait ",
        sep=""
    )
    run_tests_at(resume_filepath)
    backup = BackupReverseProxy()
    backup.do_backup()


def setup_reverse_proxy():
    """Setup the reverse proxy containers."""
    reverse_proxy_path = join(
        abspath(dirname(__file__)),
        "deployments",
        "reverse_proxy"
    )
    bring_up_service_at(reverse_proxy_path)
    run_tests_at(reverse_proxy_path)
    backup = BackupReverseProxy()
    backup.do_backup('weekly', join(reverse_proxy_path, "backup.py"))
    # ^^ nothing to back up yet, this is to install the cronjob


def main():
    if not (getuid() == 0 and getgid() == 0):
        print(
            "This application is intended to be run as root. I would "
            "recommend using a virtual machine for the server, but there's "
            "no reason you can't just run `sudo python run.py`."
        )
        exit(1)
    setup_reverse_proxy()
    setup_resume()
    setup_nextcloud()


if __name__ == '__main__':
    main()
