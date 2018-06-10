"""Backup the certificates and configurations stored in ./mounts/"""
from subprocess         import check_call
from tarfile            import TarFile
from os                 import makedirs, access, F_OK as file_exists, join
from os                 import getcwd, chdir
from os.path            import isdir
from shutil             import rmtree
from deployments.misc   import TerminalOutputModifiers
from docker             import DockerClient
from yaml               import load


client = DockerClient(u"unix://var/run/docker.sock", version=u"1.30")
font   = TerminalOutputModifiers()

with open(join(THIS_DIR, "config.yml"), u'r') as uInfo_file:
    user_config = load(uInfo_file)


class BasicRsyncBackup:
    """Methods for backing up a folder by using the `rsync`(1) command.

    Subclasses must have the following attributes:
        - backup_dir
        - stage
        - source_dir
    """

    def __init__(self, name, cronjob_freq=None, backup_script=None):
        """Initialize a backup object.

        The name is the name of the service, to be used in filenames and
        whatnot.

        The cronjob_freq must be "weekly", "monthly", "daily", or "hourly".

        The backup_script needs to be the path to the actual backup script.
        """
        self.name = name
        self.cronjob_freq = cronjob_freq
        self.backup_script = backup_script

    @staticmethod
    def prep_folder(folder):
        """Make sure that the folder exists and is writable."""
        if access(folder, file_exists):
            if isdir(folder):
                return
            raise OSError("%s is a file but we need a folder there." % folder)
        makedirs(folder)

    def do_backup(self, cronjob_freq=None, backup_script=None):
        """Perform each step in the backup procedure."""
        self.prep_folder(self.backup_dir)
        self.prep_folder(self.stage)
        self.copy_files_to_stage()
        self.archive()
        if cronjob_freq:
            self.setup_cronjob(cronjob_freq, backup_script)

    def copy_files_to_stage(self):
        """Copy the files themselves and their attrs to a staging area."""
        check_call(
            "rsync -aqX --partial %(rpd)s/ %(dest)s"
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
        archive_location = "%s/%d.tar.gz" % (self.backup_dir, self.now)
        if access(archive_location, file_exists):
            raise OSError("%s already exists!" % archive_location)
        pwd = getcwd()
        chdir(self.stage)
        with TarFile.open(archive_location, mode='w:gz') as tarchive:
            tarchive.add('.')
        chdir(pwd)

    def setup_cronjob(self):
        """Save this script to the cron.{self.cronjob_freq} folder."""
        if not self.backup_script:
            raise AttributeError(
                "Need the location of the actual backup script to write the "
                "cronjob."
            )
        with open(
                    "/etc/cron.%s/backup_%s.sh" % (
                        self.cronjob_freq, self.name
                    ), 'w'
                ) as cronjob:
            cronjob.write(
                "#!/bin/sh\npython %s --no-cronjob" % backup_script
            )   # "no-cronjob" tells it to not do this step again.
