"""Text processing and cleaning utilities."""

import logging
import re
from typing import List


class TranscriptionCleaner:
    """Handles cleaning and post-processing of transcription text."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._subtitle_patterns = [
            r'sottotitoli creati dalla comunità amara\.org.*?qtss\.?',
            r'subtitles created by.*?community.*?amara\.org.*?qtss\.?',
            r'sottotitoli e revisione a cura di.*?qtss\.?',
            r'subtitles and revision by.*?qtss\.?',
            r'traduzione e adattamento.*?qtss\.?',
            r'translation and adaptation.*?qtss\.?'
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean up transcription by removing repetitive patterns and hallucinations."""
        if not text:
            return text
        
        original_length = len(text)
        
        # Remove common subtitle/credit patterns
        text = self._remove_subtitle_credits(text)
        
        # Remove excessive repetitive patterns
        text = self._remove_repetitive_patterns(text)
        text = self._remove_trailing_repetitions(text)
        text = self._cleanup_spaces(text)
        
        cleaned_text = text.strip()
        
        # Log cleaning results
        if len(cleaned_text) < original_length:
            reduction = original_length - len(cleaned_text)
            self.logger.info(f"Text cleaning: removed {reduction} characters ({reduction/original_length*100:.1f}%)")
        
        return cleaned_text
    
    def _remove_subtitle_credits(self, text: str) -> str:
        """Remove common subtitle/credit patterns."""
        for pattern in self._subtitle_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        return text
    
    def _remove_repetitive_patterns(self, text: str) -> str:
        """Remove patterns where short words repeat excessively."""
        # Match patterns where the same short word/syllable repeats many times
        text = re.sub(r'\b(\w{1,3})(?:\s+\1){10,}\b', r'\1', text, flags=re.IGNORECASE)
        
        # Remove patterns where single characters repeat excessively
        text = re.sub(r'\b(\w)\s+(?:\1\s+){5,}', r'\1 ', text)
        
        # Remove very long sequences of identical short words
        text = re.sub(r'\b(\w{1,4})(?:\s+\1){8,}(?:\s|$)', ' ', text)
        
        return text
    
    def _remove_trailing_repetitions(self, text: str) -> str:
        """Remove repetitive endings from text."""
        words = text.strip().split()
        if len(words) <= 4:
            return text
        
        # Check if the last several words are repetitive
        last_word = words[-1]
        repetition_count = 0
        
        for i in range(len(words) - 1, -1, -1):
            if words[i] == last_word:
                repetition_count += 1
            else:
                break
        
        # If we found many repetitions of the same word at the end, remove them
        if repetition_count > 5:
            words = words[:-repetition_count + 1]
            text = ' '.join(words)
        
        # Remove standalone single letters repeated at the end
        text = re.sub(r'\s+([a-zA-Z])(?:\s+\1){2,}\s*$', '', text)
        
        return text
    
    def _cleanup_spaces(self, text: str) -> str:
        """Clean up multiple spaces."""
        return re.sub(r'\s+', ' ', text)