#!/usr/bin/env python3
import os
from abc import ABC, abstractmethod
from article_downloader import extract_article, extract_from_file
from utils import get_directory_path

class ArticleSource(ABC):
    """Abstract base class for all article sources."""
    
    @property
    @abstractmethod
    def source_name(self):
        """Name of the source type for display."""
        pass
    
    @abstractmethod
    def extract(self, *args, **kwargs):
        """Extract article content from this source.
        
        Returns:
            tuple: A tuple containing (title, content)
        """
        pass


class URLSource(ArticleSource):
    """Article source that extracts from a URL."""
    
    @property
    def source_name(self):
        return "URL"
    
    def extract(self, url):
        """Extract article from URL."""
        if not url:
            raise ValueError("No URL provided.")
        
        print("Extracting article content from URL...")
        return extract_article(url), url


class HTMLFileSource(ArticleSource):
    """Article source that extracts from a local HTML file."""
    
    def __init__(self, config):
        self.config = config
        self.html_dir = self._get_html_articles_dir()
    
    @property
    def source_name(self):
        return "HTML File"
    
    def _get_html_articles_dir(self):
        """Get the HTML articles directory from config or use default."""
        return get_directory_path(
            self.config['Directories']['html_articles_dir'],
            'HTML_ARTICLES_DIR', 
            'html_articles'
        )
    
    def extract(self, file_path):
        """Extract article from file path."""
        if not file_path:
            raise ValueError("No file path provided.")
        
        # Removed duplicate print message
        return extract_from_file(file_path), file_path
    
    def get_available_files(self):
        """Get list of available HTML files."""
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
        
        html_files = [f for f in os.listdir(self.html_dir) if f.endswith('.html')]
        return html_files
    
    def get_file_path(self, file_index, html_files):
        """Get file path from index."""
        if file_index < 0 or file_index >= len(html_files):
            raise ValueError("Invalid file index.")
        
        return os.path.join(self.html_dir, html_files[file_index])
    
    def display_available_files(self, html_files):
        """Display available HTML files."""
        if not html_files:
            print(f"\nNo HTML files found in {self.html_dir}")
            print("Please place HTML files in this directory and try again.")
            return False
        
        print("\nAvailable HTML files:")
        for i, file in enumerate(html_files, 1):
            print(f"{i}. {file}")
        print("0. Back to main menu")
        
        return True


class ArticleSourceFactory:
    """Factory class to create and manage available article sources."""
    
    def __init__(self, config):
        self.config = config
        self.sources = self._initialize_sources()
    
    def _initialize_sources(self):
        """Initialize all available article sources."""
        return {
            "url": URLSource(),
            "html_file": HTMLFileSource(self.config)
        }
    
    def get_source(self, source_type):
        """Get an article source by type."""
        if source_type not in self.sources:
            raise ValueError(f"Unknown source type: {source_type}")
        
        return self.sources[source_type]
    
    def get_available_sources(self):
        """Get all available source types with their display names."""
        return [(source_id, source.source_name) for source_id, source in self.sources.items()]


class ArticleManager:
    """Class to manage article operations using various sources."""
    
    def __init__(self, config):
        self.config = config
        self.source_factory = ArticleSourceFactory(config)
    
    def get_available_sources(self):
        """Get list of available source types."""
        return self.source_factory.get_available_sources()
    
    def extract_from_url(self, url):
        """Extract article from URL."""
        url_source = self.source_factory.get_source("url")
        (title, content), _ = url_source.extract(url)
        return title, content
    
    def extract_from_file_path(self, file_path):
        """Extract article from file path."""
        file_source = self.source_factory.get_source("html_file")
        (title, content), _ = file_source.extract(file_path)
        print(f"Successfully extracted: '{title}'")
        return title, content
    
    def get_html_source(self):
        """Get HTML file source for accessing its methods."""
        return self.source_factory.get_source("html_file")