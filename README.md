# Service Tone Track

**A Basic HTTP Server for Tracking Sentiment of Text Data.**

**Website:** [https://tone-track.uno](https://tone-track.uno)

---

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
docker compose --file user-setup.yml up -d && \
docker exec tone-track-demo /bin/sh -c "cat ./.env" | tr -d '\r' > env.txt
```

When the server is up and running, you can access the API at `localhost:80`
```curl
curl --location 'http://0:80/api/v1/sentiment-analysis' \
--header 'Content-Type: application/json' \
--header 'Authorization: <YOUR API KEY FROM env.txt or .env FILE volume>' \
--data '{"text": "Your hard work is noticed, and it brings results!", "sentiment_type": "vader"}'
```

A successful response will look like this:
```json
{"text":"Your hard work is noticed, and it brings results!","sentiment_result":"negative"}
```


---

### 📩 Demo integration and running your Slack App on local machine

To integrate the Slack App with the service, you need to create a Slack App and install it on your workspace.

1. Create a new Slack App [here](https://api.slack.com/apps?new_app=1).
2. Navigate to the `OAuth & Permissions` section and add the following scopes:

Bot Token Scopes:
 - `chat:write`
 - `chat:write.public`
 - `channels:read`
 - `commands`

User Token Scopes:
 - `channels:history`


3. Run the following command to start working with the Slack App:

If haven't already, create `.env` file in the root directory of the project with the following command:
```bash
sh generate_env.sh || exit o
```
Add the following environment variables to the `.env` file or add them to the command `docker compose --file user-setup.yml up -d` by adding `-e` flag:
- `SLACK_SIGNING_SECRET`  Your Slack App's signing secret from the `Basic Information` section.
- `SLACK_BOT_OAUTH_TOKEN` Your Slack App's bot token from the `OAuth & Permissions` section.

```bash
docker compose dowm --rmi all
docker service prune -f
docker compose --file user-setup.yml up -d
```

4. Run the following command to expose the local server to the internet:

[Ngrok](https://ngrok.com/) is required to expose the local server to the internet.

Required environment variable:
- `NGROK_AUTHTOKEN` Your Ngrok Auth Token from [here](https://dashboard.ngrok.com/get-started/setup)
```bash
docker run --net=host -it -e NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN ngrok/ngrok:latest http 80
```
5. Navigate to the `Interactivity & Shortcuts` section and add the following request URL:

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.

```text
https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/interactions
```
6. Navigate to the `Enable Events` section and add the following request URL:

Replace `YOUR_NGROK_SUBDOMAIN` with your Ngrok subdomain.
```
https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/events
```
7. Navigate to the `Slash Commands` section and create a new commands:

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

8. Install the app to your workspace.
---

### 📄 License
This project is licensed under the [Apache License](LICENSE) - see the LICENSE file for details.

---

### ❤️ DONATE

If you found this project helpful or you learned something from the source code and want to thank me, please supporting this [Charity](DONATE.md)

---
### 📧 Contact

If you have any questions, suggestions, or need help, feel free to contact me at [support](mailto:support.tone-track.uno@gmail.com)