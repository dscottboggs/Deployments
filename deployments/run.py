from subprocess                         import check_call
from os.path                            import abspath, dirname, join
from time                               import sleep
from deployments.reverse_proxy.backup   import BackupReverseProxy


def bring_up_service_at(filepath):
    check_call(
        "docker-compose --project-directory {0} --file {0}/".format(
            filepath
        ) + "docker-compose.yml up -d",
        shell=True
    )


def setup_nextcloud():
    """Setup the nextcloud service."""
    from deployments.nextcloud.backup           import  BackupNextcloud
    from deployments.nextcloud.test_nextcloud   import  test_user, test_index,\
                                                        test_upload,          \
                                                        test_upload_survives
    bring_up_service_at(join(abspath(dirname(__file__)), "nextcloud"))
    sleep(30)
    test_index()
    test_user()
    test_upload()
    test_upload_survives()
    brp = BackupReverseProxy()
    bnc = BackupNextcloud()
    brp.do_backup()
    bnc.do_backup('daily', join(
        abspath(dirname(__file__)), "nextcloud", "backup.py"
    ))


def setup_resume():
    """Setup my resume site."""
    from deployments.resume.test_resume import test_requests, test_disallowed
    bring_up_service_at(join(abspath(dirname(__file__)), "resume"))
    sleep(30)   # allow service to start and letsencrypt service to run
    test_requests()
    test_disallowed()
    backup = BackupReverseProxy()
    backup.do_backup()


def setup_reverse_proxy():
    """Setup the reverse proxy containers."""
    from deployments.reverse_proxy.test_reverse_proxy import test_companion
    from deployments.reverse_proxy.test_reverse_proxy import test_reverse_proxy
    bring_up_service_at(join(abspath(dirname(__file__)), "reverse_proxy"))
    sleep(10)   # to give the containers time to get ready.
    test_companion()
    test_reverse_proxy()
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
