#!/usr/bin/env python3
from urllib.parse import urlparse
import re
from abc import ABC, abstractmethod

class DomainHandler(ABC):
    """Base class for domain-specific handlers."""
    
    @property
    @abstractmethod
    def domain(self):
        """The domain this handler is for (e.g., 'example.com')."""
        pass
    
    def pre_validation(self, url):
        """Run before attempting to extract content.
        
        Args:
            url: The URL being processed
            
        Returns:
            tuple: (is_valid, message) where:
                - is_valid: True if extraction should proceed, False otherwise
                - message: Optional user-friendly message (None if no message)
        """
        return True, None
    
    def post_processing(self, title, content):
        """Process the extracted content.
        
        Args:
            title: The extracted title
            content: The extracted content
            
        Returns:
            tuple: (title, content) potentially modified
        """
        return title, content


class SubstackHandler(DomainHandler):
    """Handler for Substack domains."""
    
    @property
    def domain(self):
        return "substack.com"
    
    def pre_validation(self, url):
        return False, ("Substack articles require JavaScript to render content and cannot be "
                      "extracted automatically. Consider saving the article as HTML from "
                      "your browser and using the 'From a HTML File' option instead.")


class CenitalHandler(DomainHandler):
    """Handler for Cenital.com."""
    
    @property
    def domain(self):
        return "cenital.com"
    
    def post_processing(self, title, content):
        # Remove "Otras lecturas" section and everything after it
        if "Otras lecturas" in content:
            content = content.split("Otras lecturas")[0].strip()
        # Remove subscription message
        subscription_text = "¿Por qué pagar por algo que puedo leer gratis? En Cenital entendemos al periodismo como un servicio público. Por eso nuestras notas siempre estarán accesibles para todos. Pero investigar es caro y la parte más ardua del trabajo periodístico no se ve. Por eso le pedimos a quienes puedan que se sumen a nuestro círculo de Mejores amigos y nos permitan seguir creciendo. Si te gusta lo que hacemos, sumate vos también. Sumate"
        if subscription_text in content:
            content = content.replace(subscription_text, "").strip()
            # Remove extra blank lines that might appear after removing the text
            content = re.sub(r'\n{3,}', '\n\n', content)
        return title, content


class DomainHandlerRegistry:
    """Registry for domain handlers."""
    
    def __init__(self):
        self._handlers = {}
        
        # Register built-in handlers
        self.register(SubstackHandler())
        self.register(CenitalHandler())
    
    def register(self, handler):
        """Register a new domain handler."""
        self._handlers[handler.domain] = handler
    
    def get_handler(self, url):
        """Get the appropriate handler for a URL."""
        if not url:
            return None
            
        domain = urlparse(url).netloc
        
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Check for exact domain match
        if domain in self._handlers:
            return self._handlers[domain]
            
        # Check for subdomain (e.g. something.substack.com)
        for handler_domain, handler in self._handlers.items():
            if domain.endswith(f".{handler_domain}"):
                return handler
                
        return None
    
    def run_pre_validation(self, url):
        """Run pre-validation for a URL if a handler exists."""
        handler = self.get_handler(url)
        if handler:
            return handler.pre_validation(url)
        return True, None
    
    def run_post_processing(self, url, title, content):
        """Run post-processing for a URL if a handler exists."""
        handler = self.get_handler(url)
        if handler:
            return handler.post_processing(title, content)
        return title, content


# Global instance
domain_registry = DomainHandlerRegistry()


def register_domain_handler(handler):
    """Register a new domain handler with the global registry."""
    domain_registry.register(handler)