"""
AI Hackathon Judge System - Input Validators

This module provides comprehensive input validation and cleaning
for hackathon project submissions.
"""

import re
from typing import Optional, Tuple, List


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class ProjectValidator:
    """
    Validator for hackathon project submissions.
    
    Validates:
    - Required fields presence
    - Field length limits
    - URL formats
    - Content quality
    """
    
    # Field length limits
    LIMITS = {
        "project_title": (3, 100),
        "problem_statement": (50, 2000),
        "solution_description": (100, 3000),
        "tech_stack": (10, 500),
        "innovation_description": (50, 1500),
        "target_users": (20, 500),
        "future_scope": (50, 1000)
    }
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def validate_all(self, data: dict) -> Tuple[bool, List[str]]:
        """
        Validate all fields in the submission.
        
        Args:
            data: Dictionary of form data
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Validate required text fields
        for field, (min_len, max_len) in self.LIMITS.items():
            value = data.get(field, "")
            if not value or not value.strip():
                errors.append(f"{self._format_field_name(field)} is required")
            elif len(value.strip()) < min_len:
                errors.append(f"{self._format_field_name(field)} must be at least {min_len} characters")
            elif len(value.strip()) > max_len:
                errors.append(f"{self._format_field_name(field)} must be at most {max_len} characters")
        
        # Validate team size
        team_size = data.get("team_size")
        if team_size is None:
            errors.append("Team size is required")
        elif not isinstance(team_size, int) or team_size < 1 or team_size > 10:
            errors.append("Team size must be between 1 and 10")
        
        # Validate GitHub link
        github_link = data.get("github_link", "")
        if not github_link or not github_link.strip():
            errors.append("GitHub repository link is required")
        elif not self._is_valid_github_url(github_link):
            errors.append("Please provide a valid GitHub repository URL")
        
        # Validate demo link (optional)
        demo_link = data.get("demo_link", "")
        if demo_link and demo_link.strip():
            if not self._is_valid_url(demo_link):
                errors.append("Demo link must be a valid URL")
        
        return len(errors) == 0, errors
    
    def _format_field_name(self, field: str) -> str:
        """Convert field name to human-readable format."""
        return field.replace("_", " ").title()
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Check if URL is a valid GitHub repository link."""
        url = url.strip().lower()
        
        patterns = [
            r'^https?://github\.com/[\w\-]+/[\w\-\.]+/?.*$',
            r'^https?://www\.github\.com/[\w\-]+/[\w\-\.]+/?.*$',
        ]
        
        return any(re.match(pattern, url) for pattern in patterns)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        url = url.strip()
        pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(pattern, url))
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text input.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove potentially harmful HTML/script tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def clean_url(self, url: str) -> str:
        """
        Clean and normalize URL input.
        
        Args:
            url: Raw URL input
            
        Returns:
            Cleaned URL
        """
        if not url:
            return ""
        
        url = url.strip()
        
        # Add https:// if missing
        if url and not url.startswith(('http://', 'https://')):
            if url.startswith('github.com'):
                url = 'https://' + url
        
        return url


def validate_project_data(data: dict) -> Tuple[bool, List[str], dict]:
    """
    Validate and clean project submission data.
    
    Args:
        data: Raw form data dictionary
        
    Returns:
        Tuple of (is_valid, errors, cleaned_data)
    """
    validator = ProjectValidator()
    
    # Clean data
    cleaned = {}
    for key, value in data.items():
        if key in ["github_link", "demo_link"]:
            cleaned[key] = validator.clean_url(str(value) if value else "")
        elif key == "team_size":
            try:
                cleaned[key] = int(value) if value else None
            except (ValueError, TypeError):
                cleaned[key] = None
        else:
            cleaned[key] = validator.clean_text(str(value) if value else "")
    
    # Validate
    is_valid, errors = validator.validate_all(cleaned)
    
    return is_valid, errors, cleaned


def get_field_help_text(field: str) -> str:
    """
    Get help text for a form field.
    
    Args:
        field: Field name
        
    Returns:
        Help text string
    """
    help_texts = {
        "project_title": "A clear, memorable name for your project",
        "team_size": "Number of team members (1-10)",
        "problem_statement": "What problem does your project solve? Be specific about who faces this problem and why it matters.",
        "solution_description": "How does your project solve the problem? Describe your approach, architecture, and key features.",
        "tech_stack": "List the technologies used (e.g., React, Node.js, MongoDB, TensorFlow)",
        "innovation_description": "What makes your solution unique? How is it different from existing solutions?",
        "github_link": "Link to your GitHub repository (e.g., https://github.com/username/project)",
        "demo_link": "Optional link to a live demo or video",
        "target_users": "Who would use this? Describe your target audience and industry.",
        "future_scope": "What are your plans for scaling and future development?"
    }
    
    return help_texts.get(field, "")


def get_field_placeholder(field: str) -> str:
    """
    Get placeholder text for a form field.
    
    Args:
        field: Field name
        
    Returns:
        Placeholder text
    """
    placeholders = {
        "project_title": "e.g., SmartPark - AI Parking Management",
        "problem_statement": "Describe the problem in detail...",
        "solution_description": "Explain how your project solves this problem...",
        "tech_stack": "e.g., Python, FastAPI, PostgreSQL, React, Docker",
        "innovation_description": "What's new or different about your approach?",
        "github_link": "https://github.com/username/project-name",
        "demo_link": "https://your-demo-link.com (optional)",
        "target_users": "Who will use this product?",
        "future_scope": "How will this project grow?"
    }
    
    return placeholders.get(field, "")
