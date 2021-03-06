from subprocess         import run, CalledProcessError
from os                 import access, F_OK as file_exists
from os                 import R_OK as file_is_readable
from os                 import environ, getuid, getgid
from os.path            import abspath, dirname, join
from misc               import random_words, wait
from pytest             import main as pytest
from re                 import search, match
from getpass            import getpass
from yaml               import dump
from time               import sleep
from multiprocessing    import Process


THIS_DIR = dirname(abspath(__file__))
reverse_proxy_path = join(
    abspath(dirname(__file__)),
    "deployments",
    "reverse_proxy"
)


def ask_for_admin_user():
    """Request input for user details."""
    def offer2edit_userconf():
        response = input("Would you like to edit the user config? (y/N)  ")
        try:
            if response.lower()[0] == "y":
                if environ.get('EDITOR'):
                    run("%s %s" % (
                        environ['EDITOR'],
                        join(THIS_DIR, "deployments", "config.yml")
                    ), shell=True, check=True)
                else:
                    try:
                        run("nano %s" % join(
                            THIS_DIR, "deployments", "config.yml"
                        ), shell=True, check=True)
                    except CalledProcessError as e:
                        if e.returncode == 127:
                            run("vi %s" % join(
                                THIS_DIR,
                                "deployments",
                                "nextcloud",
                                "config.yml"
                            ), shell=True, check=True)
                        else:
                            raise
        except IndexError:
            pass
    if access(
        join(THIS_DIR, "deployments", "config.yml"),
        file_exists
    ):
        if access(
            join(THIS_DIR, "deployments", "config.yml"),
            file_is_readable
        ):
            print("We'll be using this for the user configuration:")
            with open(join(
                        THIS_DIR, "deployments", "config.yml"
                    ), 'r') as userconf:
                print(userconf.read())
            offer2edit_userconf()
        else:
            raise OSError(
                "I don't have access to %s." % join(
                    THIS_DIR, "deployments", "config.yml"
                )
            )
    else:
        display_name    = input  ("What's your full name?    ")
        user_id         = input  ("Pick a unique user ID:    ")
        assert not search(r'\W', user_id), \
            "User ID can only contain alphanumeric characters and _"
        email           = input  ("What's your email?        ")
        assert match(r'^\w[\w\.\-]*\w@\w[\w\.\-]*\w\.\w[\w\.]*\w$', email),\
            "Please enter a valid email."
        print("Pick an account password, or leave this blank to get a")
        password        = getpass("generated one:            ")
        if not password:
            password = random_words(3)
        db_password     = random_words(3)
        site_url        = input  ("What's the nextcloud URL? ")
        assert match(r'^\w[\w\.-]*\w$', site_url),\
            "Please enter a valid URL."
        assert not match(r'^https?://', site_url), \
            "Don't specify the protocol."
        with open(join(
                    THIS_DIR, "deployments", "config.yml"
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
                        THIS_DIR, "deployments", "config.yml"
                    ), 'r'
                ) as user_file:
            print(
                "I've stored the following under nextcloud/config.yml:\n"
                + user_file.read()
            )
        offer2edit_userconf()


def run_tests_at(filepath):
    """Run pytest on the tests stored in filepath.

    Raises assertion error if the command fails.
    """
    assert pytest(args=[filepath]) == 0


def bring_up_service_at(filepath):
    """Execute `docker-compose up -d` in the specified directory."""
    return run("docker-compose up -d", shell=True, check=True, cwd=filepath)


def setup_nextcloud():
    """Setup the nextcloud service."""
    from deployments.nextcloud.first_run    import main as install_nextcloud
    from deployments.nextcloud.backup       import BackupNextcloud
    from deployments.reverse_proxy.backup   import BackupReverseProxy
    nextcloud_dir = join(
        THIS_DIR,
        "deployments",
        "nextcloud"
    )
    install_nextcloud()
    bring_up_service_at(nextcloud_dir)
    wait(
        30,
        msg="Unfortunately, the reverse proxy generation and letsencrypt "
            "setup takes some time, including an actual timer. Please wait ",
        sep=""
    )
    run_tests_at(reverse_proxy_path)
    run_tests_at(nextcloud_dir)
    brp = BackupReverseProxy()
    bnc = BackupNextcloud()
    procs = [
        Process(target=brp.do_backup),
        Process(
            target=bnc.do_backup,
            args=('daily', join(nextcloud_dir, "backup.py"))
        )
    ]
    for proc in procs: proc.start()
    for proc in procs: proc.join()


def setup_resume():
    """Setup my resume site."""
    from deployments.reverse_proxy.backup   import BackupReverseProxy
    resume_filepath = join(
        abspath(dirname(__file__)),
        "deployments",
        "resume"
    )
    bring_up_service_at(resume_filepath)
    wait(
        30,
        msg="Unfortunately, the reverse proxy generation and letsencrypt "
            "setup takes some time, including an actual timer. Please wait ",
        sep=""
    )
    run_tests_at(reverse_proxy_path)
    run_tests_at(resume_filepath)
    backup = BackupReverseProxy()
    backup.do_backup()


def setup_reverse_proxy():
    """Setup the reverse proxy containers."""
    from deployments.reverse_proxy.backup   import BackupReverseProxy
    bring_up_service_at(reverse_proxy_path)
    run_tests_at(reverse_proxy_path)
    try:
        run(
            "docker-compose logs -f",
            shell=True,
            check=False,
            cwd=reverse_proxy_path
        )
    except KeyboardInterrupt:
        ...
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
    ask_for_admin_user()
    setup_reverse_proxy()
    setup_resume()
    setup_nextcloud()


if __name__ == '__main__':
    main()
