import unittest
import figgypy.config

import sys
import os

class TestConfig(unittest.TestCase):
    def test_config_load(self):
        os.environ['FIGGY_GPG_HOME']='tests/resources/test-keys'
        c = figgypy.config.Config('tests/resources/test-config.yaml')
        self.assertEqual(c.db, 'db.heck.ya')
        self.assertEqual(c.secrets['hush_hush'], 'i-u-i')


if __name__ == '__main__':
    unittest.main()
