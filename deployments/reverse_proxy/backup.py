"""Backup the certificates and configurations stored in ./mounts/"""
from subprocess import check_call
from datetime   import datetime
from tarfile    import TarFile
from os         import makedirs, access, F_OK as file_exists, getcwd, chdir
from os.path    import isdir
from shutil     import rmtree


class BasicRsyncBackup:
    """Methods for backing up a folder by using the `rsync`(1) command.

    Subclasses must have the following attributes:
        - backup_dir
        - stage
        - source_dir
    """

    @staticmethod
    def prep_folder(folder):
        """Make sure that the folder exists and is writable."""
        if access(folder, file_exists):
            if isdir(folder):
                return
            raise OSError("%s is a file but we need a folder there." % folder)
        makedirs(folder)

    def do_backup(self):
        """Perform each step in the backup procedure."""
        self.prep_folder(self.backup_dir)
        self.prep_folder(self.stage)
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

    def delete_stage(self):
        """Delete the staging folder"""
        def raise_exception(func, path, info):
            raise OSError(
                "Problem removing directory/file %s. Useful info, maybe?\n%s"
                % (path, info)
            )
        return rmtree(self.stage, onerror=raise_exception)

    def archive(self):
        """Put the folder in a gzipped tar archive."""
        archive_location = "%s/%s.tar.gz" % (self.backup_dir, self.now)
        if access(archive_location, file_exists):
            raise OSError("%s already exists!" % archive_location)
        pwd = getcwd()
        chdir(self.stage)
        with TarFile.open(archive_location, mode='w:gz') as tarchive:
            tarchive.add('.')
        chdir(pwd)


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
