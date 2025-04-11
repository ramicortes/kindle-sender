#!/usr/bin/env python3
import argparse
import os
import sys
import datetime

# Import from our modules
from article_downloader import extract_article
from epub_generator import create_epub
from email_sender import send_email
from config_manager import load_config

def main():
    parser = argparse.ArgumentParser(description='Send articles to Kindle')
    parser.add_argument('url', nargs='?', help='URL of the article to send')
    parser.add_argument('--no-send', action='store_true', help='Only generate ePub file without sending email')
    parser.add_argument('--output-dir', help='Directory to save the ePub file (default: temp directory)')
    parser.add_argument('--debug-extraction', action='store_true', help='Only extract and print the article content for debugging')

    args = parser.parse_args()

    # Load config
    config = load_config()

    if not args.url:
        parser.print_help()
        sys.exit(1)

    try:
        # Extract article content
        title, content = extract_article(args.url)

        if args.debug_extraction:
            print("\n=== Extracted Article ===")
            print(f"Title: {title}\n")
            print(content)
            print("\n=== End of Article ===")
            sys.exit(0)

        # Create ePub file
        output_path = create_epub(title, content, args.url, args.output_dir)

        if args.no_send:
            print(f"\nePub file generated successfully at: {output_path}")
            print("File was not sent to Kindle as --no-send flag was used.")
        else:
            # Check if configuration is complete for sending email
            if not config['Email']['from_email'] or not config['Email']['password'] or not config['Email']['kindle_email']:
                print("Email configuration incomplete. Please check your .env file.")
                print(f"ePub file generated successfully at: {output_path}")
                sys.exit(1)

            # Send email
            print(f"Sending to Kindle email: {config['Email']['kindle_email']}")
            email_subject = f"Convert: {title}"  # "Convert:" prefix tells Amazon to convert the document
            email_body = f"Article: {title}\nURL: {args.url}\nSent on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            success = send_email(config, email_subject, email_body, output_path)

            if success:
                print("\nArticle sent successfully to your Kindle!")
                # Clean up only if successfully sent
                os.remove(output_path)
            else:
                print("\nFailed to send article. Please check your email settings.")
                print(f"The ePub file is still available at: {output_path}")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
