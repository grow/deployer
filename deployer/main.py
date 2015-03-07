#!/usr/bin/env python

"""Grow deployer CLI."""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import click
from deployer import config
from deployer import commands
from deployer import logger


@click.group()
@click.option('--host', default='localhost', envvar='DEPLOYER_HOST')
@click.option('--port', default=8880, envvar='DEPLOYER_PORT')
@click.pass_context
def cli(ctx, host, port):
  config_flags = config.get('flags') or {}
  if 'host' in config_flags:
    host = config_flags['host']
  if 'port' in config_flags:
    port = config_flags['port']

  ctx.obj['HOST'] = host
  ctx.obj['PORT'] = port


@click.command()
def version():
  with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as fp:
    version = fp.read().strip()
  click.echo(version)


def main():
  logger.init()

  cli.add_command(commands.add_webhook)
  cli.add_command(commands.auth)
  cli.add_command(commands.start)
  cli.add_command(version)
  cli(obj={})


if __name__ == '__main__':
  main()
