# Mist Want To Talk
MWTT is a small python app to publish Mist Webhook messages to Slack or MsTeams channels.

It is composed of lightweight python web server ([Flask](https://github.com/pallets/flask)) and python code to process the webhook information and send it the Slack/MsTeams channels.

This script is available as is and can be run on any server with Python3. 

The script is also available as a Docker image. It is designed to simplify the deployment, and a script is available to automate the required images deployment.

* [Features](#features)
* [Mist Configuration](#mist-configuration)
* [Docker Deployment](#docker-image-deployment)
* [Source Code Deployment](#source-code-deployment)

## MIT LICENSE
 
Copyright (c) 2021 Thomas Munzer

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the  Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Features
* Send the messages to different slack channels depending on the severity level (can be configured):
<img src="https://github.com/tmunzer/mwtt/raw/master/._readme/img/slack_channel.png" width="50%">

* Send the messages to different MS Teams channels depending on the severity level (can be configured):
<img src="https://github.com/tmunzer/mwtt/raw/master/._readme/img/msteams_channel.png" width="50%">

* Send the messages to different Google Chat channels depending on the severity level (can be configured):
<img src="https://github.com/tmunzer/mwtt/raw/master/._readme/img/gchat_channel.png" width="50%">

# Mist Configuration
## Webhook Configuration
To get this script working, you will have to manually configure webhooks on your Mist account and enable the "audits", "alarms, "device-events" and/or "device-updowns" topics. This configuration can be done at the Organization level, or at the site level, depending on your needs.

For some topics, if they are enable at the Org and Site(s) levels, you may receive the same message multiple times.

This will tell Mist Cloud to send events (like AP Connected/Disconnected) to the MWTT FQDN. As of today (January, 2020), some topics like the "device-events" topics cannot be enabled directly from the Mist UI. This configuration can be done through Mist APIs. You can use the web UI to manage APIs by reaching https://api.mist.com/api/v1/orgs/:your_org_id/webhooks or https://api.eu.mist.com/api/v1/orgs/:your_org_id/webhooks (Be sure to replace ":your_org_id" first). Then you will be able to create a new webhook by using the following settings:

```json
    {
        "url": "https://<mwtt_server_fqdn>/<mwtt_url>",
        "topics": [
            "device-events"
        ],
        "enabled": true
    }
   ```


## SSL Certificate
In case you are using a Self-Signed certificate, be sure to configure the Webhook in the Mist Cloud to not validate the SSL certificate. This can be done by adding `"verify_cert": false` in the webhook configuration:
```json
    {
        "url": "https://<mwtt_server_fqdn>/<mwtt_url>",
        "topics": [
            "device-events"
        ],
        "verify_cert": false,
        "enabled": true
    }
   ```

## Secret
To improve the webhook security, Mist allows to configure a secret in the webhook configuration, which will add two HTTP headers: 
- `X-Mist-Signature-v2`: HMAC_SHA256(secret, body)
- `X-Mist-Signature`: HMAC_SHA1(secret, body)

To configure the secret in Mist, you just need to add the `"secret": "mysupersecret"` setting in the webhook configuration (please not this is just an example and we are recommanding to use something stronger than "mysupersecret"):
```json
    {
        "url": "https://<mwtt_server_fqdn>/<mwtt_url>",
        "topics": [
            "device-events"
        ],
        "secret": "mysupersecret",
        "enabled": true
    }
   ```

This App can be configured to validate the `X-Mist-Signature-v2` when receiving a new webhook, allowing to validate the origin and the content of the received webhook.
The secret is configured with the `mist_secret` parameter in the `config.py` file.

# How to use it

## Docker Image Deployment
You can easily deploy this application as a [Docker](https://www.docker.com/) image. The image is publicly available on Docker Hub at https://hub.docker.com/r/tmunzer/mwtt/.
This is the preferred way if you want to use the application.

In this case, you can choose to 
* manually deploy the image and create the container. In this case the Mwtt container will listen for HTTP messages on port `TCP51361`
* use docker-compose to deploy the mwtt container and Nginx container acting as a reverse proxy. This is the prefered way and will allow you to easily manage the SSL Certificates with Nginx. In this case Nginx will listen on port `TCP443` (HTTPS) and forward the request to the Mwtt container based on the HTTP Host (see below)

### Docker-Compose Step by Step procedure
1. create a folder used to store the permanent data (config file, certificates, ...). In this example, we'll use `/home/demo/docker`
2. in this folder, create a `mwtt` and a `nginx` folders
3. in `/home/demo/docker/mwtt/`, create the `config.py` file to configure the application. You can find an example [here](https://github.com/tmunzer/mwtt/blob/master/src/config_example.py)
4. in `/home/demo/docker/nginx/`, create or copy SSL certificate and key Nginx will use for HTTPS communication. The files names MUST be `foo.bar.com.crt` and `foo.bar.com.key`, where `foo.bar.com` is the Mwtt Application FQDN (for example, if Mist is sending the webhooks to `mwtt.mycorp.com`, the certificate filename must be `mwtt.mycorp.com.crt` and the key filename must be `mwtt.mycorp.com.key`)
5. download the [docker-compose.yaml file](https://github.com/tmunzer/mwtt/blob/master/docker-compose.yaml), and edit the required paramters
   - line 9 : replace `<your_folder>` with the folder created in step 1. In this example, line 9 will be `/home/demo/docker/nginx:/etc/nginx/certs:ro`
   - line 20: replace `<your_app_hostname>` with the application FQDN (same as step 4). Based on the example used in step 4, line 20 will be `- VIRTUAL_HOST=mwtt.mycorp.com`
   - line 22: replace `<your_folder>` with the folder created in step 1. In this example, line 9 will be `/home/demo/docker/mwtt/config.py:/app/config.py:ro`
6. start the containers with the docker-compose command: from the folder where you downloaded the `docker-compose.yaml` file, use the command `docker-compose up`. This will download the required docker images, start the containers, and display the logs on the console. After a few seconds, your Mwtt is ready to receive Webhooks messages from Mist

**Note:**
When using the command `docker-compose up`, the logs are displayed, and using `Crtl + C` will stop the containers. If you want to start and run the containers in background, please use the command `docker-compose up -d`

## Source Code Deployment
It is possible to start the application directly from the source code. This is the prefered way if you want to bring modification to the code.

### Step by step procedure
1. install [Python](https://www.python.org/) and Pip
2. Clone the repository on your computer
3. from the `src` folder, use the `python3 -m pip install -r requirements.txt` command to install the required dependencies (exact command may vary depending on your OS)
4. create a `config.py` file in the `src` folder to configure the application. You can find an example [here](https://github.com/tmunzer/mwtt/blob/master/src/config_example.py)
5. run the app from the `src` folder with the command `python3 ./mwtt.py` (exact command may vary depending on your OS)


