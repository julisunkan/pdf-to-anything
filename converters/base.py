from abc import ABC, abstractmethod

class BaseConverter(ABC):
    """Base class for all converters"""
    
    name: str = None
    input_format: str = 'pdf'
    output_format: str = None
    
    @abstractmethod
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        """Convert file from input_format to output_format"""
        pass
    
    @staticmethod
    def is_available() -> bool:
        """Check if converter dependencies are available"""
        return True
