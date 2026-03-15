import re

class UserValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Returns True if email matches valid format
        Returns False otherwise
        """
        # Regex pattern to test email
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """
        Returns True if password meets all requirements
        - 8 characters long minimum
        - At least 1 uppercase letter
        - At least 1 special character 
        Returns False otherwise.
        """
        # Test Values
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
