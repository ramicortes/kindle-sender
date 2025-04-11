import os
import re
import tempfile
from urllib.parse import urlparse
import sys

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    print("Error: ebooklib package is required")
    print("Install it with: pip install EbookLib")
    sys.exit(1)

def create_epub(title, content, url, output_dir=None):
    """Create an ePub file with article content."""
    print("Creating ePub file...")
    book = epub.EpubBook()
    
    # Clean title for filename
    clean_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    clean_title = re.sub(r'[-\s]+', '-', clean_title)
    
    # Set metadata
    book.set_identifier(f"article_{hash(title)}")
    book.set_title(title)
    book.set_language('en')
    
    # Add author as the domain name
    domain = urlparse(url).netloc
    book.add_author(domain)
    
    # Add content
    chapter = epub.EpubHtml(title='Article', file_name='article.xhtml')
    
    # Format content with basic HTML
    formatted_content = f"<h1>{title}</h1>\n"
    formatted_content += f"<p><i>Source: <a href='{url}'>{domain}</a></i></p>\n"
    
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
    
    # Create output file
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f"{clean_title}.epub")
    else:
        output_path = os.path.join(tempfile.gettempdir(), f"{clean_title}.epub")
    
    # Write to file
    epub.write_epub(output_path, book)
    print(f"Created ePub file: {output_path}")
    return output_path
