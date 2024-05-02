[Detailed information about this project is available here.](https://medium.com/@qwaq0213/managing-and-storing-content-from-urls-using-slackapp-and-chatgpt-20735c806d69)

# Managing and Storing Content From URLs Using Slackapp and ChatGPT
This project demonstrates how to create and deploy a Slackbot that retrieves URL links from articles shared within a Slack channel, extracts the paragraph text content from each shared link, sends the extracted text to ChatGPT for keyword generation and summarization, and stores the obtained information in a Google Sheets spreadsheet for easy access and organization.

**Prerequisites**
* Python 3.x
* Slack bot token (Bot User OAuth Token starting with xoxb)
* Slack channel ID
* OpenAI API key
* Google Cloud Platform account
* Google service account credential JSON file

**Installation**

1. Install the required Python packages:\
`pip install slack-sdk requests beautifulsoup4 openai gspread gspread-dataframe`

2. Set up your Slack app and obtain the bot token and channel ID.
3. Set up your OpenAI API key.
4. Set up your Google Cloud Platform account and create a service account credential JSON file.

**Usage**

1. Replace the placeholders in the code with your actual credentials:\
* `your_slack_bot_token`: Your Slack bot token
* `your_channel_id`: The ID of the Slack channel you want to retrieve data from
* `your-openai-api-key`: Your OpenAI API key
* `your-google-service-account-credential.json`: The path to your Google service account credential JSON file
* `your-spreadsheet-url`: The URL of your Google Sheets spreadsheet
* `your-current-working-sheet`: The name of the sheet within your spreadsheet

2. Run the script to retrieve the URLs, extract the text content, generate keywords and summaries using ChatGPT, and store the information in the specified Google Sheets spreadsheet.
3. Set up a Google Cloud Function to trigger the script execution via an HTTP request.
4. Add a Slash Command to your Slack app to trigger the Google Cloud Function.
5. Use the Slash Command in your Slack channel to initiate the process.

Note: You may encounter an error message from Slack stating, "/yourcommand failed with the error 'operation_timeout'." This occurs because Slack expects a response within 3 seconds. However, the process will continue, and the table will be updated despite the error message.

**Output**

The script will retrieve the URLs shared in the specified Slack channel, extract the text content from each URL, generate keywords and summaries using ChatGPT, and store the following information in a Google Sheets spreadsheet:
* Datetime
* User Name
* Title
* Tag 1
* Tag 2
* Tag 3
* Summary
* URL Link

The spreadsheet will be updated with the latest information each time the script is executed.
