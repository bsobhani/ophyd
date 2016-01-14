
import logging
import unittest

import epics

from ophyd.utils.startup import setup as setup_ophyd


logger = logging.getLogger('ophyd_session_test')


def setup_package():
    setup_ophyd()


def teardown_package():
    pass


def main(is_main):
    # fmt = '%(asctime)-15s [%(levelname)s] %(message)s'
    # logging.basicConfig(format=fmt, level=logging.DEBUG)
    epics.ca.use_initial_context()

    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)

    if is_main:
        setup_package()
        unittest.main()
        teardown_package()
