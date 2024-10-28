# Service Tone Track

**A Basic HTTP Server for Tracking Sentiment of Text Data.**

**Website:** [https://tone-track.uno](https://tone-track.uno)

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) &nbsp;
[![CI](https://github.com/Alpaca00/tone-track-service/actions/workflows/ci.yml/badge.svg)](https://github.com/Alpaca00/tone-track-service/actions/workflows/ci.yml) &nbsp;
[![CD](https://github.com/Alpaca00/tone-track-service/actions/workflows/cd.yml/badge.svg?branch=master)](https://github.com/Alpaca00/tone-track-service/actions/workflows/cd.yml) &nbsp;
[![CD | Kubernetes](https://github.com/Alpaca00/tone-track-service/actions/workflows/cd-k8s.yml/badge.svg?branch=master)](https://github.com/Alpaca00/tone-track-service/actions/workflows/cd-k8s.yml)


## 📖 Description

**Service Tone Track** is a heavyweight HTTP server designed to track the sentiment of text data. 

Leveraging the power of the [NLTK](https://www.nltk.org/) and [Transformers](https://huggingface.co/transformers/) libraries, this service provides a straightforward way to analyze the sentiment of any given text.

### 🌐 Features

- **sentiment analysis service**: Accurately determines the sentiment (positive, negative, neutral) of the input text.
- **tone-track**: The Slack App that integrates with this service to provide sentiment analysis for Slack messages.
- **web interface**: A simple web interface that allows users to interact with the sentiment analysis service.

**Models supported only english language for now:**
- **VADER**: A rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media.
- **BERT**: A transformer model that is fine-tuned to perform sentiment analysis on text data.

---

### 🛠️ Installation instructions and running the server on your local machine

To install the required dependencies, run the following commands:

```bash
chmod +x ./generate_env.sh;
./generate_env.sh;
docker compose --file user-setup.yml up -d
```

When the server is up and running, you can access the API at `localhost:80`

Replace `<YOUR API KEY FROM .env FILE volume>` with the API key from the `.env` file in the root directory.

```curl
curl --location 'http://0:80/api/v1/sentiment-analysis' \
--header 'Content-Type: application/json' \
--header 'Authorization: <YOUR API KEY FROM .env FILE volume>' \
--data '{"text": "Your hard work is noticed, and it brings results!", "sentiment_type": "vader"}'
```

A successful response will look like this:
```json
{"text":"Your hard work is noticed, and it brings results!","sentiment_result":"negative"}
```


---

### 📩 Demo integration and running your Slack App on local machine

To integrate the Slack App with the service, you need to create a Slack App and install it on your workspace.

1. Create a new Slack App [here](https://api.slack.com/apps?new_app=1) and select from scratch.
2. Navigate to the `OAuth & Permissions` section and add the following scopes:

Bot Token Scopes:
 - `chat:write`
 - `chat:write.public`
 - `channels:read`
 - `commands`

User Token Scopes:
 - `channels:history`

Install the app to your workspace by `Install to Workspace` button.

4. Add the following environment variables to the `.env` file in the root directory:
- `SLACK_SIGNING_SECRET`  - your Slack App's signing secret from the `Basic Information` section.
- `SLACK_BOT_OAUTH_TOKEN` - your Slack App's bot token from the `OAuth & Permissions` section.

5. Run the following command to expose the local server to the internet:

[Ngrok](https://ngrok.com/) is required to expose the local server to the internet.

Required environment variable:
- `NGROK_AUTHTOKEN` - your Ngrok auth token from [here](https://dashboard.ngrok.com/get-started/your-authtoken)
```bash
docker run --net=host -it -e NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN ngrok/ngrok:latest http 80
```
6. Navigate to the `Interactivity & Shortcuts` section of the Slack and add the following request URL:

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.

Example: `https://0154-95-160-47-60.ngrok-free.app/api/v1/slack/interactions`

```text
https://YOUR_NGROK_SUBDOMAIN.ngrok-free.app/api/v1/slack/interactions
```
7. Navigate to the `Enable Events` section and add the following request URL:

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.
```
https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/events
```
**Note:** trouble with save button, look at the [Slack Forum](https://forums.slackcommunity.com/s/question/0D53a000092sM1LCAU/save-changes-button-in-event-subscription-of-apislackcom-isnt-working-whenever-one-clicks-on-it-it-just-selects-something-else-on-the-screen?language=en_US) for more information.

8. Navigate to the `Slash Commands` section and create a new commands:

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.

I: Add | Update sentiment analysis message to channel
```text
    - Command: /tt-add-message
    - Request URL: https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/commands
    - Short Description: Add | Update sentiment analysis message to channel
```

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.

   II: Retrieve sentiment analysis message from channel
```text
    - Command: /tt-read-message
    - Request URL: https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/commands
    - Short Description: Retrieve sentiment analysis message from channel
```

**Well done!** You have successfully integrated the Slack App with service.

You can now test the app by sending negative message in channel and bot identifies the sentiment and reply to you.

---

### 📦 Deployment

#### Kubernetes
To deploy the service to Kubernetes cluster, you can use the Helm chart provided in the [devops/helm](devops/helm) directory.

For detailed instructions, refer to the [Helm README](devops/helm/README.md).


#### Docker Compose (cloud instance)
Alternatively, if you are using Docker Compose, you can deploy the service using the [user-setup.yml](user-setup.yml) file provided in the root directory.


SSL certificate are required to configure the Slack App. You can generate them using this [guide](https://mindsers.blog/en/post/https-using-nginx-certbot-docker/) and modify [user-setup.yml](user-setup.yml) and [nginx](nginx/conf/demo/user-setup.conf) files.


##### Don't forget to update configuration settings by new URL in the Slack App settings after deployment.


---

### 📄 License
This project is licensed under the [Apache License](LICENSE) - see the LICENSE file for details.

---

### ❤️ DONATE

If you found this project helpful or you learned something from the source code and want to thank me, please supporting this [Charity](DONATE.md)

---
### 📧 Contact

If you have any questions, suggestions, or need help, feel free to contact me at [support](mailto:support.tone-track.uno@gmail.com)