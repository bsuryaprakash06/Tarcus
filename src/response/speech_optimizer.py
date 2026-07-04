import re

class SpeechOptimizer:
    """
    Optimizes text for Text-to-Speech engines purely through presentation formatting.
    Does NOT alter factual meaning or semantic grammar.
    """
    
    @staticmethod
    def optimize(text: str) -> str:
        """
        Cleans up spacing and punctuation for better TTS rhythm.
        """
        if not text:
            return ""
            
        # 1. Collapse multiple spaces into a single space
        text = re.sub(r'\s+', ' ', text)
        
        # 2. Ensure exactly one space after ending punctuation if a letter follows immediately
        text = re.sub(r'([.?!])([a-zA-Z])', r'\1 \2', text)
        
        # 3. Trim leading and trailing whitespace
        return text.strip()
