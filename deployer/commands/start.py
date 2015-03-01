#!/usr/bin/env python

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
    # TODO(stevenle): impl.
    return {'success': True}


class GitHubWebhookHandler(webapp2.RequestHandler):

  def post(self):
    logger.info(self.request.body)

    # Verify signature.
    if not self.is_signature_valid():
      self.write_json(success=False)
      return

    data = json.loads(self.request.body)
    # The branch name can be derived from the last part of the "ref", e.g.:
    # refs/head/<branch name>.
    branch = os.path.basename(data['ref'])

    grow_service = rpc.get_service('GrowService')
    # TODO(stevenle): impl.

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
      ('/_/github/webhook', github.GitHubWebhookHandler),
      ('/_/rpc', rpc.JsonRpcHandler),
  ], debug=False)

  host = ctx.obj['HOST']
  port = ctx.obj['PORT']
  httpserver.serve(app, host=host, port=port)
