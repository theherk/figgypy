figgypy
=======

A simple configuration parser.

Installation
------------

    pip install figgypy

Usage
-----

    from figgypy import Config

    cfg = Config(conf_file)

Config object can be created with a filename only, relative path, or absolute path.
If only name or relative path is provided, look in this order:

1. current directory
2. `~/.config/<file_name>`
3. `/etc/<file_name>`

It is a good idea to include you `__package__` in the file name.
For example, `cfg = Config(os.path.join(__package__, 'config.yaml'))`.
This way it will look for `your_package/config.yaml`,
`~/.config/your_package/config.yaml`, and `/etc/your_package/config.yaml`.

This will create a `cfg` variable with attributes for each top level item in the configuration file. Each attribute will be a dictionary with the remaining nested structure.

The configuration file currently supports json, _xml*_, and yaml.

_* note_ - xml will work, but since it requires having only one root, all of the configuration will be in a dictionary named that root. See examples below.

Examples
--------

### json

```json
{
    "db": {
        "url": "mydburl.com",
        "name": "mydbname",
        "user": "myusername",
        "pass": "correcthorsebatterystable"
    },
    "log": {
        "file": "/var/log/cool_project.log",
        "level": "INFO"
    }
}
```

    cfg = Config('theabove.json')

This yields object `cfg` with attributes `db` and `log`, each of which are dictionaries.

### xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    <db>
        <url>mydburl.com</url>
        <name>mydbname</name>
        <user>myusername</user>
        <pass>correcthorsebatterystable</pass>
    </db>
    <log>
        <file>/var/log/cool_project.log</file>
        <level>INFO</level>
    </log>
</config>
```

    cfg = Config('theabove.xml')

This yields object `cfg` with attribute `config`, which is the complete dictionary.

### yaml

```yaml
db:
  url: mydburl.com
  name: mydbname
  user: myusername
  pass: correcthorsebatterystable
log:
  file: /var/log/cool_project.log
  level: INFO
```

    cfg = Config('theabove.yaml')

This yields object `cfg` with attributes `db` and `log`, each of which are dictionaries. This is the exact same behaviour as json, which makes sense given the close relationship of yaml and json.

Thanks
------

This tool uses [Seria](https://github.com/rtluckie/seria) to serialize between supported formats. Seria is a great tool if you want convert json, xml, or yaml to another of the same three formats.
