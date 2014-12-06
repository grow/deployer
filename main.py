#!/usr/bin/env python

"""Main application handler."""

import logging
import os
import shutil
import subprocess
import sys
import tempfile
import git
import webapp2
from deployer import rpc

DEBUG = True


class Error(Exception):
  pass


class GrowDeployService(object):

  @rpc.RpcMethod
  def Deploy(self, repo, host='github', branch='master',  commit_id=None,
      github_access_token=None, deploy_target='default'):
    """Deploys a grow site.

    Args:
      repo: The id of the git repository to deploy.
      host: Right now, only "github" is supported.
      branch: The git branch to deploy from. Defaults to master.
      commit_id: If provided, deploys a particular commit. Otherwise, HEAD is
          deployed.
      github_access_token: OAuth2 access token for GitHub. Required for private
          repos.
      deploy_target: The grow deployment target.
    """
    if host != 'github':
      raise Error('Only host="github" is currently supported.')
    if not github_access_token:
      raise Error('github_access_token is required.')


    tmp_dir = tempfile.mkdtemp(prefix='grow-')
    try:
      # Clone the repo.
      logging.info('cloning pod')
      clone_url = 'https://{}@github.com/{}.git'.format(
          github_access_token, repo)
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
      logging.info('deploying pod')
      ret_code = subprocess.call(
          ['grow', 'deploy', '--confirm', deploy_target, pod_path])
      if ret_code != 0:
        return {'success': False}
    finally:
      logging.info('removing %s', tmp_dir)
      shutil.rmtree(tmp_dir)

    return {'success': True}


class HelloWorldHandler(webapp2.RequestHandler):

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('hello, world!')


rpc.register_service('GrowDeployService', GrowDeployService)
app = webapp2.WSGIApplication([
    ('/_/rpc', rpc.JsonRpcHandler),
    ('/', HelloWorldHandler),
], debug=DEBUG)


def main(argv):
  from paste import httpserver
  httpserver.serve(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
  main(sys.argv)

