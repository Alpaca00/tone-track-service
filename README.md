# Service Tone Track

**A Basic HTTP Server for Tracking Sentiment of Text Data.**

---

## 📖 Description

**Service Tone Track** is a heavyweight HTTP server designed to track the sentiment of text data. 

Leveraging the power of the [NLTK](https://www.nltk.org/) and [Transformers](https://huggingface.co/transformers/) libraries, this service provides a straightforward way to analyze the sentiment of any given text.

### 🌐 Features

- **Sentiment Analysis**: Accurately determines the sentiment (positive, negative, neutral) of the input text.
- **tone-track**: The Slack App that integrates with this service to provide sentiment analysis for Slack messages.

**Models supported only english language for now:**
- **VADER**: A rule-based sentiment analysis tool that is specifically attuned to sentiments expressed in social media.
- **BERT**: A transformer model that is fine-tuned to perform sentiment analysis on text data.

---

### 🛠️ Installation instructions and running the server on your local machine

To install the required dependencies, run the following commands:

```bash
git clone https://github.com/Alpaca00/tone-track-service.git
cd tone-track-service
echo "API_KEY=YOUR_API_KEY" > .env  # Replace YOUR_API_KEY with your random API key
docker-compose up
```

When the server is up and running, you can access the API at `localhost:80`
```curl
curl --location 'http://0:80/api/v1/sentiment-analysis' \
--header 'Content-Type: application/json' \
--header 'Authorization: YOUR_API_KEY' \
--data '{"text": "Your hard work is noticed, and it brings results!", "sentiment_type": "vader"}'
```

A successful response will look like this:
```json
{"text":"Your hard work is noticed, and it brings results!","sentiment_result":"negative"}
```


---

### 📩 Slack App Integration and running the Slack App on your local machine

[Ngrok](https://ngrok.com/) is required to expose the local server to the internet.

Run the following command to expose the local server to the internet:
```bash
docker run --net=host -it -e NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN ngrok/ngrok:latest http 80
```

To integrate the Slack App with the service, you need to create a Slack App and install it on your workspace.

1. Create a new Slack App [here](https://api.slack.com/apps?new_app=1).
2. Navigate to the `OAuth & Permissions` section and add the following scopes:
    - `chat:write`
    - `chat:write.public`
    - `channels:read`
    - `channels:history`
    - `commands`
3. Navigate to the `Interactivity & Shortcuts` section and add the following request URL:
```text
https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/interactions
```
4. Navigate to the `Enable Events` section and add the following request URL:
```
https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/events
```
5. Navigate to the `Slash Commands` section and create a new commands:

I: Add a workspace and sentiment analysis message
```text
    - Command: /tt-add-workspace
    - Request URL: https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/commands
    - Short Description: Add a workspace and sentiment analysis message
```

   II: Get information about a workspace
```text
    - Command: /tt-info-workspace
    - Request URL: https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/commands
    - Short Description: Get information about a workspace
```

   III: Update a workspace and sentiment analysis message
```text
     - Command: /tt-update-workspace
     - Request URL: https://YOUR_NGROK_SUBDOMAIN.ngrok.io/api/v1/slack/commands
     - Short Description: Update a workspace and sentiment analysis message
```
6. Install the app to your workspace.
7. Add environment variables from the Slack App to the `.env` file:
```bash
# Replace the placeholders below with your actual Slack App credentials and PostgreSQL configuration values to ensure the security of your data
echo "SLACK_BOT_OAUTH_TOKEN=YOUR_SLACK_BOT_AUTH_TOKEN" >> .env
echo "SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET" >> .env
echo "POSTGRES_USER=YOUR_POSTGRES_USER" >> .env
echo "POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD" >> .env
# Don't change this values
echo "POSTGRES_DB=tts" >> .env
echo "POSTGRES_HOST=postgres" >> .env
```
8. Run the following command to start the Slack App:
```bash
docker compose dowm --rmi all
docker service prune -f
docker-compose up
```

---

### 📄 License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

### ❤️ DONATE

If you found this project helpful or you learned something from the source code and want to thank me, please supporting this [Charity](DONATE.md)
