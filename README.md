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

### Listen for GitHub changes and trigger a deploy

```
deployer add_webhook --repo=github.com/user/project --deploy_target=default
```

### Specify an access token to use for private repos

```
deployer add_webhook --repo=github.com/user/project \
  --access_token=$GITHUB_ACCESS_TOKEN --deploy_target=default
```

### Specify a deploy target for a different branch

```
deployer add_webhook --repo=github.com/user/project --branch=dev \
  --deploy_target=dev
```
