import unittest
import figgypy.config

import sys
import logging

logger = None
logger=logging.getLogger("figgypy.test")

class TestConfig(unittest.TestCase):
    def test_config_load(self):
        c = figgypy.config.Config('test-config.json')
        self.assertEquals(c.db, 'db.heck.ya')
        logger.debug('test123')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout)
    unittest.main()
