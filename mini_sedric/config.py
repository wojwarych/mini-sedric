"""App config kept in Dynaconf library style"""

import os

from dynaconf import Dynaconf  # type: ignore[import-untyped]

# well-known issue with dynaconf and running tests
# https://github.com/dynaconf/dynaconf/issues/374
curr_dir = os.path.dirname(os.path.realpath(__file__))
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    environments=True,
    settings_files=[f"{curr_dir}/settings.toml", f"{curr_dir}/.secrets.toml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
