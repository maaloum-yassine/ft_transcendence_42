# validators/user_validators.py
import re
from rest_framework import serializers
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
# Définir les messages d'erreur
error_username = (
    "Starts with a letter: The username must start with a letter (A-Z or a-z).\n"
    "Allowed characters: Letters (A-Z, a-z), numbers (0-9), underscores (_), "
    "hyphens (-), and periods (.) are allowed in the middle of the name.\n"
    "Must not end with a symbol: The username must end with a letter or a number. "
    "Symbols (_, -, .) are not allowed at the end of the name.\n\n"
    "Valid examples: JohnPeter, John_Peter, John-Peter.42\n"
    "Invalid examples: _JohnPeter, JohnPeter!, John..Peter"
)

error_name = (
    "The name first or last  must begin with a letter, including accented letters (A-Z, a-z, A-ÿ).\n"
    "The name may contain symbols such as hyphens (-), apostrophes ('), spaces (\\s), or underscores (_) "
    "in the middle, but each segment after a symbol must begin with a letter.\n"
    "The name must end with a letter, it cannot end with a symbol, a number, or a space.\n"
    "It is possible to have multiple segments separated by a symbol (such as 'John Peter' or 'O'Connor')."
)



# Regular expression for first and last name validation
name_pattern = r"^[A-Za-zÀ-ÿ]+([-'\s_][A-Za-zÀ-ÿ]+)*$"
# Regular expression for username validation
username_pattern = r"^[A-Za-z][A-Za-z0-9._-]*[A-Za-z0-9]$"

def validate_password(data):
    """password rules validation"""
    if len(data['password']) < 4:
        raise serializers.ValidationError("Password must contain at least 4 characters.")
    if not any(char.isdigit() for char in data['password']):
        raise serializers.ValidationError("Password must contain at least one number.")
    if not any(char.isupper() for char in data['password']):
        raise serializers.ValidationError("Password must contain at least one capital letter.")
    if data['password'] != data['confirm_password']:
        raise serializers.ValidationError("Passwords do not match.")

def validate_name(name):
    """Validation pour les champs first_name et last_name"""
    if not re.match(name_pattern, name):
        raise serializers.ValidationError(error_name)

def validate_username(username):
    """Validation du nom d'utilisateur"""
    if not re.match(username_pattern, username):
        raise serializers.ValidationError(error_username)

def validate_email(email):
    """Validation du nom d'utilisateur"""
    validator = EmailValidator()
    try:
        validator(email)
    except ValidationError:    
        raise serializers.ValidationError("Invalid email!!")