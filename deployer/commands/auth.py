#!/usr/bin/env python

"""Description."""

import urllib
import webbrowser
import click
from deployer import config
from deployer import rpc

__all__ = ('auth',)

GITHUB_SCOPES = (
    'repo',
    'write:repo_hook',
)


@click.command()
@click.option('--client_id', envvar='DEPLOYER_CLIENT_ID')
@click.option('--client_secret', envvar='DEPLOYER_CLIENT_SECRET')
@click.pass_context
def auth(ctx, client_id, client_secret):
  if client_id and client_secret:
    config.set('github', {
        'client_id': client_id,
        'client_secret': client_secret,
    })
  else:
    credentials = config.get('github', {})
    client_id = credentials.get('client_id')

  host = ctx.obj['HOST']
  if host == '0.0.0.0':
    host = 'localhost'
  port = ctx.obj['PORT']
  if host.startswith('http'):
    redirect_uri = '{}:{}/_/github/auth'.format(host, port)
  else:
    redirect_uri = 'http://{}:{}/_/github/auth'.format(host, port)

  params = {
      'client_id': client_id,
      'redirect_uri': redirect_uri,
      'scope': ','.join(GITHUB_SCOPES),
  }
  query_str = urllib.urlencode(params)
  auth_url = 'https://github.com/login/oauth/authorize?' + query_str
  webbrowser.open(auth_url)
