from deployments    import BasicRsyncBackup, client
from os.path        import dirname, abspath, join
from datetime       import datetime


class BackupNextcloud(BasicRsyncBackup):
    """Backup the database and files for the nextcloud service."""

    backup_dir = "/backups/nextcloud"
    source_dir = join(dirname(abspath(__file__)), "mounts")

    def __init__(self):
        """Initialize variables that are dynamic."""
        self.now = int(datetime.now().strftime(r"%s"))
        self.stage = join(self.backup_dir, "staging", self.now)
        self.container = client.containers.list(
            filter={'name': 'nextcloud_database_1'}
        )[0]    # throws an exception if the container isn't running.

    def do_backup(self):
        """Override to add extra steps."""
        self.backup_database()
        super().do_backup()

    def backup_database(self):
        """Get a dump from the database and store it in the staging area."""
        self.container.exec_run()
