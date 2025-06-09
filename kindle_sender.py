#!/usr/bin/env python3
import argparse
import os
import sys
import time
from blessed import Terminal

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
        self.current_author = None
        self.term = Terminal()  # Initialize blessed terminal
    
    def reset_article(self):
        """Reset the current article data."""
        self.current_url = None
        self.current_file = None
        self.current_title = None
        self.current_content = None
        self.current_author = None
    
    def get_source_reference(self):
        """Get the source reference for the current article."""
        return format_source_reference(self.current_url, self.current_file)
    
    def _display_menu(self, title, options, selected_idx=0):
        """Display a menu with arrow key navigation.
        
        Args:
            title: The title to display above the menu.
            options: List of options to display.
            selected_idx: The initially selected index.
            
        Returns:
            The selected index.
        """
        # Clear screen for better UI
        print(self.term.clear)
        
        with self.term.cbreak(), self.term.hidden_cursor():
            # Initial render
            selected = selected_idx
            
            while True:
                # Clear screen and display title
                print(self.term.home + self.term.clear)
                print(f"\n{title}\n")
                
                # Display options with selected option highlighted
                for i, option in enumerate(options):
                    if i == selected:
                        print(f" {self.term.black_on_white}→ {option}{self.term.normal}")
                    else:
                        print(f"  {option}")
                
                # Display navigation instructions
                print(f"\n{self.term.dim}Use ↑/↓ arrows to navigate, Enter to select{self.term.normal}")
                
                # Wait for key press
                key = self.term.inkey()
                
                # Handle navigation
                if key.code == self.term.KEY_UP:
                    selected = max(0, selected - 1)
                elif key.code == self.term.KEY_DOWN:
                    selected = min(len(options) - 1, selected + 1)
                elif key.code == self.term.KEY_ENTER:
                    return selected
                elif key.code == self.term.KEY_ESCAPE or key == 'q':
                    # Allow escape or 'q' to exit
                    if "Exit" in options:
                        return options.index("Exit")
                    return len(options) - 1  # Assume last option is exit or cancel
                elif key == 'h':
                    self._show_help_overlay()
    
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
        # Clear screen for a clean start
        print(self.term.clear)
        
        # Create a colorful title with box styling
        title = "Kindle Article Sender"
        box_width = len(title) + 8
        
        print(f"\n{self.term.bright_blue}{'═' * box_width}")
        print(f"╔{'═' * (box_width - 2)}╗")
        print(f"║{' ' * ((box_width - 2 - len(title)) // 2)}{self.term.bold_white}{title}{self.term.bright_blue}{' ' * ((box_width - 2 - len(title) + 1) // 2)}║")
        print(f"╚{'═' * (box_width - 2)}╝{self.term.normal}")
        
        # More informative welcome message
        print(f"\n{self.term.bright_green}Welcome!{self.term.normal}")
        print("This tool helps you send web articles and HTML files to your Kindle device")
        print("for a better reading experience without distractions.")
        
        # Feature highlights
        print(f"\n{self.term.bright_yellow}Features:{self.term.normal}")
        print(f"  {self.term.yellow}•{self.term.normal} Extract content from web URLs")
        print(f"  {self.term.yellow}•{self.term.normal} Process local HTML files")
        print(f"  {self.term.yellow}•{self.term.normal} Generate ePub files")
        print(f"  {self.term.yellow}•{self.term.normal} Send articles directly to your Kindle")
        
        # Navigation tip
        print(f"\n{self.term.bright_cyan}Navigation:{self.term.normal}")
        print(f"  {self.term.cyan}•{self.term.normal} Use {self.term.bold}↑/↓{self.term.normal} arrow keys to move between options")
        print(f"  {self.term.cyan}•{self.term.normal} Press {self.term.bold}Enter{self.term.normal} to select an option")
        print(f"  {self.term.cyan}•{self.term.normal} Press {self.term.bold}h{self.term.normal} at any time for help")
        
        # Add a short wait for user to see the welcome message
        print(f"\n{self.term.italic}Press any key to continue...{self.term.normal}")
        with self.term.cbreak():
            self.term.inkey()
    
    def _choose_article_source(self):
        """Present options to choose an article source."""
        choosing_source = True
        
        while choosing_source:
            print("\nHow would you like to import an article?")
            
            # Display all available sources
            sources = self.article_manager.get_available_sources()
            options = [f"From a {source_name}" for _, source_name in sources] + ["Exit"]
            choice_idx = self._display_menu("Choose Article Source", options)
            
            # Check for exit option
            if choice_idx == len(sources):
                print("Exiting.")
                sys.exit(0)
            
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
    
    def _handle_url_source(self):
        """Handle URL source selection."""
        # Clear screen for better UI
        print(self.term.clear)
        print(f"\n{self.term.bright_cyan}Enter Article URL{self.term.normal}")
        print(f"\n{self.term.dim}(Press Enter with empty input to go back){self.term.normal}\n")
        
        # Create an input area with border
        print(f"{self.term.bright_blue}┌{'─' * 50}┐{self.term.normal}")
        print(f"{self.term.bright_blue}│{self.term.normal} ", end="")
        
        # Get input with cursor positioned correctly
        with self.term.location(x=2, y=self.term.height // 2):
            self.current_url = input("").strip()
        
        print(f"{self.term.bright_blue}└{'─' * 50}┘{self.term.normal}")
        
        # Check for empty input to go back
        if not self.current_url:
            print(f"{self.term.yellow}No URL provided. Returning to source selection.{self.term.normal}")
            with self.term.cbreak():
                self.term.inkey(timeout=2)  # 2-second delay to read message
            return True
        
        # Import domain registry here to minimize circular imports
        from domain_handlers import domain_registry
        
        # Check for domain-specific pre-validation
        is_valid, message = domain_registry.run_pre_validation(self.current_url)
        if not is_valid and message:
            # Display domain-specific warning message
            print(f"\n{self.term.bright_red}⚠ Domain Warning:{self.term.normal}")
            print(f"{self.term.bright_yellow}┌{'─' * 50}┐{self.term.normal}")
            
            # Format message with word wrapping
            words = message.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= 48:  # Keep space for borders
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
                
            # Print wrapped message
            for line in lines:
                print(f"{self.term.bright_yellow}│{self.term.normal} {line.ljust(48)} {self.term.bright_yellow}│{self.term.normal}")
            
            print(f"{self.term.bright_yellow}└{'─' * 50}┘{self.term.normal}")
            
            # Wait for user acknowledgment
            print(f"\n{self.term.dim}Press any key to return to source selection...{self.term.normal}")
            with self.term.cbreak():
                self.term.inkey()
            return True
        
        # Show loading indicator
        print(f"\n{self.term.bright_yellow}Extracting article...{self.term.normal}")
        
        # Extract article content
        try:
            self.current_title, self.current_content, self.current_author = self.article_manager.extract_from_url(self.current_url)
            
            # Show success message with article title
            print(f"\n{self.term.bright_green}✓ Successfully extracted:{self.term.normal} {self.term.bold}{self.current_title}{self.term.normal}")
            if self.current_author:
                print(f"Author: {self.current_author}")
            
            # Brief pause to show success message
            with self.term.cbreak():
                self.term.inkey(timeout=2)
                
            return False  # Exit the choosing source loop
            
        except Exception as e:
            # Show error message
            print(f"\n{self.term.bright_red}✗ Error:{self.term.normal} {e}")
            print(f"\n{self.term.dim}Press any key to try again...{self.term.normal}")
            
            self.current_url = None
            with self.term.cbreak():
                self.term.inkey()
                
            return True  # Stay in the choosing source loop
    
    def _handle_file_source(self):
        """Handle file source selection."""
        # Get HTML file source for specific methods
        html_source = self.article_manager.get_html_source()
        
        # Get available HTML files
        html_files = html_source.get_available_files()
        
        if not html_source.display_available_files(html_files):
            return True  # Stay in the choosing source loop if no files available
        
        # Create list of options from HTML files and add a "Back" option
        file_options = []
        for i, file_info in enumerate(html_files):
            # Extract just the filename for display
            file_name = os.path.basename(file_info)
            file_options.append(f"{file_name}")
        
        # Add back option
        file_options.append("Go back")
        
        # Display menu for file selection
        file_choice_idx = self._display_menu("Select HTML File", file_options)
        
        # Check if user selected "Go back"
        if file_choice_idx == len(html_files):
            return True  # Go back to source selection
        
        # Get the full file path from the chosen index
        self.current_file = html_source.get_file_path(file_choice_idx, html_files)
        
        # Extract article content
        try:
            self.current_title, self.current_content, self.current_author = self.article_manager.extract_from_file_path(self.current_file)
            return False  # Exit the choosing source loop
        except Exception as e:
            print(f"\nError: {e}")
            self.current_file = None
            return True  # Stay in the choosing source loop
    
    def _process_main_menu(self):
        """Display main menu and process user choice."""
        # Display all available output options
        outputs = self.publication_manager.get_available_outputs()
        options = [output_name for _, output_name in outputs] + ["Work on a new article", "Exit"]
        choice_idx = self._display_menu("Main Menu", options)
        
        # Check for work on new article option
        if choice_idx == len(outputs):
            # Reset to work on a new article
            self.reset_article()
            return True
        
        # Check for exit option
        elif choice_idx == len(outputs) + 1:
            # Display exit animation
            print(self.term.clear)
            print(f"\n{self.term.bright_blue}Thank you for using Kindle Article Sender!{self.term.normal}")
            print(f"{self.term.dim}Exiting...{self.term.normal}")
            for _ in range(5):
                print(f"{self.term.move_up()}{self.term.bright_blue}Thank you for using Kindle Article Sender!{self.term.normal}")
                print(f"{self.term.dim}Exiting...{self.term.dim}{' ' * _}{self.term.normal}")
                time.sleep(0.1)
            return False
        
        # Get output ID for the selected choice
        selected_output_id = outputs[choice_idx][0]
        
        # Handle the selected output
        source_reference = self.get_source_reference()
        
        # Clear screen and show processing message with spinner
        print(self.term.clear)
        print(f"\n{self.term.bright_cyan}Processing:{self.term.normal} {self.term.bold}{self.current_title}{self.term.normal}")
        
        spinner_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        spinner_idx = 0
        
        def show_spinner(message):
            """Display a loading spinner with a message."""
            nonlocal spinner_idx
            spinner = spinner_chars[spinner_idx % len(spinner_chars)]
            spinner_idx += 1
            print(f"{self.term.move_up(1)}\r{self.term.bright_yellow}{spinner} {message}...{' ' * 20}{self.term.normal}")
            
        # Process according to selected output
        if selected_output_id == "print":
            print("")  # Add space for spinner
            show_spinner("Formatting article for display")
            time.sleep(0.5)  # Simulate processing
            
            self.publication_manager.print_article(
                self.current_title,
                self.current_content,
                source_reference,
                self.current_author
            )
            
        elif selected_output_id == "epub":
            print("")  # Add space for spinner
            show_spinner("Preparing ePub creation")
            time.sleep(0.5)  # Simulate processing
            
            # Clear spinner line
            print(f"{self.term.move_up(1)}\r{' ' * 50}")
            
            # Ask for output directory with styled input
            print(f"\n{self.term.bright_blue}┌{'─' * 50}┐{self.term.normal}")
            print(f"{self.term.bright_blue}│{self.term.normal} Output directory (press Enter for default): ", end="")
            output_dir = input("").strip()
            print(f"{self.term.bright_blue}└{'─' * 50}┘{self.term.normal}")
            
            print("")  # Add space for spinner
            show_spinner("Generating ePub file")
            time.sleep(0.5)  # Simulate processing
            show_spinner("Writing content")
            time.sleep(0.3)  # Simulate processing
            show_spinner("Finalizing ePub")
            time.sleep(0.2)  # Simulate processing
            
            # Generate the ePub
            result = self.publication_manager.create_epub(
                self.current_title,
                self.current_content,
                source_reference,
                output_dir if output_dir else None,
                self.current_author
            )
            
            # Show success message
            print(f"{self.term.move_up(1)}\r{self.term.bright_green}✓ ePub created successfully!{' ' * 30}{self.term.normal}")
            
        elif selected_output_id == "kindle":
            print("")  # Add space for spinner
            steps = ["Preparing article", "Generating ePub", "Establishing connection", "Sending to Kindle"]
            
            for step in steps:
                show_spinner(step)
                time.sleep(0.5)  # Simulate processing steps
            
            # Send to Kindle
            self.publication_manager.send_to_kindle(
                self.current_title,
                self.current_content,
                source_reference,
                self.current_file,
                self.current_author
            )
            
            # Show success message
            print(f"{self.term.move_up(1)}\r{self.term.bright_green}✓ Article sent to Kindle!{' ' * 30}{self.term.normal}")
            
        else:
            # Generic handling for new output types
            print("")  # Add space for spinner
            show_spinner(f"Processing with {options[choice_idx]}")
            time.sleep(0.5)  # Simulate processing
            
            self.publication_manager.process_with_output(
                selected_output_id,
                self.current_title,
                self.current_content,
                source_reference,
                self.current_file,
                self.current_author
            )
        
        # After each operation, ask if user wants to continue with styled prompt
        print(f"\n{self.term.bright_cyan}┌{'─' * 50}┐{self.term.normal}")
        print(f"{self.term.bright_cyan}│{self.term.normal} Press {self.term.bold}Enter{self.term.normal} to continue or type {self.term.bold}exit{self.term.normal} to quit: ", end="")
        continue_prompt = input("").strip().lower()
        print(f"{self.term.bright_cyan}└{'─' * 50}┘{self.term.normal}")
        
        if continue_prompt == 'exit':
            # Display exit animation
            print(self.term.clear)
            print(f"\n{self.term.bright_blue}Thank you for using Kindle Article Sender!{self.term.normal}")
            print(f"{self.term.dim}Exiting...{self.term.normal}")
            for _ in range(5):
                print(f"{self.term.move_up()}{self.term.bright_blue}Thank you for using Kindle Article Sender!{self.term.normal}")
                print(f"{self.term.dim}Exiting...{self.term.dim}{' ' * _}{self.term.normal}")
                time.sleep(0.1)
            return False
        
        return True
    
    def _show_help_overlay(self):
        """Display a help overlay with keyboard shortcuts and tips."""
        # Save current screen
        with self.term.fullscreen(), self.term.cbreak(), self.term.hidden_cursor():
            # Display help screen
            print(self.term.clear)
            
            # Header
            print(f"\n{self.term.bold_white}{self.term.center('Keyboard Shortcuts and Help')}{self.term.normal}")
            print(f"{self.term.center('=' * 30)}\n")
            
            # Navigation shortcuts
            print(f"{self.term.bright_yellow}Navigation{self.term.normal}")
            print(f"  {self.term.bright_cyan}↑/↓{self.term.normal}: Move between options")
            print(f"  {self.term.bright_cyan}Enter{self.term.normal}: Select the highlighted option")
            print(f"  {self.term.bright_cyan}Esc/q{self.term.normal}: Go back or exit current menu")
            print(f"  {self.term.bright_cyan}h{self.term.normal}: Show this help screen\n")
            
            # General tips
            print(f"{self.term.bright_yellow}Tips{self.term.normal}")
            print(f"  • You can paste URLs directly when prompted")
            print(f"  • HTML files should be stored in the 'html_articles' folder")
            print(f"  • Generated ePub files are saved in 'epub_output' by default")
            print(f"  • Email settings can be configured in config.json\n")
            
            # Additional help
            print(f"{self.term.bright_yellow}About{self.term.normal}")
            print(f"  Kindle Article Sender helps you easily send web articles")
            print(f"  and HTML files to your Kindle device for distraction-free reading.\n")
            
            # Press any key to continue
            print(f"\n{self.term.center(f'{self.term.dim}Press any key to return...{self.term.normal}')}")
            
            # Wait for key press to exit help
            self.term.inkey()
            
            # Return to the previous screen (no need to redraw, as we're using fullscreen context)


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
            title, content, author, source_reference, source_file = self._extract_article()
            
            # Handle debug extraction if requested
            if self.args.debug_extraction:
                self.publication_manager.print_article(title, content, source_reference, author)
                sys.exit(0)
            
            # Handle sending or generating ePub
            if self.args.no_send:
                self.publication_manager.create_epub(
                    title, 
                    content, 
                    source_reference, 
                    self.args.output_dir,
                    author
                )
                print("File was not sent to Kindle as --no-send flag was used.")
            else:
                # Send to Kindle
                self.publication_manager.send_to_kindle(
                    title,
                    content,
                    source_reference,
                    source_file,
                    author
                )
                
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    
    def _extract_article(self):
        """Extract article content based on command line arguments."""
        if self.args.url:
            title, content, author = self.article_manager.extract_from_url(self.args.url)
            source_reference = self.args.url
            source_file = None
        elif self.args.file:
            title, content, author = self.article_manager.extract_from_file_path(self.args.file)
            source_reference = format_source_reference(file_path=self.args.file)
            source_file = self.args.file
        else:
            raise ValueError("No URL or file specified")
            
        return title, content, author, source_reference, source_file


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
