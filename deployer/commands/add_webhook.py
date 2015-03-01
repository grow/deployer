#!/usr/bin/env python

import click
from deployer import rpc

__all__ = ('add_webhook',)


@click.command()
@click.option('--repo', required=True)
@click.option('--branch', default='master')
@click.option('--access_token', default=None)
@click.option('--deploy_target', default='default')
@click.option('--webhook_secret', default=None)
@click.pass_context
def add_webhook(ctx, repo, branch, access_token, deploy_target, webhook_secret):
  data = {
    'repo': repo,
    'branch': branch,
    'deploy_target': deploy_target,
    'access_token': access_token,
    'webhook_secret': webhook_secret,
  }
  response = rpc.call(ctx, 'GrowService.AddWebhook', data)
  if response.json().get('result', {}).get('success'):
    click.echo('success')
  else:
    click.echo('failed')
