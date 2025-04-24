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

def interactive_mode(config):
    """Run the program in interactive mode with menu options."""
    print("\n===== Kindle Article Sender =====")
    print("\nUsage Instructions:")
    print("  Interactive Mode: ./kindle_sender.py")
    print("  Command Line Mode: ./kindle_sender.py [URL] [options]")
    print("  Help: ./kindle_sender.py --help")
    
    continue_session = True
    current_url = None
    current_title = None
    current_content = None
    
    while continue_session:
        # Get article URL if we don't have one
        if current_url is None:
            current_url = input("\nEnter article URL: ").strip()
            if not current_url:
                print("No URL provided. Exiting.")
                sys.exit(0)
            
            # Extract article content
            try:
                current_title, current_content = extract_article(current_url)
                print(f"\nSuccessfully extracted: '{current_title}'")
            except Exception as e:
                print(f"\nError: {e}")
                current_url = None
                continue
        
        # Display menu options
        print("\nWhat would you like to do?")
        print("1. Extract and print article content")
        print("2. Generate ePub file (without sending)")
        print("3. Send article to Kindle")
        print("4. Work on a new URL")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Print article content
            print("\n=== Extracted Article ===")
            print(f"Title: {current_title}\n")
            print(current_content)
            print("\n=== End of Article ===")
            
        elif choice == '2':
            # Generate ePub without sending
            output_dir = input("Enter output directory (or press Enter for temp directory): ").strip()
            output_path = create_epub(current_title, current_content, current_url, output_dir if output_dir else None)
            print(f"\nePub file generated successfully at: {output_path}")
            
        elif choice == '3':
            # Generate and send to Kindle
            if not config['Email']['from_email'] or not config['Email']['password'] or not config['Email']['kindle_email']:
                print("Email configuration incomplete. Please check your .env file.")
                continue
                
            output_path = create_epub(current_title, current_content, current_url)
            
            print(f"Sending to Kindle email: {config['Email']['kindle_email']}")
            email_subject = f"Convert: {current_title}"  # "Convert:" prefix tells Amazon to convert the document
            email_body = f"Article: {current_title}\nURL: {current_url}\nSent on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            success = send_email(config, email_subject, email_body, output_path)
            
            if success:
                print("\nArticle sent successfully to your Kindle!")
                # Clean up only if successfully sent
                os.remove(output_path)
            else:
                print("\nFailed to send article. Please check your email settings.")
                print(f"The ePub file is still available at: {output_path}")
        
        elif choice == '4':
            # Reset to work on a new URL
            current_url = None
            current_title = None
            current_content = None
            continue
            
        elif choice == '5':
            print("Exiting.")
            continue_session = False
            
        else:
            print("Invalid choice. Please try again.")
            
        # After each operation (except for choosing a new URL or exit), ask if user wants to continue
        if choice not in ['4', '5']:
            print("\n")
            continue_prompt = input("Press Enter to continue or type 'exit' to quit: ").strip().lower()
            if continue_prompt == 'exit':
                continue_session = False

def main():
    parser = argparse.ArgumentParser(description='Send articles to Kindle')
    parser.add_argument('url', nargs='?', help='URL of the article to send')
    parser.add_argument('--no-send', action='store_true', help='Only generate ePub file without sending email')
    parser.add_argument('--output-dir', help='Directory to save the ePub file (default: temp directory)')
    parser.add_argument('--debug-extraction', action='store_true', help='Only extract and print the article content for debugging')

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Check if we should run in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        interactive_mode(config)
        return

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
