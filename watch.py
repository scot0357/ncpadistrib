"""This script is meant for the sole purpose of automating NCPA builds.

"""

import configparser
import os
import logging
import requests
import subprocess
import datetime

logging.basicConfig(filename='watch.log',
                    level=logging.INFO,
                    format='%(asctime)-15s %(message)s')


def parse_config():
    """Parses the config that **should** be located in the same directory
    as the actual script.

    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = configparser.ConfigParser()
    logging.debug('Parsing the config at location %s', config_path)
    config.read(config_path)

    return config


def check_page(url):
    """Takes a URL and returns the JSON that was returned by that
    URL.

    """
    page = requests.get(url)

    return page.json()


def buildtime_is_newer(buildtime, config):
    """Determines whether or not the build time given in the instructions
    is newer than that of what we have in our RPM build directory.

    """
    builddir = config.get('build', 'pkgpath')
    pkgtime = datetime.datetime.fromtimestamp(os.path.getmtime(builddir))
    return buildtime > pkgtime


def execute_build(config):
    """Execute the make the make for the NCPA agent.

    """
    makefile = config.get('build', 'makefile')
    return subprocess.call(['make', '-e', makefile])


def upload_build(config):
    """Uploads to the distribution system.

    """
    pass


def execute_instructions(instructions, config):
    """Executes the given instructions. This probably will mean executing
    the build for NCPA.

    """
    buildtime = datetime.datetime.fromtimestamp(instructions.get('buildtime', 0))

    if buildtime_is_newer(buildtime, config):
        do_build = True

    # Having two ifs here might seem a bit obtuse or naive, but
    # in the case where we might want to make this logic more
    # complicated I have elected to make execute_build a flag
    # so we can make the logic more complicated in the future.
    if do_build is True:
        if execute_build(config) == 0:
            upload_build(config)
        else:
            raise Exception('Could not build!')





def main():
    """Kicks off all script activity. Parses the config,
    then it checks a webpage, decodes the JSON and determines whether or not
    it needs to re-build the NCPA package.

    """
    logging.info('Checking for new instructions...')
    config = parse_config()
    page_options = dict(config.items('master'))

    instructions = check_page(page_options.get('url'))
    execute_instructions(instructions, config)

    logging.info('Done checking build instructions.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        logging.exception(exc)
