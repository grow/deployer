#!/usr/bin/env python

import json
import os
import shutil
import subprocess
import sys
import tempfile

import click
import git
import webapp2

from deployer import logger
from deployer import rpc
from paste import httpserver

__all__ = ('start',)


class Error(Exception):
  pass


def get_webhooks():
  config_dir = os.path.expanduser('~/.deployer')
  if not os.path.exists(config_dir):
    os.mkdir(config_dir)
  webhooks_file_path = os.path.join(config_dir, 'webhooks.json')
  webhooks = []
  if os.path.exists(webhooks_file_path):
    with open(webhooks_file_path) as webhooks_file:
      try:
        webhooks = json.load(webhooks_file)['webhooks']
      except ValueError:
        pass
  return webhooks


def set_webhooks(webhooks):
  config_dir = os.path.expanduser('~/.deployer')
  if not os.path.exists(config_dir):
    os.mkdir(config_dir)
  webhooks_file_path = os.path.join(config_dir, 'webhooks.json')
  with open(webhooks_file_path, 'w') as webhooks_file:
    json.dump({'webhooks': webhooks}, webhooks_file)


class GrowService(object):

  @rpc.RpcMethod
  def Deploy(self, repo, host='github', branch='master', commit_id=None,
      access_token=None, deploy_target='default'):
    """Deploys a grow site.

    Args:
      repo: The id of the git repository to deploy.
      host: Right now, only "github" is supported.
      branch: The git branch to deploy from. Defaults to master.
      commit_id: If provided, deploys a particular commit. Otherwise, HEAD is
          deployed.
      access_token: OAuth2 access token. Required for private
          repos.
      deploy_target: The grow deployment target.
    """
    if host != 'github':
      raise Error('Only host="github" is currently supported.')

    tmp_dir = tempfile.mkdtemp(prefix='grow-')
    try:
      # Clone the repo.
      logger.info('cloning pod')
      if access_token:
        clone_url = 'https://{}@github.com/{}.git'.format(
            access_token, repo)
      else:
        clone_url = 'https://github.com/{}.git'.format(repo)
      root = git.Git(tmp_dir)
      root.clone(clone_url, 'growpod')
      pod_path = os.path.join(tmp_dir, 'growpod')

      # Checkout the branch and/or commit to deploy.
      git_repo = git.Git(pod_path)
      if branch != 'master':
        git_repo.checkout(branch)
      if commit_id:
        git_repo.checkout(commit_id)

      # Run grow deploy.
      logger.info('deploying pod')
      ret_code = subprocess.call(
          ['grow', 'deploy', '--confirm', deploy_target, pod_path])
      if ret_code != 0:
        logger.info('deploy failed')
        return {'success': False}
    finally:
      logger.info('removing %s', tmp_dir)
      shutil.rmtree(tmp_dir)

  @rpc.RpcMethod
  def AddWebhook(self, repo, host='github', branch='master', access_token=None,
      deploy_target='default'):
    """Adds a webhook listener that triggers a deploy on push."""
    logger.info('adding webhook')
    if host != 'github':
      raise Error('Only host="github" is currently supported.')
    webhooks = get_webhooks()
    webhooks.append({
        'repo': repo,
        'branch': branch,
        'access_token': access_token,
        'deploy_target': deploy_target,
    })
    set_webhooks(webhooks)
    return {'success': True}


class GitHubWebhookHandler(webapp2.RequestHandler):

  def post(self):
    logger.info(self.request.body)

    # Verify signature.
    if not self.is_signature_valid():
      logger.info('invalid github webhook signature')
      self.write_json(success=False)
      return

    data = json.loads(self.request.body)
    repo = data['repository']['url'][8:]  # Remove "https://" from the url.

    # The branch name can be derived from the last part of the "ref", e.g.:
    # refs/head/<branch name>.
    branch = os.path.basename(data['ref'])

    grow_service = rpc.get_service('GrowService')
    webhooks = get_webhooks()
    for webhook in webhooks:
      if webhook.get('repo') == repo and webhook.get('branch') == branch:
        deploy_target = webhook.get('deploy_target') or 'default'
        access_token = webhook.get('access_token')
        grow_service.Deploy(repo, host='github', branch=branch,
            access_token=access_token, deploy_target=deploy_target)

  def is_signature_valid(self):
    header = self.request.headers.get('X-Hub-Signature', None)
    if not header:
      return False
    if not header.startswith('sha1='):
      return False
    signature = header[5:]

    # The GitHub webhook signature is the HMAC SHA1 hex digest with the secret
    # as its key.
    webhook_secret = str(settings.get('github_webhook_secret'))
    payload = str(self.request.body)
    hash = hmac.new(webhook_secret, payload, hashlib.sha1).hexdigest()
    return signature == hash

  def write_json(self, **kwargs):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(kwargs, indent=2))


@click.command()
@click.pass_context
def start(ctx):
  rpc.register_service('GrowService', GrowService)
  app = webapp2.WSGIApplication([
      ('/_/github/webhook', GitHubWebhookHandler),
      ('/_/rpc', rpc.JsonRpcHandler),
  ], debug=True)

  host = ctx.obj['HOST']
  port = ctx.obj['PORT']
  httpserver.serve(app, host=host, port=port)
