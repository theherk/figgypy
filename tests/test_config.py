import os
import unittest

import figgypy.config


class TestConfig(unittest.TestCase):
    def test_config_pass_on_int(self):
        os.environ['FIGGYPY_GPG_HOMEDIR']='tests/resources/test-keys'
        c = figgypy.config.Config('tests/resources/test-config.yaml')
        self.assertEqual(c.number, 1)

    def test_config_load_with_gpg(self):
        os.environ['FIGGYPY_GPG_HOMEDIR'] = 'tests/resources/test-keys'
        c = figgypy.config.Config('tests/resources/test-config.yaml')
        self.assertEqual(c.db['host'], 'db.heck.ya')
        self.assertEqual(c.db['pass'], 'test password')

    def test_config_load_without_gpg(self):
        figgypy.decrypt.GPG_IMPORTED = False
        c = figgypy.config.Config('tests/resources/test-config.yaml')
        encrypted_password = (
            '-----BEGIN PGP MESSAGE-----\n'
            'Version: GnuPG v2\n'
            '\n'
            'hQIMAzf92ZrOUZL3ARAAgWexav8+pc2lnqISEuQafFZrqYI0pU3xCuMXnFZp+hpU\n'
            'gb0LsaExZ136p4ATIinFHuaLt94hFx7gULgqoSigt/2fubnUCsOGedq122xYZdtV\n'
            'Ep/24WPVQPcMVIP9pDTJTk82A41BQsOrVYorAGjjB13zFizizYHApNTcWKr4/gfR\n'
            'jmCqAX5qusXB84fXBecCJ886uEQI2v7+Vxnk+fQMqNt3ybd/uLuBLShMSygr6uLX\n'
            'zktyeZvP2QqPSWe0OpttdcvD792/SI/CTznsjbMe0wr1L81csEQcj++4o5wJop3Y\n'
            'mbQvG/FxeDdRi2aCxh7JK2xdCsrQzXKTNG2QZMwWqatB5Lb6lJ1mNiJQGX2YK+nI\n'
            'lbjy5Cp2lHlNxa9QfB+KglueMnH9gDku5YqBDos6rCEuqK/aTDdMx0V7YGYTamZ3\n'
            '3Za+OGi+hl/+4WX2gm+bOM2WWrIysiu9k1HMI1/onui/3hr1nClR8rGb4a5qDlpg\n'
            'yRrt7LuLRU4vGXpYm05dXlUeI3uT04ur/DwLo32ujnPo3dc8LFegX8N8p1LLS9vq\n'
            'vvrvXRnWsgeAvAYFBprbEYcz7sOU04HM9OGcyjYREMs3Ih6H2oBi3GavJ2x0MG75\n'
            'M9JSTu/yytD8GCM3s+3RncKuEAxfZIk1Gbdz0pjb+U6G43qq8/vQPKtKuAeqJHDS\n'
            'SAER9YkKqbp0y85LbhUWNWPpHQ2zy8WB71TfYE6vBP5qjoxiqP/QGWjT/3jhCY+t\n'
            '5k7R6XqvdvbSu1avFlEgApknzn94I+gsWQ==\n'
            '=QuDe\n'
            '-----END PGP MESSAGE-----\n'
        )
        self.assertEqual(c.db['host'], 'db.heck.ya')
        self.assertEqual(c.db['pass'].rstrip('\n'), encrypted_password.rstrip('\n'))


if __name__ == '__main__':
    unittest.main()
