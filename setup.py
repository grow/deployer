#!/usr/bin/env python

import setuptools
import uuid
from pip import req

ENTRY_POINTS = """
[console_scripts]
deployer=deployer.main:main
"""


def get_version():
  with open('deployer/VERSION') as fp:
    return fp.read().strip()


def get_requirements():
  reqs = []
  for r in req.parse_requirements('requirements.txt', session=uuid.uuid1()):
    reqs.append(str(r.req))
  return reqs


setuptools.setup(
    name='deployer',
    version=get_version(),
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points=ENTRY_POINTS,
)
