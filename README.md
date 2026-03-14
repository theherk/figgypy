# figgypy

[![CI](https://github.com/theherk/figgypy/actions/workflows/ci.yml/badge.svg)](https://github.com/theherk/figgypy/actions/workflows/ci.yml)

A simple configuration parser with transparent secret decryption via GPG, AWS KMS, and AWS SSM Parameter Store.

Requires Python 3.10+.

## Installation

```sh
pip install figgypy
```

Or with [uv](https://docs.astral.sh/uv/):

```sh
uv add figgypy
```

## Usage

```python
import figgypy

cfg = figgypy.Config("config.yaml")

# Access values as attributes (set from top-level keys).
cfg.db["host"]

# Or use the values dict directly.
cfg.values.get("db")

# Or use the get_value helper.
cfg.get_value("db")
```

### File Lookup

A `Config` can be created with a filename, relative path, or absolute path. For non-absolute paths, figgypy searches in order:

1. Current directory
2. `~/.config/<file_name>`
3. `/etc/<file_name>`

Including your `__package__` in the path is a good practice:

```python
cfg = figgypy.Config(os.path.join(__package__, "config.yaml"))
```

### Supported Formats

Configuration files can be YAML, JSON, or XML. The format is determined by file extension (`.yaml`, `.yml`, `.json`, `.xml`). Unrecognized extensions fall back to YAML parsing.

For XML, the root element becomes a top-level key since XML requires a single root:

```xml
<config>
    <db>
        <host>db.example.com</host>
    </db>
</config>
```

```python
cfg = figgypy.Config("config.xml")
cfg.config["db"]["host"]  # "db.example.com"
```

### Global Configuration

A `Config` instance can be shared globally across modules:

```python
# app.py
import figgypy
cfg = figgypy.Config(config_file="config.yaml")
figgypy.set_config(cfg)

# elsewhere.py
import figgypy
figgypy.get_value("db")
```

### Programmatic Configuration

No file is required. Values can be set directly:

```python
cfg = figgypy.Config()
cfg.set_value("db", {"host": "localhost", "port": 5432})
```

### Reconfiguration

Use `Config.setup` to reconfigure an existing instance with new settings:

```python
cfg.setup(config_file="other.yaml", decrypt_kms=False, gpg_config=gpg_conf)
```

## Secrets

Secrets in configuration files are decrypted transparently at load time. All three decryption methods (GPG, KMS, SSM) are enabled by default. Disable any of them at construction:

```python
cfg = figgypy.Config("config.yaml", decrypt_gpg=False, decrypt_kms=False, decrypt_ssm=False)
```

Setting a decrypt flag back to `True` triggers reprocessing:

```python
cfg.decrypt_kms = True
```

### GPG

PGP-encrypted values are detected automatically when they contain a `BEGIN PGP` block:

```yaml
db:
  host: db.example.com
  pass: |
    -----BEGIN PGP MESSAGE-----
    Version: GnuPG v2

    hQIMAzf92ZrOUZL3ARAAgW...
    -----END PGP MESSAGE-----
```

Alternatively, use the `_gpg` key to wrap an encrypted value:

```yaml
db:
  pass:
    _gpg: |
      -----BEGIN PGP MESSAGE-----
      ...
      -----END PGP MESSAGE-----
```

To encrypt a value:

```sh
echo -n "your secret" | gpg --encrypt --armor -r KEY_ID
```

GPG configuration can be passed in:

```python
gpg_config = {"homedir": "~/.gnupg/", "binary": "gpg", "keyring": "pubring.kbx"}
cfg = figgypy.Config("config.yaml", gpg_config=gpg_config)
```

### AWS KMS

Use the `_kms` key with a base64-encoded ciphertext blob:

```yaml
db:
  pass:
    _kms: AQICAHg...base64...==
```

To encrypt a value:

```sh
aws kms encrypt --key-id 'alias/your-key' --plaintext "your secret" \
    --query CiphertextBlob --output text
```

Or use the Python helper:

```python
from figgypy.util import kms_encrypt
encrypted = kms_encrypt("your secret", "alias/your-key")
```

### AWS SSM Parameter Store

Use the `_ssm` key with the parameter name:

```yaml
db:
  pass:
    _ssm: /myapp/db/password
```

Parameters are fetched with decryption enabled (`WithDecryption=True`).

To store a parameter:

```python
from figgypy.util import ssm_store_parameter
ssm_store_parameter("/myapp/db/password", "your secret")
```

### AWS Configuration

AWS credentials follow the standard boto3 resolution order: explicit config, environment variables, then machine configuration (instance profile, config files).

Pass credentials explicitly when needed:

```python
aws_config = {
    "aws_access_key_id": "...",
    "aws_secret_access_key": "...",
    "region_name": "us-east-1",
}
cfg = figgypy.Config("config.yaml", aws_config=aws_config)
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```sh
uv sync
uv run pytest
uv run ruff check .
```
