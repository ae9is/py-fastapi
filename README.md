# py-fastapi

Boilerplate example for setting up a FastAPI endpoint with AWS Cognito authorisation.

Provides run scripts to bundle a Docker image and upload to ECR for later deployment.

## Setup

### Environment variables

Setup loading .env variables: https://direnv.net/

```bash
direnv allow
```

### Python

Uses Python 3.11. To easily switch between versions of python, consider setting up [pyenv](https://github.com/pyenv/pyenv).

[PDM](https://github.com/pdm-project/pdm) is used for proper dependency resolution and convenience scripts.

```bash
pip install pipx
pipx install pdm
```

Pre-commit is used for some commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### IAM Identity Center (SSO)

1. Enable IAM Identity Center following: https://aws.amazon.com/iam/identity-center/
1. Add user `admin`
1. Add group `Admins` to Groups
1. Add `admin` to `Admins`
1. Add a permission set `AdministratorAccess` based on the `AdministratorAccess` AWS managed policy
1. Assign the permission set to the `Admins` group under `AWS accounts → Assign users or groups`

### AWS CLI
1. Install AWS CLI

    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    # or update:
    $ sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
    ```

    (ref: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

1. Configure CLI session and login

    ```bash
    aws configure sso
    # enter info...
    aws sso login --sso-session admin
    ```

1. Check the resulting config at `~/.aws/config` and make sure it matches what you expect, for ex:

    ```
    [profile admin]
    region = us-east-1
    sso_session = admin
    sso_account_id = 123456789012
    sso_role_name = AdministratorAccess

    [sso-session admin]
    sso_region = us-east-1
    sso_start_url = https://my-sso-portal.awsapps.com/start
    sso_registration_scopes = sso:account:access
    ```

    (ref: https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html)

### Cognito

You'll need to setup an authentication provider for the FastAPI endpoints.

The FastAPI authentication library used is [fastapi-cloudauth](https://github.com/tokusumi/fastapi-cloudauth/), which supports AWS Cognito / Auth0 / Firebase Auth. The app is setup to use Cognito.

1. Create a new user pool in [Cognito in the AWS console](https://us-east-1.console.aws.amazon.com/cognito/v2/idp/user-pools).
1. Sign-in and sign-up options should be arbitrary, just don't enable public sign-up. You don't need any actual users or groups.
1. Once the user pool is created, select it and click "App integration" options.
1. Under "Domain" setup a new cognito domain
1. Create a resource server, with Resource server identifier `pyapi` and custom scope `user` for example. These values should match `.env` environment variable `COGNITO_AUTH_USER_SCOPE`, i.e. as in `pyapi/user` (resource_server_id/custom_scope_name).
1. Under "App client list" click "Create app client" &rarr; App type "Confidential client"
1. Client secret &rarr; Generate a client secret
1. Accept default and create
1. Once created, select the app client again and configure Hosted UI
    - Callback URLs: http://localhost
    - OAuth grant types: enable Client credentials grant
    - Custom scopes: `pyapi/user` (for example)

Once this setup is complete, note your:
- Custom Cognito user pool domain
- Custom scope
- App integration &rarr; app client &rarr; Client ID
- App integration &rarr; app client &rarr; Client secret

These will be needed to generate access tokens to authenticate requests against the api later.

## Install

```bash
pdm install-all
```

## Build

```bash
pdm docker-build
```

## Deploy

Set environment variables for Dockerfile images in `.env.dockerfile`. Make sure to set `PYTHON_ENV=production`, or unset it. The app needs some Cognito config to be set in `.env.dockerfile` so that it knows what user pool to authenticate against.

Make sure `AWS_REGION` and `AWS_ACCOUNT_ID` are set in `.env` environment variables. These are needed to login Docker to ECR.

Login Docker to AWS ECR:
```bash
pdm docker-login
```

Create a new private registry called `fastapi` (adjust the PDM run scripts in `pyproject.toml` to change this): https://console.aws.amazon.com/ecr/get-started

Push the built docker image to ECR:

```bash
pdm docker-push
```

No infrastructure is provisioned in code for this example.

An example deploying on Fargate:

1. Create a new ECS cluster, type Fargate.
1. Create an `ecsTaskExecutionRole` following: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html#create-task-execution-role
1. Attach the following inline policy to `ecsTaskExecutionRole` (in addition to AmazonECSTaskExecutionRolePolicy):
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup"
                ],
                "Resource": "*"
            }
        ]
    }
    ```
1. Create a new task definition from JSON file `task-definition.json`, editing the file with the `ecsTaskExecutionRole`'s ARN.
1. In the ECS cluster, create a new service:
    - Specify FARGATE_SPOT capacity provider
    - Select Task definition &rarr; Family: pyapi
    - Service name: fastapi
1. Edit security group config at: AWS ECS &rarr; Clusters &rarr; <cluster_name> &rarr; Services &rarr; <service_name> &rarr; Configuration and networking &rarr; Network configuration &rarr; Security groups
1. Edit inbound rules &rarr; Add new custom TCP inbound rule for port 5000, source "My IP" (or anywhere)
1. Grab the endpoint's Public ID from Tasks &rarr; <task_id> &rarr; Public IP

*Note: memory requirements for each task varies depending on what kind of model and job you're running! Check the task definition JSON file to adjust: `task-definition.json`.* 

## Run (local api)

Different pdm scripts exist for testing the endpoint locally:

- asgi: run the FastAPI app via an ASGI server, without docker
- docker-run fastapi: run the FastAPI app via the docker image

### Authentication

In order to authenticate against the FastAPI endpoints, you need to provide credentials. This section assumes a Cognito User Pool and App Client have already been setup previously [(see here)](#cognito), and is an example for using [Postman](https://www.postman.com/) from a [trusted client](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html#user-pool-settings-client-app-client-types) to side step having to setup any actual users and login in Cognito.

1. Create a new postman environment, and edit it, adding the following variables:
```
    client_id       <client_id_from_cognito_app_client>
    client_secret   <client_secret_from_cognito_app_client>
    token_url       https://<cognito_subdomain>.<aws_region>.amazoncognito.com/oauth2/token
    scope           pyapi/user (or whatever scope you wish, i.e. pyapi/write, pyapi/read, ..., matching the values configured in the Cognito App Client)
```
1. Create a new request
1. Click Authorization &rarr; OAuth 2.0 &rarr; Add auth data to Request Headers
1. Fill in the Configuration Options:
```
    Token Name             pyapi (arbitrary)
    Grant Type             Client credentials
    Access Token URL       {{token_url}}
    Client ID              {{client_id}}
    Client Secret          {{client_secret}}
    Scope                  {{scope}}
    Client Authentication  Send client credentials in body (arbitrary)
```
1. Click "Get New Access Token" and copy the access_token in the response body
1. Alternatively, you can just directly send a POST request yourself to the endpoint at `{{token_url}}`, specifying a `x-www-form-urlencoded` body:
```
    grant_type    client_credentials
    client_id     {{client_id}}
    client_secret {{client_secret}}
    scope         {{scope}}
```
1. Open a new request to the development endpoint at (for ex.) `GET http://localhost:5000/v1/healthz`
1. Click Authorization &rarr; OAuth 2.0 &rarr; Add auth data to Request Headers
1. Paste the access token into Current Token &rarr; Access Token, just above Header Prefix "Bearer"

## Test

Make sure to set the `.env` environment variables for [Cognito](#cognito).

Start up endpoint:
```bash
pdm docker-build
pdm docker-run
```

Then:
```bash
pdm test
```
