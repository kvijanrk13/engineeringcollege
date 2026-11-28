"""
Custom validators for the dashboard app.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexityValidator:
    """
    Validate password complexity:
    - At least 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    def __init__(self, min_length=12):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        errors = []
        
        if len(password) < self.min_length:
            errors.append(_(f"Password must be at least {self.min_length} characters long."))
        
        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least one uppercase letter."))
        
        if not re.search(r'[a-z]', password):
            errors.append(_("Password must contain at least one lowercase letter."))
        
        if not re.search(r'\d', password):
            errors.append(_("Password must contain at least one digit."))
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/`~]', password):
            errors.append(_("Password must contain at least one special character."))
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append(_("Password must not contain repeating characters."))
        
        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append(_("Password must not contain sequential characters (e.g., abc, 123)."))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            f"Password must be at least {self.min_length} characters long and contain "
            "uppercase, lowercase, digit, and special character."
        )
    
    def _has_sequential_chars(self, password):
        """Check for sequential characters like abc, 123, etc."""
        password_lower = password.lower()
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm',
        ]
        
        for seq in sequences:
            for i in range(len(seq) - 2):
                subseq = seq[i:i+3]
                if subseq in password_lower or subseq[::-1] in password_lower:
                    return True
        return False