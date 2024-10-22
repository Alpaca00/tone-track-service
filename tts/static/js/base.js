import { config } from './config.js';

class Config {
    constructor(config) {
        this.host = config.host;
        this.port = config.port;
        this.serverUrl = `http://${this.host}:${this.port}/api/v1/proxy-sentiment-analysis`;
    }

    /**
     * Get the server URL for the sentiment analysis API.
     * @returns {string} The full server URL.
     */
    getServerUrl() {
        return this.serverUrl;
    }
}

const conf = new Config(config);

$(document).ready(function () {
    $('#sentiment-form').on('submit', function (e) {
        e.preventDefault();
        const userInput = $('#input-text').val();

        $.ajax({
            url: conf.getServerUrl(),
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ text: userInput, sentiment_type: 'all' }),
            success: function (response) {
                response = JSON.parse(response);
                $('#info-text').text(response.sentiment_result);
                $('#input-text').val('');
            },
            error: function () {
                $('#info-text').text('Error processing request.');
                $('#input-text').val('');
            }
        });
    });
});
