# Upwork Job Alert Bot

This bot automatically scans Upwork job postings and sends you alerts via Telegram when new jobs matching your criteria are posted.

## Features

- Monitors search URLs for new job postings
- Sends detailed Telegram notifications with job information
- Tracks previously seen jobs to avoid duplicate alerts
- Works with proxy servers for enhanced anonymity
- Saves debug information (optional) for troubleshooting

## Setup Instructions

### Prerequisites

You need to have Python installed on your computer. If you don't have Python installed:

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Install it, making sure to check "Add Python to PATH" during installation

### Installation Steps

1. **Download the project**

   - Either download the ZIP file and extract it, or clone the repository if you know how to use Git
   - Open a terminal/command prompt and navigate to the folder where you extracted the files

2. **Install required packages**

   - Run the following command to install the required packages:
     ```
     pip install -r requirements.txt
     ```

3. **Set up a Telegram bot**

   - Open Telegram and search for "BotFather"
   - Start a chat with BotFather and create a new bot with the command `/newbot`
   - Follow the instructions to set a name and username for your bot
   - Once created, you'll receive a token that looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
   - Start a chat with your new bot and send it any message

4. **Get your Telegram Chat ID**

   - Open your web browser and go to: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
     (replace `<YOUR_BOT_TOKEN>` with the token you received)
   - Look for the `"chat":{"id":123456789}` section in the response
   - The number shown as "id" is your Chat ID

5. **Configure the script**

   - Open the `upwork-job-alert-bot.py` file in a text editor
   - Find the following lines and update them with your information:

     ```python
     TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
     TELEGRAM_CHAT_ID = "your_telegram_chat_id_here"

     SEARCH_URLS = [
         "https://www.upwork.com/nx/search/jobs/?q=your_search_terms_here",
     ]
     ```

   - You can add multiple search URLs to monitor different types of jobs
   - Set the `USE_PROXY` to `False` if you don't want to use a proxy, or configure your own proxy settings if needed

## Running the Bot

1. **Start the bot**

   - Open a terminal/command prompt
   - Navigate to the folder containing the script
   - Run the script with:
     ```
     python upwork-job-alert-bot.py
     ```
   - The bot will start running and checking for new jobs

2. **For Windows users**

   - You can also create a batch file (`.bat`) to run the script:
     1. Create a new text file in the same folder as the script
     2. Add the following line:
        ```
        python upwork-job-alert-bot.py
        pause
        ```
     3. Save the file as `start_bot.bat`
     4. Double-click this file to run the bot

3. **For macOS/Linux users**
   - You can create a shell script to run the bot:
     1. Create a new text file in the same folder as the script
     2. Add the following lines:
        ```bash
        #!/bin/bash
        python3 upwork-job-alert-bot.py
        ```
     3. Save the file as `start_bot.sh`
     4. Make it executable with:
        ```
        chmod +x start_bot.sh
        ```
     5. Run the script with:
        ```
        ./start_bot.sh
        ```

## Customizing the Bot

- **Check interval**: Change the `CHECK_INTERVAL` value (in minutes) to control how often the bot checks for new jobs
- **Debug options**: Set `SAVE_SEARCH_HTML`, `SAVE_POST_HTML`, and `SAVE_TELEGRAM_MESSAGE` to `True` or `False` to enable/disable saving debug information

## Troubleshooting

- **Chrome Driver issues**: If you see errors related to Chrome driver, make sure Chrome browser is installed on your system
- **Parsing errors**: If the bot isn't finding jobs, the Upwork website structure might have changed. Enable debug options to save HTML for inspection
- **Telegram errors**: Double-check your bot token and chat ID; make sure you've started a chat with your bot

## Running the Bot Continuously

To keep the bot running even after closing your terminal:

- **On Windows**: Consider setting up a scheduled task
- **On macOS/Linux**: Consider using `nohup` or setting up a systemd service

## Important Notes

- Using automated tools to scrape websites may violate terms of service
- Use proxies and reasonable delays to avoid being blocked
- This bot is for educational purposes only
