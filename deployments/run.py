from subprocess             import check_call
from os.path                import abspath, dirname, join
from time                   import sleep
from reverse_proxy.backup   import BackupReverseProxy
from pytest                 import main as pytest


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


def setup_nextcloud():
    """Setup the nextcloud service."""
    from nextcloud.backup import BackupNextcloud
    nextcloud_dir = join(abspath(dirname(__file__)), "nextcloud")
    bring_up_service_at(nextcloud_dir)
    sleep(30)
    run_tests_at(nextcloud_dir)
    brp = BackupReverseProxy()
    bnc = BackupNextcloud()
    brp.do_backup()
    bnc.do_backup('daily', join(nextcloud_dir, "backup.py"))


def setup_resume():
    """Setup my resume site."""
    resume_filepath = join(abspath(dirname(__file__)), "resume")
    bring_up_service_at(resume_filepath)
    sleep(30)   # allow service to start and letsencrypt service to run
    run_tests_at(resume_filepath)
    backup = BackupReverseProxy()
    backup.do_backup()


def setup_reverse_proxy():
    """Setup the reverse proxy containers."""
    reverse_proxy_path = join(abspath(dirname(__file__)), "reverse_proxy")
    bring_up_service_at(reverse_proxy_path)
    sleep(10)   # to give the containers time to get ready.
    run_tests_at(reverse_proxy_path)
    backup = BackupReverseProxy()
    backup.do_backup('weekly', join(
        abspath(dirname(__file__)), "reverse_proxy", "backup.py"
    ))
    # ^^ nothing to back up yet, this is to install the cronjob


def main():
    setup_reverse_proxy()
    setup_resume()
    setup_nextcloud()


if __name__ == '__main__':
    main()
