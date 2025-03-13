# Upwork Job Search Alerts

This tool monitors Upwork for new job postings matching your search criteria and sends real-time alerts to your Telegram account. Never miss out on potential job opportunities again!

![Example telegram message](./assets/preview.jpeg)

## Features

- 🔍 Monitor multiple custom Upwork job search URLs
- 🔔 Get instant Telegram notifications for new job postings
- 💰 View complete job details (budget, client info, required skills)
- 🌐 Support for proxy connections to avoid rate limiting
- 🤖 Automated regular checking with customizable intervals
- 🧠 Smart tracking to avoid duplicate notifications

## Prerequisites

Before installing this tool, you need to have:

1. **Python 3.8 or higher** installed on your system
2. **A Telegram account** to receive notifications
3. **Chrome/Chromium browser** installed (used by the Selenium web driver)

## Installation Guide

### Step 0: Ensure Python and pip are working correctly

#### Windows

1. Check if Python is installed:

   - Open Command Prompt (search for "cmd" in the Start menu)
   - Type `python --version` and press Enter
   - You should see something like "Python 3.8.x" or higher
   - If you see "Command not found" or a version lower than 3.8, you need to [install Python](https://www.python.org/downloads/windows/)

2. Verify pip is working:

   - In Command Prompt, type `pip --version` and press Enter
   - You should see pip version information

3. If Python is installed but commands aren't recognized:
   - This usually means Python isn't in your PATH
   - Either reinstall Python and check "Add Python to PATH" during installation
   - Or use the full path to Python:
     ```
     C:\Users\YourUsername\AppData\Local\Programs\Python\Python38\python.exe
     C:\Users\YourUsername\AppData\Local\Programs\Python\Python38\Scripts\pip.exe
     ```

#### macOS

1. Check Python installation:

   - Open Terminal (from Applications > Utilities)
   - Type `python3 --version` and press Enter
   - You should see something like "Python 3.8.x" or higher
   - Note: On macOS, use `python3` and `pip3` commands (not `python` and `pip`)

2. Verify pip is working:

   - In Terminal, type `pip3 --version`

3. If Python isn't installed or is outdated:
   - Install [Homebrew](https://brew.sh/) if you don't have it:
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - Install Python with Homebrew:
     ```
     brew install python
     ```

#### Linux (Ubuntu/Debian)

1. Check Python installation:

   - Open Terminal
   - Type `python3 --version` and press Enter

2. Verify pip is working:

   - In Terminal, type `pip3 --version`

3. If Python isn't installed or is outdated:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

#### Linux (CentOS/RHEL/Fedora)

1. Check Python installation:

   - Open Terminal
   - Type `python3 --version`

2. Verify pip is working:

   - In Terminal, type `pip3 --version`

3. If Python isn't installed or is outdated:
   ```bash
   sudo dnf install python3 python3-pip  # For Fedora/CentOS 8+
   # OR
   sudo yum install python3 python3-pip  # For older CentOS/RHEL
   ```

Now that you've verified Python and pip are working correctly, you can proceed with the installation.

### Step 1: Download the Project

If you're familiar with Git:

```bash
git clone git@github.com:jmdoan1/upwork-job-search-alerts.git # or https://github.com/jmdoan1/upwork-job-search-alerts.git
cd upwork-job-search-alerts
```

If you're not familiar with Git:

1. Click the green "Code" button at the top of this GitHub page
2. Select "Download ZIP"
3. Extract the ZIP file to a folder on your computer
4. Open a command prompt or terminal and navigate to that folder

### Step 2: Install Python Dependencies

> **Note**: The included run scripts ([run.sh](run.sh) for macOS/Linux or [run.bat](run.bat) for Windows) handle all of this automatically. See the "Running the Tool" section for details.

Modern Python installations often prevent direct installation of packages to avoid breaking system dependencies. The best practice is to use virtual environments:

#### Windows

```bash
# Create a virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies (notice we just use pip, not pip3 when in a virtual environment)
pip install -r requirements.txt
```

#### macOS/Linux

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

When you're done using the virtual environment, you can deactivate it:

```bash
deactivate
```

### Step 3: Set Up Your Telegram Bot

The tool sends notifications through Telegram, so you'll need to create a bot:

1. Open Telegram and search for **@BotFather**
2. Start a chat with BotFather and send the message: `/newbot`
3. Follow the instructions to name your bot
4. **Important**: Save the API token provided by BotFather (it looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

Next, you need to get your Telegram chat ID:

1. Search for **@userinfobot** in Telegram
2. Start a chat with this bot, and it will reply with your account information
3. Copy your ID number

### Step 4: Create Your Configuration File

1. In the project folder, create a file named `.env` based on the `.envexample` file
2. Open the `.env` file in a text editor and fill in your details:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

SEARCH_URLS=["https://www.upwork.com/nx/search/jobs"]

PROXY_LIST=[]
```

### Step 5: Set Up Your Upwork Search URLs

To customize what jobs you monitor:

1. Go to [Upwork Jobs](https://www.upwork.com/nx/search/jobs)
2. Enter your search terms, select filters (categories, experience level, etc.)
3. After applying all filters, copy the complete URL from your browser's address bar
4. Add this URL to the `SEARCH_URLS` array in your `.env` file
5. You can add multiple URLs by separating them with commas:

```
SEARCH_URLS=["https://www.upwork.com/nx/search/jobs?q=python&sort=recency", "https://www.upwork.com/nx/search/jobs?q=django&sort=recency"]
```

## Using Proxies (Optional)

Using proxies can help prevent rate limiting or IP blocking. If you don't need proxies, you can leave the `PROXY_LIST` empty.

If you want to use proxies, here are some examples of supported formats:

- "socks5://username:password@dallas.us.socks.nordhold.net:1080",
- "socks5://atlanta.us.socks.nordhold.net:1080",
- "http://username:password@proxy.example.com:8080",
- "http://192.168.1.1:8080",
- "https://proxy.example.com:3128"

```
PROXY_LIST=[ "socks5://username:password@dallas.us.socks.nordhold.net:1080", "socks5://atlanta.us.socks.nordhold.net:1080", "http://username:password@proxy.example.com:8080", "http://192.168.1.1:8080", "https://proxy.example.com:3128"]
```

You can obtain proxies from various proxy service providers such as:

- NordVPN
- ExpressVPN
- Bright Data (formerly Luminati)
- SmartProxy
- OxyLabs

Most of these services will provide instructions on how to format their proxy addresses for your use.

## Running the Tool

### Easy Setup & Run (Recommended)

The project includes convenience scripts that handle everything for you automatically:

1. **Make the script executable** (macOS/Linux only):

   ```bash
   chmod +x run.sh
   ```

2. **Run the script**:
   - On Windows: Double-click `run.bat` or run it from Command Prompt
   - On macOS/Linux: `./run.sh`

These scripts will:

- Create a virtual environment if one doesn't exist
- Install/update all required dependencies
- Run the Upwork job search alerts tool

### Manual Setup (Advanced)

If you prefer to set things up manually:

#### Windows

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python upwork-job-search-alerts.py

# When done, deactivate the environment
deactivate
```

#### macOS/Linux

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the script
python upwork-job-search-alerts.py

# When done, deactivate the environment
deactivate
```

### Running in the Background

#### Windows

1. Create a batch file named `start_upwork_monitor.bat` with the following content:
   ```batch
   @echo off
   call venv\Scripts\activate
   start /min cmd /c "python upwork-job-search-alerts.py > upwork_log.txt 2>&1"
   ```
2. Double-click this file to run the script in the background

#### macOS/Linux

1. Using nohup (keeps running after you close terminal):
   ```bash
   source .venv/bin/activate
   nohup python upwork-job-search-alerts.py > upwork_log.txt 2>&1 &
   ```
2. To stop the process later:
   ```bash
   ps aux | grep upwork-job-search-alerts.py
   kill [PID]  # Replace [PID] with the process ID you found
   ```

The script will:

1. Check your search URLs for new job postings
2. Send you Telegram notifications for new matches
3. Continue to run and check periodically (default: every 3 minutes)

You can keep it running in the background or on a server for continuous monitoring.

## Customization Options

You can modify these parameters in the `upwork-job-search-alerts.py` file:

- `CHECK_INTERVAL = 3` - Time between checks in minutes
- `MAX_DESCRIPTION_LENGTH = 300` - Maximum length of job descriptions in notifications before
- `SAVE_SEARCH_HTML = False` - Whether to save search page HTML for debugging
- `SAVE_POST_HTML = False` - Whether to save job posting HTML for debugging
- `SAVE_TELEGRAM_MESSAGES = False` - Whether to save job posting HTML for debugging
- `USE_PROXY = True` - Whether or not to use the proxy list from the .env file

## Troubleshooting

**Problem**: No notifications are being received

- Verify your Telegram bot token and chat ID are correct
- Make sure you've started a conversation with your bot on Telegram (send a `/start` message to your bot)
- Check your internet connection and proxy settings if using proxies

**Problem**: Script crashes or doesn't load jobs

- Make sure Chrome/Chromium is installed
- Try running without proxies first
- Check the console for specific error messages

**Problem**: Getting rate limited by Upwork

- Increase the check interval
- Use proxies
- Reduce the number of search URLs you're monitoring

**Problem**: "Command not found" when running pip or python

- See the platform-specific instructions in Step 0
- Make sure Python is installed correctly and added to your PATH

**Problem**: Chrome driver fails to start

- Ensure Chrome or Chromium is installed on your system
- Try reinstalling the selenium package:
  ```bash
  pip install --upgrade selenium webdriver-manager
  ```
- For Linux users, you may need additional dependencies:
  ```bash
  sudo apt install chromium-browser chromium-chromedriver  # Ubuntu/Debian
  sudo dnf install chromium chromedriver  # Fedora
  ```

**Problem**: Browser automation detected by Upwork

- Try adjusting the `USER_AGENTS` list in the script with more recent browser user agent strings
- Use proxies to rotate IP addresses
- Increase the random delays in the script

**Problem**: "externally-managed-environment" error when installing packages

- This is a protective feature in newer Python versions
- Use a virtual environment as described in the setup instructions
- Or use the provided run scripts which handle virtual environments automatically

**Problem**: Issues installing lxml or other compiled packages

- The provided run scripts attempt multiple installation methods
- On macOS: You may need to install system dependencies: `brew install libxml2 libxslt`
- On Ubuntu/Debian: `sudo apt-get install python3-lxml libxml2-dev libxslt1-dev`
- On Fedora/RHEL: `sudo dnf install python3-lxml libxml2-devel libxslt-devel`
- On Windows: Download a precompiled wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml that matches your Python version

## Technical Details

This tool uses:

- **Selenium** with Chrome WebDriver for browsing Upwork
- **BeautifulSoup** for parsing HTML content
- **Requests** for sending Telegram notifications
- **Python dotenv** for configuration

The script maintains a history of seen jobs in `job_history.pkl` to avoid sending duplicate notifications.

## Legal Considerations

Please use this tool responsibly and in accordance with Upwork's Terms of Service. This script is intended for personal use to help freelancers find relevant opportunities more efficiently.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
