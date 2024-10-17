# Service Tone Track

**A Basic HTTP Server for Tracking Sentiment of Text Data.**

---

## 📖 Description

**Service Tone Track** is a heavyweight HTTP server designed to track the sentiment of text data. 

Leveraging the power of the [NLTK](https://www.nltk.org/) and [Transformers](https://huggingface.co/transformers/) libraries, this service provides a straightforward way to analyze the sentiment of any given text.

### 🌐 Features

- **Sentiment Analysis**: Accurately determines the sentiment (positive, negative, neutral) of the input text.
- **tone-track**: The Slack App that integrates with this service to provide sentiment analysis for Slack messages.

---

### 🛠️ Installation instructions on local machine

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

### 📩 Slack App Integration
TODO: Add Slack app integration. Stay tuned for updates on how to integrate this service with your Slack applications for real-time sentiment tracking!

```commandline
echo "SLACK_BOT_OAUTH_TOKEN=YOUR_SLACK_BOT_AUTH_TOKEN" >> .env
```

---

### 📄 License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

---

### ❤️ DONATE

If you found this project helpful or you learned something from the source code and want to thank me, please supporting this [Charity](DONATE.md)
