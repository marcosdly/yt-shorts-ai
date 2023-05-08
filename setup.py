#! /usr/bin/env python3

from os.path import dirname, join, isdir, exists
from shutil import copytree
from sys import exit, stdout
from logging import info as log, basicConfig, INFO

# Script to setup project to being run.
# Some sensible information still have to be inserted manually (db credentials, etc).

# ---> This file is expected to exist in the root of the git repo. <--- #

# logging config
basicConfig(
    stream=stdout,
    level=INFO,
    format="::%(filename)s:Ln %(lineno)d: %(message)s"
)

def main() -> None:
    template_dir = join(dirname(__file__), "template")
    config_dir = join(dirname(__file__), "config") # doesn't need to exist nor to be dir
    if not isdir(template_dir):
        log("Path to 'template' directory doesn't point to a directory.")
        log(f"PATH: {template_dir}")
        exit(1)

    if not exists(config_dir):
        log("Creating 'config' directory...")
    copytree(src=template_dir, dst=config_dir)
    log("Copied template files to 'config' directory. Check for config entries that need manual attention.")

if __name__ == "__main__":
    main()
