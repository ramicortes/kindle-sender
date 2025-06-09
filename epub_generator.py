import os
import re
import tempfile
from urllib.parse import urlparse
import sys
import unicodedata

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    print("Error: ebooklib package is required")
    print("Install it with: pip install EbookLib")
    sys.exit(1)

def sanitize_text_for_kindle(text):
    """
    Sanitize text by removing or replacing problematic characters for Kindle.
    This converts accented characters to their base equivalents and removes other special characters.
    """
    if not text:
        return text
    
    # Normalize unicode characters (NFD = decomposed form)
    normalized = unicodedata.normalize('NFD', text)
    
    # Remove combining characters (accents, etc.) and keep only ASCII
    ascii_text = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    
    # Additional cleanup: replace remaining problematic characters
    # Keep alphanumeric, spaces, hyphens, underscores, and basic punctuation
    sanitized = re.sub(r'[^\w\s\-.,!?():;]', '', ascii_text)
    
    # Clean up multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized

def create_epub(title, content, source_reference, output_dir=None, config=None, author=None):
    """Create an ePub file with article content."""
    print("Creating ePub file...")
    book = epub.EpubBook()
    
    # Sanitize title and author early to avoid issues
    title = sanitize_text_for_kindle(title)
    
    # Clean title for filename
    clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    clean_title = re.sub(r'[-\s]+', '-', clean_title)
    
    # Determine author information
    if author:
        # Use the extracted author
        author = sanitize_text_for_kindle(author)
    else:
        # Fallback to determining from source reference (old behavior)
        if source_reference.startswith("Local file:"):
            # For local files, use filename as author
            author = source_reference.replace("Local file: ", "")
        else:
            # For URLs, use domain as author
            domain = urlparse(source_reference).netloc
            author = domain if domain else "Unknown"
        author = sanitize_text_for_kindle(author)
    
    # Determine domain for display purposes
    if source_reference.startswith("Local file:"):
        domain = "Local HTML File"
    else:
        domain = urlparse(source_reference).netloc
    
    # Display and allow overriding of title and author
    print("\n=== Article Information ===")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print("=========================")
    
    override = input("Do you want to override the title or author? (y/n): ").lower().strip()
    if override == 'y':
        new_title = input(f"Enter new title (or press Enter to keep '{title}'): ").strip()
        if new_title:
            title = sanitize_text_for_kindle(new_title)  # Sanitize user input
            # Update clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            clean_title = re.sub(r'[-\s]+', '-', clean_title)
        
        new_author = input(f"Enter new author (or press Enter to keep '{author}'): ").strip()
        if new_author:
            author = sanitize_text_for_kindle(new_author)  # Sanitize user input
    
    # Show final sanitized values if they were changed during sanitization
    print(f"\nFinal sanitized title: {title}")
    print(f"Final sanitized author: {author}")
    
    # Set metadata
    book.set_identifier(f"article_{hash(title)}")
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    
    # Add content
    chapter = epub.EpubHtml(title='Article', file_name='article.xhtml')
    
    # Format content with basic HTML
    formatted_content = f"<h1>{title}</h1>\n"
    formatted_content += f"<p><i>Source: {domain}</i></p>\n"
    
    # Split content by newlines and format paragraphs/headings
    paragraphs = content.split('\n\n')
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
            
        # Check if it might be a heading
        if len(p) < 80 and not p.endswith('.') and not p.endswith('?') and not p.endswith('!'):
            formatted_content += f"<h2>{p}</h2>\n"
        else:
            formatted_content += f"<p>{p}</p>\n"
    
    chapter.content = formatted_content
    book.add_item(chapter)
    
    # Define book structure
    book.spine = ['nav', chapter]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Determine output directory
    # Priority: 1. Function parameter, 2. Config setting, 3. Temp directory
    if output_dir:
        target_dir = output_dir
    elif config and config['Directories']['epub_output_dir']:
        target_dir = config['Directories']['epub_output_dir']
    else:
        target_dir = tempfile.gettempdir()
    
    # Create directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Create output file path
    output_path = os.path.join(target_dir, f"{clean_title}.epub")
    
    # Write to file
    epub.write_epub(output_path, book)
    print(f"Created ePub file: {output_path}")
    return output_path
