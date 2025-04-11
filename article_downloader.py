import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Try to import optional dependencies
try:
    from newspaper import Article
    newspaper_available = True
except ImportError:
    newspaper_available = False

def extract_article(url):
    """Extract article content from URL."""
    print("Extracting article content...")

    # Ensure the URL is from cenital.com
    if "cenital.com" not in urlparse(url).netloc:
        raise ValueError("This downloader only supports articles from cenital.com")

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

        # Remove non-content elements specific to cenital.com
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            element.decompose()

        # Target the main content area (adjusted for cenital.com structure)
        main_content = soup.find('div', class_='article-content')  # Replace with actual class or ID
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
