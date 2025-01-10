#   -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init


import os
import sys

sys.path.append(os.path.abspath('src/main/python'))



use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "prusaslicer_server"
default_task = "publish"

@init
def initialize_project_properties(project):
    # Dependencies
    project.build_depends_on("flask")
    project.build_depends_on("pytest")

    # Directory settings
    project.set_property("dir_source_main_python", "src/main/python")
    project.set_property("dir_source_unittest_python", "src/unittest/python")
    project.set_property("dir_source_main_scripts", "src/main/scripts")
    project.set_property('unittest_module_glob', '*.py')
    project.set_property('verbose', True)

    # Style checking
    project.set_property("flake8_max_line_length", 120)


# Custom task to run the Flask server
def run_flask_server(logger):
    import subprocess
    logger.info("Starting Flask server...")
    subprocess.call(["python", "src/main/python/server.py"])
