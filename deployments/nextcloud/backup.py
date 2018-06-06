from deployments            import BasicRsyncBackup, client
from deployments.nextcloud  import user_info
from os.path                import dirname, abspath, join
from datetime               import datetime


class BackupNextcloud(BasicRsyncBackup):
    """Backup the database and files for the nextcloud service."""

    backup_dir = "/backups/nextcloud"
    source_dir = join(dirname(abspath(__file__)), "mounts")

    def __init__(self):
        """Initialize variables that are dynamic."""
        self.now = int(datetime.now().strftime(r"%s"))
        self.stage = join(self.backup_dir, "staging", str(self.now))
        self.container = client.containers.list(
            filters={'name': 'nextcloud_database_1'}
        )[0]    # throws an exception if the container isn't running.

    def do_backup(self, *args, **kwargs):
        """Override to add extra steps."""
        self.backup_database()
        super().do_backup(*args, **kwargs)

    def backup_database(self):
        """Get a dump from the database and store it in the staging area."""
        dump_result = self.container.exec_run(
            "mysqldump -u nextcloud -p '%s' nextcloud" % user_info['database']
        )
        if dump_result.exit_code:
            raise ValueError(
                "The mysqldump command returned %d. The command output:\n%s"
                    % (int(dump_result.exit_code), dump_result.output)
            )
        with open(join(self.stage, "database.dump"), 'w') as dumpfile:
            dumpfile.write(dump_result.output)


def main():
    """The main entrypoint of the backup script if it's run alone."""
    backup = BackupNextcloud()
    backup.do_backup('daily', abspath(__file__))


if __name__ == '__main__':
    main()
