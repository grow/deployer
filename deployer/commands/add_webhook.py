#!/usr/bin/env python

import json
import uuid
import click
import requests
from deployer import config

__all__ = ('add_webhook',)


@click.command()
@click.option('--repo', required=True)
@click.option('--branch', default='master')
@click.option('--deploy_target', default='default')
@click.option('--webhook_secret', default=None)
@click.pass_context
def add_webhook(ctx, repo, branch, deploy_target, webhook_secret):
  webhooks = config.get('webhooks') or []

  if not webhook_secret:
    webhook_secret = str(uuid.uuid1())

  webhooks.append({
      'host': ctx.obj['HOST'],
      'repo': repo,
      'branch': branch,
      'deploy_target': deploy_target,
      'webhook_secret': webhook_secret,
  })
  config.set('webhooks', webhooks)

  access_token = config.get('github', default={}).get('access_token')
  if access_token:
    host = ctx.obj['HOST']
    port = ctx.obj['PORT']
    webhook_url = '{}:{}/_/github/webhook'.format(host, port)
    if not host.startswith('http'):
      webhook_url = 'http://' + webhook_url

    url = 'https://api.github.com/repos/{}/hooks'.format(repo)
    headers = {
        'Accept': 'application/json',
        'Authorization': 'token {}'.format(access_token),
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        'name': 'web',
        'config': {
            'url': webhook_url,
            'content_type': 'json',
            'secret': webhook_secret,
        },
        'events': ['push'],
        'active': True,
    })
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200 or response.status_code == 201:
      click.echo('success')
    else:
      click.echo('failed')
      click.echo(response.text)
