import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import re

# Import domain handlers
from domain_handlers import domain_registry

# Try to import optional dependencies
try:
    from newspaper import Article
    newspaper_available = True
except ImportError:
    newspaper_available = False

def extract_author_from_soup(soup):
    """Extract author information from HTML soup by looking for author-related elements."""
    author = None
    
    # Define patterns for author-related class names and attributes
    author_patterns = [
        # Class-based selectors (most common)
        '[class*="author-name"]',
        '[class*="author"]',
        '[class*="autor"]',  # Spanish/Portuguese
        '[class*="byline"]',
        '[class*="writer"]',
        '[class*="journalist"]',
        '[class*="by-author"]',
        '[class*="post-author"]',
        '[class*="article-author"]',
        '[class*="entry-author"]',
        
        # Attribute-based selectors
        '[rel="author"]',
        '[itemprop="author"]',
        '[data-author]',
        
        # Microdata and structured data
        '[itemtype*="Person"]',
        
        # Common HTML patterns
        'address',  # Sometimes used for author info
        '.byline',
        '.author',
        '.writer'
    ]
    
    # Try each pattern
    for pattern in author_patterns:
        try:
            elements = soup.select(pattern)
            for element in elements:
                # Skip if element is empty or too long (likely not an author name)
                text = element.get_text(strip=True)
                if text and 2 <= len(text) <= 100:
                    # Clean up common prefixes
                    text = re.sub(r'^(by|por|autor|author|written by|escrito por)\s*:?\s*', '', text, flags=re.IGNORECASE)
                    # Remove common suffixes like social media handles or publication info
                    text = re.sub(r'\s*[@#]\w+.*$', '', text)
                    text = re.sub(r'\s*\|\s*.*$', '', text)  # Remove everything after |
                    text = text.strip()
                    
                    # Basic validation: should look like a name (letters, spaces, common punctuation)
                    if re.match(r'^[a-zA-ZÀ-ÿ\s\.\-\']+$', text) and len(text.split()) <= 6:
                        return text
        except Exception:
            # Skip this pattern if it causes issues
            continue
    
    # Try to find author in meta tags as fallback
    meta_patterns = [
        'meta[name="author"]',
        'meta[property="article:author"]',
        'meta[name="dc.creator"]',
        'meta[name="twitter:creator"]'
    ]
    
    for pattern in meta_patterns:
        try:
            meta_tag = soup.select_one(pattern)
            if meta_tag and meta_tag.get('content'):
                content = meta_tag.get('content').strip()
                # Clean up social media handles
                content = re.sub(r'^@', '', content)
                if content and 2 <= len(content) <= 100:
                    return content
        except Exception:
            continue
    
    return author

def extract_article(url):
    """Extract article content from URL."""
    print("Extracting article content...")

    # Try newspaper3k if available
    if newspaper_available:
        try:
            article = Article(url)
            article.download()
            article.parse()

            title = article.title
            content = article.text
            # Try to get author from newspaper3k
            author = None
            if hasattr(article, 'authors') and article.authors:
                # newspaper3k returns a list of authors, take the first one
                author = article.authors[0] if article.authors else None
            
            # If newspaper3k didn't find author, try our custom extraction
            if not author:
                # Parse HTML again for author extraction
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(response.text, 'html.parser')
                author = extract_author_from_soup(soup)

            if title and content:
                print(f"Successfully extracted: '{title}'")
                if author:
                    print(f"Author found: '{author}'")
                # Apply post-processing for the domain
                processed_title, processed_content = domain_registry.run_post_processing(url, title, content)
                return processed_title, processed_content, author
        except Exception as e:
            print(f"Newspaper extraction failed: {e}")

    # Fallback to BeautifulSoup
    print("Using fallback extraction method...")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Get title
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else urlparse(url).netloc
        
        # Extract author before removing elements (to avoid removing author info)
        author = extract_author_from_soup(soup)

        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            element.decompose()

        # Try to find the main content with different selectors
        main_content = None
        for selector in ['article', 'main', '.content', '.article-content', '.post-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
                
        if not main_content:
            # If no common content container found, use the body
            main_content = soup.body

        # Extract paragraphs within the main content
        content_elements = main_content.find_all(['p', 'h2', 'h3', 'h4'])
        content = "\n\n".join([el.get_text(strip=True) for el in content_elements if el.get_text(strip=True)])

        if not title or not content:
            raise ValueError("Could not extract article content")

        if author:
            print(f"Author found: '{author}'")

        # Apply post-processing for the domain
        processed_title, processed_content = domain_registry.run_post_processing(url, title, content)
        return processed_title, processed_content, author
    except Exception as e:
        raise ValueError(f"Failed to extract article content: {e}")

def extract_from_file(file_path):
    """Extract article content from a local HTML file."""
    print(f"Extracting article content from file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to extract title
        title = None
        if soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        elif soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        
        # If title not found, use filename
        if not title:
            title = os.path.basename(file_path).replace('.html', '')
        
        # Extract author before removing elements (to avoid removing author info)
        author = extract_author_from_soup(soup)

        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            element.decompose()
        
        # Try to find the main content
        # This is a simplified approach and may need adjustment for different HTML structures
        main_content = None
        
        for selector in ['article', 'main', '.content', '.article-content', '.post-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # If no common content container found, use the body
            main_content = soup.body
        
        # Extract paragraphs within the main content
        content_elements = main_content.find_all(['p', 'h2', 'h3', 'h4'])
        content = "\n\n".join([el.get_text(strip=True) for el in content_elements if el.get_text(strip=True)])
        
        if not content:
            # Fallback: just get the text from body
            content = soup.body.get_text(strip=True)
        
        if not content:
            raise ValueError("Could not extract article content from the file")
        
        if author:
            print(f"Author found: '{author}'")
        
        # Apply post-processing for the domain
        processed_title, processed_content = domain_registry.run_post_processing(file_path, title, content)
        return processed_title, processed_content, author
    
    except Exception as e:
        raise ValueError(f"Failed to extract article content from file: {e}")
