#!/usr/bin/env python

#  Copyright (C) 2014  Alexander Gude - gude@physics.umn.edu
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  The most recent version of this program is available at:
#  https://github.com/UMN-CMS/LogSaver

# Cleanly exit program
from sys import exit
# Access external programs
from subprocess import call
# Secure methods of generating random directories
from tempfile import mkdtemp
# Get the time
from time import strftime
# Allow removal of a directory structure
from shutil import rmtree
# Make paths sane, and allow splitting
from os.path import normpath, split


## Helper functions
class Rsyncer:
    """ A class to handle running rsync """
    def __init__(self, rsync_exe, remote_location):
        """ Set up the class. """
        self.rsync_exe = rsync_exe
        self.remote_location = remote_location

        # Make the temp directory, build the command, and run it
        current_time = strftime("%Y%m%d%H%M%S")
        prefix = "power_mezzanine_tester_logs_" + current_time + "_"
        self.tmp_directory = normpath(mkdtemp(prefix=prefix) + '/')
        self.__build_command()

    def __build_command(self):
        """ Build the rsync command that will be called. """
        # Build command
        self.command = [
            self.rsync_exe,
            "--archive",
            self.remote_location,
            self.tmp_directory
            ]

    def run(self):
        """ Run the rsync command. """
        com = ' '.join(self.command)
        call(com, shell=True)

    def clean(self):
        """ Remove self.tmp_directory """
        rmtree(self.tmp_directory, ignore_errors=True)


class Tarrer:
    """ A class to handle tarring the log directory. """
    def __init__(self, tar_exe, directory_to_tar, output_location):
        self.tar_exe = tar_exe
        self.directory_to_tar = directory_to_tar
        self.output_location = output_location

        # Build the command to run
        self.__build_command()

    def __build_command(self):
        """ Build the tar command that will be called. """
        # Output file
        current_time = strftime("%Y%m%d%H%M%S")
        file_name = normpath("power_mezzanine_tester_logs_" + current_time + ".tar.bz2")
        output_file = normpath(self.output_location + "/" + file_name)
        (base_dir, log_dir) = split(self.directory_to_tar)
        input_files = normpath(log_dir + "/*.txt")

        # Build the command
        # I can't get "tar -C dir -cjf out.tar.bz2 stuff" to work, so we use cd
        # explicitly
        self.command = [
            "cd",
            base_dir,
            "&&",
            self.tar_exe,
            "-cjf",
            output_file,
            input_files,
            ]

    def run(self):
        """ Run the rsync command. """
        com = ' '.join(self.command)
        call(com, shell=True)


##### START OF CODE
if __name__ == '__main__':
    from distutils.spawn import find_executable
    from argparse import ArgumentParser

    # Check if rsync exists
    rsync_exe = find_executable("rsync")
    tar_exe = find_executable("tar")
    if rsync_exe is None:
        exit("Can not find rsync.")
    elif tar_exe is None:
        exit("Can not find tar.")

    # Command line argument parser
    arg_parser = ArgumentParser(
        description="Backup log files from a remote server."
    )
    # Arguments
    arg_parser.add_argument(
        "log_location",
        type=str,
        help="location of the log files in a form that rsync understands"
    )
    arg_parser.add_argument(
        "output_dir",
        type=str,
        help="local directory to backup logs to"
    )

    args = arg_parser.parse_args()

    # Set up our objects
    rsyncer = Rsyncer(rsync_exe, args.log_location)
    tarrer = Tarrer(tar_exe, rsyncer.tmp_directory, args.output_dir)
    # Pull the files and tar them
    rsyncer.run()
    tarrer.run()
    rsyncer.clean()
