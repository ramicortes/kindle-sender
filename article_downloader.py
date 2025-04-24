import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

# Try to import optional dependencies
try:
    from newspaper import Article
    newspaper_available = True
except ImportError:
    newspaper_available = False

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

            if title and content:
                print(f"Successfully extracted: '{title}'")
                return title, content
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

        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            element.decompose()

        # Target the main content area
        main_content = soup.find('div', class_='article-content')  # Replace with actual class or ID if needed
        if not main_content:
            raise ValueError("Could not locate main content on the page")

        # Extract paragraphs within the main content
        content_elements = main_content.find_all(['p', 'h2', 'h3'])
        content = "\n\n".join([el.get_text(strip=True) for el in content_elements if el.get_text(strip=True)])

        if not title or not content:
            raise ValueError("Could not extract article content")

        return title, content
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
        
        print(f"Successfully extracted: '{title}'")
        return title, content
    
    except Exception as e:
        raise ValueError(f"Failed to extract article content from file: {e}")
