#!/usr/bin/env python3
import os
from abc import ABC, abstractmethod
from epub_generator import create_epub
from email_sender import send_email
from utils import create_email_content, check_email_config, handle_successful_send, handle_failed_send, get_directory_path, rename_html_file

class ArticleOutput(ABC):
    """Abstract base class for all article output destinations."""
    
    @property
    @abstractmethod
    def output_name(self):
        """Name of the output type for display."""
        pass
    
    @abstractmethod
    def process(self, title, content, source_reference, source_file=None, author=None, **kwargs):
        """Process the article and send it to the output destination.
        
        Args:
            title: The article title
            content: The article content
            source_reference: Reference to the source (URL or file path)
            source_file: Original source file path if from a file
            author: The article author (if extracted)
            **kwargs: Additional parameters specific to the output type
            
        Returns:
            tuple: A tuple containing (success, result_data)
        """
        pass


class PrintOutput(ArticleOutput):
    """Output that prints article content to the console."""
    
    @property
    def output_name(self):
        return "Print to Console"
    
    def process(self, title, content, source_reference, source_file=None, author=None, **kwargs):
        """Print article content to the console."""
        print("\n=== Extracted Article ===")
        print(f"Title: {title}")
        if author:
            print(f"Author: {author}")
        print(f"Source: {source_reference}")
        print("\n" + content)
        print("\n=== End of Article ===")
        return True, None


class EPubOutput(ArticleOutput):
    """Output that generates an ePub file."""
    
    def __init__(self, config):
        self.config = config
        self.epub_output_dir = self._get_epub_output_dir()
    
    @property
    def output_name(self):
        return "Generate ePub"
    
    def _get_epub_output_dir(self):
        """Get the ePub output directory from config or use default."""
        return get_directory_path(
            self.config['Directories']['epub_output_dir'],
            'EPUB_OUTPUT_DIR',
            'epub_output'
        )
    
    def process(self, title, content, source_reference, source_file=None, author=None, **kwargs):
        """Generate an ePub file from the article content."""
        output_dir = kwargs.get('output_dir', self.epub_output_dir)
        output_path = create_epub(title, content, source_reference, output_dir, self.config, author)
        print(f"\nePub file generated successfully at: {output_path}")
        return True, output_path


class KindleOutput(ArticleOutput):
    """Output that sends the article to a Kindle device."""
    
    def __init__(self, config):
        self.config = config
        self.epub_generator = EPubOutput(config)
    
    @property
    def output_name(self):
        return "Send to Kindle"
    
    def process(self, title, content, source_reference, source_file=None, author=None, **kwargs):
        """Create ePub and send to Kindle."""
        # Check email configuration
        if not check_email_config(self.config):
            print("Email configuration incomplete. Please check your .env file.")
            return False, None
            
        # Create ePub
        success, output_path = self.epub_generator.process(title, content, source_reference, author=author)
        if not success:
            return False, None
        
        # Prepare email content
        email_subject, email_body = create_email_content(title, source_reference)
        print(f"Sending to Kindle email: {self.config['Email']['kindle_email']}")
        
        # Send email
        success = send_email(self.config, email_subject, email_body, output_path)
        
        # Handle result
        if success:
            new_file_path = handle_successful_send(output_path, source_file)
            return True, new_file_path
        else:
            handle_failed_send(output_path)
            return False, output_path


class OutputFactory:
    """Factory class to create and manage available output destinations."""
    
    def __init__(self, config):
        self.config = config
        self.outputs = self._initialize_outputs()
    
    def _initialize_outputs(self):
        """Initialize all available output destinations."""
        return {
            "print": PrintOutput(),
            "epub": EPubOutput(self.config),
            "kindle": KindleOutput(self.config)
        }
    
    def get_output(self, output_type):
        """Get an output destination by type."""
        if output_type not in self.outputs:
            raise ValueError(f"Unknown output type: {output_type}")
        
        return self.outputs[output_type]
    
    def get_available_outputs(self):
        """Get all available output types with their display names."""
        return [(output_id, output.output_name) for output_id, output in self.outputs.items()]


class PublicationManager:
    """Class to handle publication operations using various output destinations."""
    
    def __init__(self, config):
        self.config = config
        self.output_factory = OutputFactory(config)
    
    def get_available_outputs(self):
        """Get list of available output types."""
        return self.output_factory.get_available_outputs()
    
    def create_epub(self, title, content, source_reference, custom_output_dir=None, author=None):
        """Create an ePub file from the article content."""
        epub_output = self.output_factory.get_output("epub")
        _, output_path = epub_output.process(
            title, 
            content, 
            source_reference, 
            author=author,
            output_dir=custom_output_dir
        )
        return output_path
    
    def send_to_kindle(self, title, content, source_reference, source_file=None, author=None):
        """Create ePub and send to Kindle."""
        kindle_output = self.output_factory.get_output("kindle")
        return kindle_output.process(
            title,
            content,
            source_reference,
            source_file,
            author=author
        )
    
    def print_article(self, title, content, source_reference, author=None):
        """Print article content to console."""
        print_output = self.output_factory.get_output("print")
        return print_output.process(
            title,
            content,
            source_reference,
            author=author
        )
    
    def process_with_output(self, output_type, title, content, source_reference, source_file=None, author=None, **kwargs):
        """Process article with the specified output type."""
        output = self.output_factory.get_output(output_type)
        return output.process(
            title,
            content,
            source_reference,
            source_file,
            author=author,
            **kwargs
        )