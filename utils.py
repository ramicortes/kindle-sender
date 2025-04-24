#!/usr/bin/env python3
import os
import sys
import datetime

def format_source_reference(url=None, file_path=None):
    """Create a standardized source reference string from a URL or file path."""
    if url:
        return url
    elif file_path:
        return f"Local file: {os.path.basename(file_path)}"
    return "Unknown source"

def print_article_content(title, content):
    """Print article content in a formatted way."""
    print("\n=== Extracted Article ===")
    print(f"Title: {title}\n")
    print(content)
    print("\n=== End of Article ===")

def create_email_content(title, source_reference):
    """Create standardized email subject and body content."""
    email_subject = f"Convert: {title}"  # "Convert:" prefix tells Amazon to convert the document
    email_body = f"Article: {title}\nSource: {source_reference}\n"
    email_body += f"Sent on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return email_subject, email_body

def get_directory_path(config_path, env_var_name, default_dir_name):
    """Get a directory path from config, create if it doesn't exist."""
    dir_path = config_path
    if not dir_path:
        # Use default directory if not specified
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), default_dir_name)
    
    # Create directory if it doesn't exist
    if not os.path.exists(dir_path):
        print(f"Creating directory at {dir_path}")
        os.makedirs(dir_path)
        
    return dir_path

def rename_html_file(file_path):
    """Rename a file by prepending '[SENT] ' to its filename."""
    if not file_path:
        return None
        
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

def check_email_config(config):
    """Check if email configuration is complete."""
    if not config['Email']['from_email'] or not config['Email']['password'] or not config['Email']['kindle_email']:
        return False
    return True

def handle_successful_send(output_path, source_file=None):
    """Handle operations after successful send."""
    print("\nArticle sent successfully to your Kindle!")
    
    # Clean up the epub file
    if output_path and os.path.exists(output_path):
        os.remove(output_path)
    
    # If the source was a file, rename it to avoid sending duplicates
    if source_file:
        return rename_html_file(source_file)
    return None

def handle_failed_send(output_path):
    """Handle operations after failed send."""
    print("\nFailed to send article. Please check your email settings.")
    if output_path:
        print(f"The ePub file is still available at: {output_path}")