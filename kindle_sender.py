#!/usr/bin/env python3
import argparse
import os
import sys
import datetime

# Import from our modules
from article_downloader import extract_article, extract_from_file
from epub_generator import create_epub
from email_sender import send_email
from config_manager import load_config

def rename_html_file(file_path):
    """Rename a file by prepending '[SENT] ' to its filename."""
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    # Skip if already marked as sent
    if filename.startswith('[SENT] '):
        return file_path
    
    new_filename = f"[SENT] {filename}"
    new_file_path = os.path.join(directory, new_filename)
    
    try:
        os.rename(file_path, new_file_path)
        print(f"File renamed to: {new_filename}")
        return new_file_path
    except Exception as e:
        print(f"Warning: Could not rename file: {e}")
        return file_path

def get_html_articles_dir(config):
    """Get the HTML articles directory from config or use default."""
    html_dir = config['Directories']['html_articles_dir']
    if not html_dir:
        # Use default directory if not specified
        html_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html_articles')
    
    # Create directory if it doesn't exist
    if not os.path.exists(html_dir):
        print(f"Creating HTML articles directory at {html_dir}")
        os.makedirs(html_dir)
        
    return html_dir

def interactive_mode(config):
    """Run the program in interactive mode with menu options."""
    print("\n===== Kindle Article Sender =====")
    print("\nUsage Instructions:")
    print("  Interactive Mode: ./kindle_sender.py")
    print("  Command Line Mode: ./kindle_sender.py [URL] [options]")
    print("  Help: ./kindle_sender.py --help")
    
    continue_session = True
    current_url = None
    current_file = None
    current_title = None
    current_content = None
    
    while continue_session:
        # Get article source if we don't have one
        if current_url is None and current_file is None:
            choosing_source = True
            
            while choosing_source:
                print("\nHow would you like to import an article?")
                print("1. From a URL")
                print("2. From a local HTML file")
                print("3. Exit")
                
                source_choice = input("\nEnter your choice (1-3): ").strip()
                
                if source_choice == '1':
                    # URL mode
                    current_url = input("\nEnter article URL: ").strip()
                    if not current_url:
                        print("No URL provided. Returning to source selection.")
                        continue
                    
                    # Extract article content
                    try:
                        current_title, current_content = extract_article(current_url)
                        print(f"\nSuccessfully extracted: '{current_title}'")
                        choosing_source = False
                    except Exception as e:
                        print(f"\nError: {e}")
                        current_url = None
                        continue
                        
                elif source_choice == '2':
                    # File mode
                    html_dir = get_html_articles_dir(config)
                    
                    # List HTML files
                    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
                    
                    if not html_files:
                        print(f"\nNo HTML files found in {html_dir}")
                        print("Please place HTML files in this directory and try again.")
                        continue
                    
                    selecting_file = True
                    while selecting_file:
                        print("\nAvailable HTML files:")
                        for i, file in enumerate(html_files, 1):
                            print(f"{i}. {file}")
                        print("0. Back to main menu")
                        
                        try:
                            file_choice = input("\nEnter file number (0 to go back): ").strip()
                            
                            if file_choice == '0':
                                # Go back to source selection
                                selecting_file = False
                                continue
                                
                            file_choice = int(file_choice)
                            if file_choice < 1 or file_choice > len(html_files):
                                print("Invalid selection. Please try again.")
                                continue
                            
                            current_file = os.path.join(html_dir, html_files[file_choice - 1])
                            
                            # Extract article content
                            try:
                                current_title, current_content = extract_from_file(current_file)
                                print(f"\nSuccessfully extracted: '{current_title}'")
                                selecting_file = False
                                choosing_source = False
                            except Exception as e:
                                print(f"\nError: {e}")
                                current_file = None
                                continue
                                
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                            continue
                        
                elif source_choice == '3':
                    print("Exiting.")
                    sys.exit(0)
                    
                else:
                    print("Invalid choice. Please try again.")
                    continue
        
        # Display menu options
        print("\nWhat would you like to do?")
        print("1. Print article content")
        print("2. Generate ePub file (without sending)")
        print("3. Send article to Kindle")
        print("4. Work on a new article")
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
            output_dir = input("Enter output directory (or press Enter for default/temp directory): ").strip()
            source_reference = current_url if current_url else f"Local file: {os.path.basename(current_file)}"
            output_path = create_epub(current_title, current_content, source_reference, output_dir if output_dir else None, config)
            print(f"\nePub file generated successfully at: {output_path}")
            
        elif choice == '3':
            # Generate and send to Kindle
            if not config['Email']['from_email'] or not config['Email']['password'] or not config['Email']['kindle_email']:
                print("Email configuration incomplete. Please check your .env file.")
                continue
                
            source_reference = current_url if current_url else f"Local file: {os.path.basename(current_file)}"
            output_path = create_epub(current_title, current_content, source_reference, None, config)
            
            print(f"Sending to Kindle email: {config['Email']['kindle_email']}")
            email_subject = f"Convert: {current_title}"  # "Convert:" prefix tells Amazon to convert the document
            email_body = f"Article: {current_title}\nSource: {source_reference}\nSent on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            success = send_email(config, email_subject, email_body, output_path)
            
            if success:
                print("\nArticle sent successfully to your Kindle!")
                # Clean up only if successfully sent
                os.remove(output_path)
                
                # If the source was a file, rename it to avoid sending duplicates
                if current_file:
                    current_file = rename_html_file(current_file)
            else:
                print("\nFailed to send article. Please check your email settings.")
                print(f"The ePub file is still available at: {output_path}")
        
        elif choice == '4':
            # Reset to work on a new article
            current_url = None
            current_file = None
            current_title = None
            current_content = None
            continue
            
        elif choice == '5':
            print("Exiting.")
            continue_session = False
            
        else:
            print("Invalid choice. Please try again.")
            
        # After each operation (except for choosing a new URL/file or exit), ask if user wants to continue
        if choice not in ['4', '5']:
            print("\n")
            continue_prompt = input("Press Enter to continue or type 'exit' to quit: ").strip().lower()
            if continue_prompt == 'exit':
                continue_session = False

def main():
    parser = argparse.ArgumentParser(description='Send articles to Kindle')
    
    # Create a mutually exclusive group for URL or file
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument('url', nargs='?', help='URL of the article to send')
    source_group.add_argument('--file', help='Path to a local HTML file to send')
    
    parser.add_argument('--no-send', action='store_true', help='Only generate ePub file without sending email')
    parser.add_argument('--output-dir', help='Directory to save the ePub file (default: configured directory or temp)')
    parser.add_argument('--debug-extraction', action='store_true', help='Only extract and print the article content for debugging')

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Check if we should run in interactive mode (no arguments provided)
    if not args.url and not args.file:
        interactive_mode(config)
        return

    try:
        # Extract article content
        if args.url:
            title, content = extract_article(args.url)
            source_reference = args.url
            source_file = None
        elif args.file:
            title, content = extract_from_file(args.file)
            source_reference = f"Local file: {os.path.basename(args.file)}"
            source_file = args.file
        else:
            parser.print_help()
            sys.exit(1)

        if args.debug_extraction:
            print("\n=== Extracted Article ===")
            print(f"Title: {title}\n")
            print(content)
            print("\n=== End of Article ===")
            sys.exit(0)

        # Create ePub file
        output_path = create_epub(title, content, source_reference, args.output_dir, config)

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
            email_body = f"Article: {title}\nSource: {source_reference}\nSent on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            success = send_email(config, email_subject, email_body, output_path)

            if success:
                print("\nArticle sent successfully to your Kindle!")
                # Clean up only if successfully sent
                os.remove(output_path)
                
                # If the source was a file, rename it to avoid sending duplicates
                if source_file:
                    rename_html_file(source_file)
            else:
                print("\nFailed to send article. Please check your email settings.")
                print(f"The ePub file is still available at: {output_path}")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
