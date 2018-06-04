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
    if "--no-cronjob" in argv:
        # setup cron job
        freq = None
    else:
        if '--freq=hourly' in argv:
            freq = 'hourly'
        if '--freq=daily' in argv:
            freq = 'daily'
        if '--freq=monthly' in argv:
            freq = 'monthly'
        else:
            freq = 'weekly'
    backup.do_backup(freq, abspath(__file__))


if __name__ == '__main__':
    main()
