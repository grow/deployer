#!/usr/bin/env python

"""Deployer configuration file."""

import collections
import os
import yaml

CONFIG_PATH = '~/.deployer/config.yaml'


def get(key, default=None):
  return get_all().get(key, default)


def set(key, value):
  config = get_all()
  config[key] = value
  set_all(config)


def get_all():
  path = os.path.expanduser(CONFIG_PATH)
  if not os.path.exists(path):
    return {}
  with open(path) as fp:
    content = fp.read()
  return yaml.safe_load(content)


def set_all(config):
  path = os.path.expanduser(CONFIG_PATH)
  config_dir = os.path.dirname(path)
  if not os.path.exists(config_dir):
    os.mkdir(config_dir, 0o700)

  content = yaml.safe_dump(config, encoding='utf-8', allow_unicode=True,
      default_flow_style=False)
  with open(path, 'w') as fp:
    fp.write(content)
