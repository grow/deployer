#!/usr/bin/env python

"""Logging wrapper."""

import logging
import sys

LOGGER = logging.getLogger('deployer')


def debug(*args, **kwargs):
  LOGGER.debug(*args, **kwargs)


def info(*args, **kwargs):
  LOGGER.info(*args, **kwargs)


def error(*args, **kwargs):
  LOGGER.error(*args, **kwargs)


def init():
  LOGGER.setLevel(logging.DEBUG)
  ch = logging.StreamHandler(sys.stderr)
  ch.setLevel(logging.DEBUG)
  LOGGER.addHandler(ch)
