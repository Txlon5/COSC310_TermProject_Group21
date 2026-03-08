import hashlib
import re

class UserValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        length_valid = False
        capitals = False
        special_character = False

        # Validate Length is above 8 characters
        if len(password) >= 8:
            length_valid = True
        else: 
            return False

        # Check that password has atleast 1 capital
        if re.search(r'[A-Z]', password):
            capitals = True
        else:
            return False

        # Check that password has atleast 1 special character
        if re.search(r'[@_!#$%^&*()<>?/\|}{~:]', password):
            special_character = True
        else:
            return False

        # Check all conditions are met
        if (length_valid and capitals and special_character):
            return True
        
        # Return if conditions not met and has not returned yet
        return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
