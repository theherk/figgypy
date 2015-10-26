import unittest
import figgypy.config

import sys
import os

class TestConfig(unittest.TestCase):
    def test_config_load(self):
        os.environ['FIGGY_GPG_HOME']='tests/resources/test-keys'
        c = figgypy.config.Config('tests/resources/test-config.yaml')
        self.assertEqual(c.db['host'], 'db.heck.ya')
        self.assertEqual(c.db['pass'], 'test password')


if __name__ == '__main__':
    unittest.main()
