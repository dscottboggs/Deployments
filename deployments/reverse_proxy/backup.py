from datetime       import datetime
from os.path        import abspath
from sys            import argv
from deployments    import BasicRsyncBackup


class BackupReverseProxy(BasicRsyncBackup):
    """Methods for backing up the reverse proxy mounts."""
    backup_dir = "/backup/reverse_proxy"
    source_dir = '.'

    def __init__(self):
        """Initialize variables needed for all methods."""
        self.now = datetime.now().strftime('%s')       # the current epoch time
        self.stage = "%(bd)s/staging/%(t)s" % {
            'bd': self.backup_dir, 't': self.now
        }


def main():
    """Code to execute this file as a script."""
    backup = BackupReverseProxy()
    backup.do_backup()
    if "--no-cronjob" not in argv:
        # setup cron job
        with open("/etc/cron.weekly/backup_reverse_proxy.sh", 'w') as cronjob:
            cronjob.write(
                "#!/bin/sh\npython %s --no-cronjob" % abspath(__file__)
            )


if __name__ == '__main__':
    main()
