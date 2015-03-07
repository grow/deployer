# Deployer

Deployer is a service to deploy grow sites.

*NOTE*: Deployer is currently under development and is not yet ready for use.


### Install deployer

```
sudo python setup.py install
```

### Start the server

```
deployer start
```

Using a different port:

```
deployer --port=9999 start
```

### Authenticate

```
deployer auth --client_id=$GITHUB_CLIENT_ID --client_secret=$GITHUB_SECRET
```

### Add a webhook to trigger a grow deploy when code changes

```
deployer add_webhook --repo=user/project --deploy_target=default
```

Specify an access token to use for private repos

```
deployer add_webhook --repo=user/project --access_token=$GITHUB_ACCESS_TOKEN \
  --deploy_target=default
```

Specify a deploy target for a different branch

```
deployer add_webhook --repo=user/project --branch=dev --deploy_target=dev
```
