#!/usr/bin/env python3
import argparse
import os
import sys

# Import from our modules
from config_manager import load_config
from article_manager import ArticleManager
from publication_manager import PublicationManager
from utils import format_source_reference

class InteractiveMode:
    """Class to handle interactive mode operations."""
    
    def __init__(self, config):
        self.config = config
        self.article_manager = ArticleManager(config)
        self.publication_manager = PublicationManager(config)
        self.current_url = None
        self.current_file = None
        self.current_title = None
        self.current_content = None
    
    def reset_article(self):
        """Reset the current article data."""
        self.current_url = None
        self.current_file = None
        self.current_title = None
        self.current_content = None
    
    def get_source_reference(self):
        """Get the source reference for the current article."""
        return format_source_reference(self.current_url, self.current_file)
    
    def run(self):
        """Run the interactive mode interface."""
        self._print_welcome_message()
        
        continue_session = True
        while continue_session:
            # Get article source if we don't have one
            if self.current_title is None:
                self._choose_article_source()
            
            # Display menu options and process choice
            continue_session = self._process_main_menu()
    
    def _print_welcome_message(self):
        """Print the welcome message and usage instructions."""
        print("\n===== Kindle Article Sender =====")
        print("\nUsage Instructions:")
        print("  Interactive Mode: ./kindle_sender.py")
        print("  Command Line Mode: ./kindle_sender.py [URL] [options]")
        print("  Help: ./kindle_sender.py --help")
    
    def _choose_article_source(self):
        """Present options to choose an article source."""
        choosing_source = True
        
        while choosing_source:
            print("\nHow would you like to import an article?")
            
            # Display all available sources
            sources = self.article_manager.get_available_sources()
            for i, (source_id, source_name) in enumerate(sources, 1):
                print(f"{i}. From a {source_name}")
            print(f"{len(sources) + 1}. Exit")
            
            source_choice = input(f"\nEnter your choice (1-{len(sources) + 1}): ").strip()
            
            # Check for exit option
            if source_choice == str(len(sources) + 1):
                print("Exiting.")
                sys.exit(0)
            
            # Validate and process choice
            try:
                choice_idx = int(source_choice) - 1
                if choice_idx < 0 or choice_idx >= len(sources):
                    print("Invalid choice. Please try again.")
                    continue
                
                # Get source ID for the selected choice
                selected_source_id = sources[choice_idx][0]
                
                # Handle source-specific import
                if selected_source_id == "url":
                    choosing_source = self._handle_url_source()
                elif selected_source_id == "html_file":
                    choosing_source = self._handle_file_source()
                else:
                    print(f"Support for {sources[choice_idx][1]} is not yet implemented.")
                    continue
                    
            except ValueError:
                print("Invalid choice. Please enter a number.")
    
    def _handle_url_source(self):
        """Handle URL source selection."""
        # URL mode
        self.current_url = input("\nEnter article URL: ").strip()
        if not self.current_url:
            print("No URL provided. Returning to source selection.")
            return True
        
        # Extract article content
        try:
            self.current_title, self.current_content = self.article_manager.extract_from_url(self.current_url)
            print(f"\nSuccessfully extracted: '{self.current_title}'")
            return False  # Exit the choosing source loop
        except Exception as e:
            print(f"\nError: {e}")
            self.current_url = None
            return True  # Stay in the choosing source loop
    
    def _handle_file_source(self):
        """Handle file source selection."""
        # Get HTML file source for specific methods
        html_source = self.article_manager.get_html_source()
        
        # Get available HTML files
        html_files = html_source.get_available_files()
        
        if not html_source.display_available_files(html_files):
            return True  # Stay in the choosing source loop if no files available
        
        selecting_file = True
        while selecting_file:
            try:
                file_choice = input("\nEnter file number (0 to go back): ").strip()
                
                if file_choice == '0':
                    # Go back to source selection
                    return True
                    
                file_choice = int(file_choice)
                if file_choice < 1 or file_choice > len(html_files):
                    print("Invalid selection. Please try again.")
                    continue
                
                file_index = file_choice - 1
                self.current_file = html_source.get_file_path(file_index, html_files)
                
                # Extract article content
                try:
                    self.current_title, self.current_content = self.article_manager.extract_from_file_path(self.current_file)
                    return False  # Exit the choosing source loop
                except Exception as e:
                    print(f"\nError: {e}")
                    self.current_file = None
                    return True  # Stay in the choosing source loop
                    
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def _process_main_menu(self):
        """Display main menu and process user choice."""
        print("\nWhat would you like to do?")
        
        # Display all available output options
        outputs = self.publication_manager.get_available_outputs()
        for i, (output_id, output_name) in enumerate(outputs, 1):
            print(f"{i}. {output_name}")
            
        # Additional options
        print(f"{len(outputs) + 1}. Work on a new article")
        print(f"{len(outputs) + 2}. Exit")
        
        choice = input(f"\nEnter your choice (1-{len(outputs) + 2}): ").strip()
        
        # Check for work on new article option
        if choice == str(len(outputs) + 1):
            # Reset to work on a new article
            self.reset_article()
            return True
        
        # Check for exit option
        elif choice == str(len(outputs) + 2):
            print("Exiting.")
            return False
        
        # Process output choice
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(outputs):
                print("Invalid choice. Please try again.")
                return True
            
            # Get output ID for the selected choice
            selected_output_id = outputs[choice_idx][0]
            
            # Handle the selected output
            source_reference = self.get_source_reference()
            
            if selected_output_id == "print":
                self.publication_manager.print_article(
                    self.current_title,
                    self.current_content,
                    source_reference
                )
            elif selected_output_id == "epub":
                # Ask for output directory
                output_dir = input("Enter output directory (or press Enter for default/temp directory): ").strip()
                self.publication_manager.create_epub(
                    self.current_title,
                    self.current_content,
                    source_reference,
                    output_dir if output_dir else None
                )
            elif selected_output_id == "kindle":
                self.publication_manager.send_to_kindle(
                    self.current_title,
                    self.current_content,
                    source_reference,
                    self.current_file
                )
            else:
                # Generic handling for new output types
                self.publication_manager.process_with_output(
                    selected_output_id,
                    self.current_title,
                    self.current_content,
                    source_reference,
                    self.current_file
                )
                
        except ValueError:
            print("Invalid choice. Please enter a number.")
            return True
        
        # After each operation (except for choosing a new article or exit), ask if user wants to continue
        print("\n")
        continue_prompt = input("Press Enter to continue or type 'exit' to quit: ").strip().lower()
        if continue_prompt == 'exit':
            return False
        
        return True


class CommandLineMode:
    """Class to handle command line mode operations."""
    
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.article_manager = ArticleManager(config)
        self.publication_manager = PublicationManager(config)
    
    def run(self):
        """Run the command line mode operations."""
        try:
            # Extract article content
            title, content, source_reference, source_file = self._extract_article()
            
            # Handle debug extraction if requested
            if self.args.debug_extraction:
                self.publication_manager.print_article(title, content, source_reference)
                sys.exit(0)
            
            # Handle sending or generating ePub
            if self.args.no_send:
                self.publication_manager.create_epub(
                    title, 
                    content, 
                    source_reference, 
                    self.args.output_dir
                )
                print("File was not sent to Kindle as --no-send flag was used.")
            else:
                # Send to Kindle
                self.publication_manager.send_to_kindle(
                    title,
                    content,
                    source_reference,
                    source_file
                )
                
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    
    def _extract_article(self):
        """Extract article content based on command line arguments."""
        if self.args.url:
            title, content = self.article_manager.extract_from_url(self.args.url)
            source_reference = self.args.url
            source_file = None
        elif self.args.file:
            title, content = self.article_manager.extract_from_file_path(self.args.file)
            source_reference = format_source_reference(file_path=self.args.file)
            source_file = self.args.file
        else:
            raise ValueError("No URL or file specified")
            
        return title, content, source_reference, source_file


def main():
    """Main entry point of the program."""
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
        interactive = InteractiveMode(config)
        interactive.run()
    else:
        # Run in command line mode
        command_line = CommandLineMode(args, config)
        command_line.run()

if __name__ == "__main__":
    main()
