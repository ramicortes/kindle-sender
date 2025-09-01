# Kindle Article Sender

A Python application that extracts articles from web URLs or local HTML files and sends them directly to your Kindle device for distraction-free reading. The tool generates ePub files and can either send them via email to your Kindle or save them locally.

## Features

- 📖 **Extract content from web URLs** - Clean article extraction with fallback methods
- 📄 **Process local HTML files** - Convert saved HTML articles to ePub format
- 📧 **Send directly to Kindle** - Automated email delivery to your Kindle device
- 📚 **Generate ePub files** - Create properly formatted ePub files for offline reading
- 🎯 **Interactive mode** - User-friendly terminal interface with arrow key navigation
- ⚡ **Command-line mode** - Batch processing and automation support
- 🔧 **Domain-specific handling** - Optimized extraction for different websites

## Prerequisites

- Python 3.6 or higher
- A valid email account (Gmail recommended for SMTP settings)
- Your Kindle email address (found in your Amazon account settings)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd "Kindle Sender"
```

Or download and extract the ZIP file to your desired location.

### 2. Install Required Dependencies

Install the required Python packages:

```bash
pip install requests beautifulsoup4 python-dotenv blessed ebooklib
```

**Optional dependencies** (for enhanced article extraction):
```bash
pip install newspaper3k
```

### 3. Configure Email Settings

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your email configuration:
   ```bash
   # Email Configuration
   FROM_EMAIL=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   KINDLE_EMAIL=your_kindle_email@kindle.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587

   # Directory Configuration (optional)
   HTML_ARTICLES_DIR=./html_articles
   EPUB_OUTPUT_DIR=./epub_output
   ```

### 4. Setup Email Authentication

**For Gmail users:**
1. Enable 2-factor authentication on your Google account
2. Generate an "App Password" specifically for this application:
   - Go to Google Account settings → Security → 2-Step Verification → App passwords
   - Select "Mail" and generate a password
   - Use this app password in the `EMAIL_PASSWORD` field (not your regular Gmail password)

**For other email providers:**
- Update `SMTP_SERVER` and `SMTP_PORT` according to your provider's settings
- Ensure SMTP access is enabled for your account

### 5. Find Your Kindle Email Address

1. Go to [Amazon's Manage Your Content and Devices](https://www.amazon.com/hz/mycd/myx)
2. Select your Kindle device
3. Find the email address (usually ends with `@kindle.com`)
4. Add your sender email to the approved list in your Amazon account settings

## Usage

### Interactive Mode (Recommended)

Simply run the application without any arguments to start the interactive interface:

```bash
python kindle_sender.py
```

The interactive mode provides:
- Arrow key navigation through menus
- Real-time article extraction preview
- Step-by-step guidance through the process
- Help overlay (press 'h' at any time)

### Command Line Mode

For automation and batch processing:

**Send article from URL:**
```bash
python kindle_sender.py "https://example.com/article"
```

**Process local HTML file:**
```bash
python kindle_sender.py --file "path/to/article.html"
```

**Generate ePub only (without sending):**
```bash
python kindle_sender.py "https://example.com/article" --no-send
```

**Specify custom output directory:**
```bash
python kindle_sender.py "https://example.com/article" --output-dir "/path/to/output"
```

**Debug article extraction:**
```bash
python kindle_sender.py "https://example.com/article" --debug-extraction
```

### Command Line Options

- `url` - URL of the article to process
- `--file` - Path to a local HTML file
- `--no-send` - Generate ePub file without sending to Kindle
- `--output-dir` - Custom directory for ePub output
- `--debug-extraction` - Extract and display article content without processing

## Directory Structure

The application creates and uses these directories:

```
Kindle Sender/
├── html_articles/          # Place HTML files here for processing
├── epub_output/            # Generated ePub files (when not sent)
├── .env                    # Your configuration file
├── .env.example           # Configuration template
└── *.py                   # Application files
```

## Troubleshooting

### Common Issues

**"Missing required email configuration"**
- Ensure your `.env` file exists and contains all required email settings
- Check that there are no extra spaces in your configuration values

**"Authentication failed" when sending email**
- For Gmail: Make sure you're using an App Password, not your regular password
- Verify 2-factor authentication is enabled on your Google account
- Check that your email credentials are correct

**"Could not extract article content"**
- Some websites may block automated access
- Try the optional `newspaper3k` dependency for better extraction
- Save the webpage as HTML and use the file processing option instead

**ePub files not appearing on Kindle**
- Verify your Kindle email address is correct
- Check that your sender email is in Amazon's approved sender list
- Look for the email in your regular inbox - it may have bounced back

**"Import Error" messages**
- Install missing dependencies with `pip install <package-name>`
- Ensure you're using Python 3.6 or higher

### Email Provider Settings

**Gmail:**
- SMTP Server: `smtp.gmail.com`
- Port: `587`
- Use App Password (not regular password)

**Outlook/Hotmail:**
- SMTP Server: `smtp-mail.outlook.com`
- Port: `587`

**Yahoo:**
- SMTP Server: `smtp.mail.yahoo.com`
- Port: `587` or `465`

## Tips

- HTML files placed in the `html_articles/` folder will be automatically detected
- Processed HTML files are renamed with `[SENT]` prefix to avoid duplicates
- Use the interactive mode's help (press 'h') to see keyboard shortcuts
- The application works best with article-style content rather than general web pages
- For problematic websites, try saving the page as HTML first

## File Processing Workflow

1. **URL Processing**: Article content is extracted directly from the web
2. **HTML File Processing**: Local files are parsed and content extracted
3. **ePub Generation**: Content is formatted into a proper ePub file
4. **Email Delivery**: ePub is sent to your Kindle email address
5. **Cleanup**: Temporary files are removed, source files are marked as sent

## Security Notes

- Your email credentials are stored locally in the `.env` file
- Never commit your `.env` file to version control
- Use App Passwords when available instead of main account passwords
- The application only sends emails to your configured Kindle address

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is provided as-is for personal use. Please respect the terms of service of websites you're extracting content from.
