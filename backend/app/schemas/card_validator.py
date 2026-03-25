import re

class CardValidator:
    @staticmethod
    def is_valid_card_num(card_num: str) -> bool:
        """
        Returns True if card_num is only digits and is between 13 to 19 digits
        Returns False otherwise
        """
        # Regex for only card digits with a length between 13 to 19 digits
        pattern = r"^\d{13,19}$"
        return re.match(pattern, card_num) is not None

    @staticmethod
    def is_valid_cvc(cvc: str) -> bool:
        """
        Returns True if CVC is only digits and 3-4 characters long
        """
        # Regex pattern to test CVC
        pattern = r"^\d{3,4}$"
        return re.match(pattern, cvc) is not None
    
    @staticmethod
    def is_valid_expiry(expiry: str) -> bool:
        """
        Returns True if expiry matches YYYY-MM format
        Validates month is within 01 (Jan) to 12 (Dec)
        """
        # Regex pattern to test expiry date (ex: 2026-09)
        pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
        return re.match(pattern, expiry) is not None
    
    @staticmethod
    def is_valid_name(name: str) -> bool:
        """
        Returns True if name contains only letters and no spaces
        No special characters allowed
        """
        pattern = r"^[a-zA-Z\s]+$"
        return re.match(pattern, name) is not None

    @staticmethod
    def is_valid_address(address: str) -> bool:
        """
        Returns True if address contains only letters, spaces, "-", or ","
        No other special characters allowed
        """
        pattern = r"^[a-zA-Z0-9\s\-,]+$"
        return re.match(pattern, address) is not None