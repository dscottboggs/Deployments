"""Backup the certificates and configurations stored in ./mounts/"""
from subprocess import check_call
from datetime   import datetime
from tarfile    import TarFile


class BasicRsyncBackup:
    """Methods for backing up a folder by using the `rsync`(1) command.

    Subclasses must have the following attributes:
        - backup_dir
        - stage
        - source_dir
    """

    def do_backup(self):
        """Perform each step in the backup procedure."""
        self.copy_files_to_stage()
        self.archive()

    def copy_files_to_stage(self):
        """Copy the files themselves and their attrs to a staging area."""
        check_call(
            "rsync -aqX --partial %(rpd)s/mounts/ %(dest)s"
            % {
                'rpd': self.source_dir, 'dest': self.stage
            },
            shell=True
        )

    def archive(self):
        """Put the folder in a gzipped tar archive."""
        with TarFile.open(
                    "%(backup)s/%(t)s.tar.gz" % {
                        'backup': self.backup_dir, 't': self.now
                    },
                    mode='x:gz'     # Raises an exception if file exists, open
                ) as tarchive:      # as gzipped file for writing.
            tarchive.add(self.stage)


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


if __name__ == '__main__':
    main()
