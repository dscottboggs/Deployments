from datetime       import datetime
from os.path        import abspath, dirname, join
from sys            import argv
from deployments    import BasicRsyncBackup


class BackupReverseProxy(BasicRsyncBackup):
    """Methods for backing up the reverse proxy mounts."""
    source_dir = join(
        abspath(dirname(__file__)),
        "mounts"
    )

    def __init__(self, *args, **kwargs):
        """Initialize variables needed for all methods."""
        super().__init__(*args, **kwargs)
        self.backup_dir = "/backup/%s" % self.name
        self.now = int(datetime.now().strftime('%s'))  # the current epoch time
        self.stage = "%(bd)s/staging/%(t)s" % {
            'bd': self.backup_dir, 't': self.now
        }


def main():
    """Code to execute this file as a script."""
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
    backup = BackupReverseProxy(freq, abspath(__file__))
    backup.do_backup()


if __name__ == '__main__':
    main()
