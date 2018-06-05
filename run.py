from subprocess                         import check_call
from os.path                            import abspath, dirname, join
from time                               import sleep
from deployments.reverse_proxy.backup   import BackupReverseProxy
from pytest                             import main as pytest
from sys                                import stdout


def ask_for_admin_user():
    """Request input for user details."""


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
    from deployments.nextcloud.backup import BackupNextcloud
    nextcloud_dir = join(
        abspath(dirname(__file__)),
        "deployments",
        "nextcloud"
    )
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
    setup_reverse_proxy()
    setup_resume()
    setup_nextcloud()


if __name__ == '__main__':
    main()
