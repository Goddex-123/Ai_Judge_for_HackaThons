"""
AI Hackathon Judge System - Project Data Model

This module defines the Pydantic-based data model for hackathon projects,
including input validation, cleaning, and type-safe representation.
"""

from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, List
import re


class HackathonProject(BaseModel):
    """
    Data model for a hackathon project submission.
    
    All fields are validated and cleaned automatically.
    """
    
    # Required fields
    project_title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="The name of the hackathon project"
    )
    
    team_size: int = Field(
        ...,
        ge=1,
        le=10,
        description="Number of team members (1-10)"
    )
    
    problem_statement: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="What problem does this project solve?"
    )
    
    solution_description: str = Field(
        ...,
        min_length=100,
        max_length=3000,
        description="How does the project solve the problem?"
    )
    
    tech_stack: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Technologies used in the project"
    )
    
    innovation_description: str = Field(
        ...,
        min_length=50,
        max_length=1500,
        description="What makes this solution innovative?"
    )
    
    github_link: str = Field(
        ...,
        description="Link to the GitHub repository"
    )
    
    target_users: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Who are the target users/industry?"
    )
    
    future_scope: str = Field(
        ...,
        min_length=50,
        max_length=1000,
        description="Future plans and scalability"
    )
    
    # Optional fields
    demo_link: Optional[str] = Field(
        None,
        description="Link to live demo (optional)"
    )
    
    @field_validator('project_title')
    @classmethod
    def clean_title(cls, v: str) -> str:
        """Clean and normalize project title."""
        # Remove extra whitespace
        v = ' '.join(v.split())
        # Capitalize first letter of each word
        v = v.title()
        return v
    
    @field_validator('problem_statement', 'solution_description', 'innovation_description', 
                     'target_users', 'future_scope')
    @classmethod
    def clean_text(cls, v: str) -> str:
        """Clean and normalize text fields."""
        # Remove extra whitespace
        v = ' '.join(v.split())
        # Remove potentially harmful HTML/script tags
        v = re.sub(r'<[^>]+>', '', v)
        return v
    
    @field_validator('tech_stack')
    @classmethod
    def clean_tech_stack(cls, v: str) -> str:
        """Clean and normalize tech stack."""
        # Remove extra whitespace
        v = ' '.join(v.split())
        # Normalize separators
        v = re.sub(r'[,;|/]+', ', ', v)
        return v
    
    @field_validator('github_link')
    @classmethod
    def validate_github_link(cls, v: str) -> str:
        """Validate GitHub repository link."""
        v = v.strip()
        if not v:
            raise ValueError('GitHub link is required')
        
        # Check if it's a valid GitHub URL
        github_patterns = [
            r'^https?://github\.com/[\w\-]+/[\w\-\.]+/?$',
            r'^https?://www\.github\.com/[\w\-]+/[\w\-\.]+/?$',
            r'^github\.com/[\w\-]+/[\w\-\.]+/?$'
        ]
        
        is_valid = any(re.match(pattern, v, re.IGNORECASE) for pattern in github_patterns)
        if not is_valid:
            # Be lenient - just check if it contains github.com
            if 'github.com' not in v.lower():
                raise ValueError('Please provide a valid GitHub repository URL')
        
        return v
    
    @field_validator('demo_link')
    @classmethod
    def validate_demo_link(cls, v: Optional[str]) -> Optional[str]:
        """Validate demo link if provided."""
        if v is None or v.strip() == '':
            return None
        
        v = v.strip()
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        if not re.match(url_pattern, v):
            raise ValueError('Please provide a valid demo URL')
        
        return v
    
    def get_all_text(self) -> str:
        """
        Get all text content from the project for NLP analysis.
        
        Returns:
            str: Combined text from all descriptive fields
        """
        text_parts = [
            self.project_title,
            self.problem_statement,
            self.solution_description,
            self.tech_stack,
            self.innovation_description,
            self.target_users,
            self.future_scope
        ]
        return ' '.join(text_parts)
    
    def get_word_count(self) -> int:
        """Get total word count of the submission."""
        return len(self.get_all_text().split())
    
    def to_dict(self) -> dict:
        """Convert project to dictionary for serialization."""
        return {
            "project_title": self.project_title,
            "team_size": self.team_size,
            "problem_statement": self.problem_statement,
            "solution_description": self.solution_description,
            "tech_stack": self.tech_stack,
            "innovation_description": self.innovation_description,
            "github_link": self.github_link,
            "demo_link": self.demo_link,
            "target_users": self.target_users,
            "future_scope": self.future_scope
        }


class ProjectScore(BaseModel):
    """
    Data model for a project's evaluation scores.
    """
    
    project_title: str
    
    # Individual criterion scores (0-100)
    innovation_score: float = Field(ge=0, le=100)
    technical_depth_score: float = Field(ge=0, le=100)
    problem_relevance_score: float = Field(ge=0, le=100)
    feasibility_score: float = Field(ge=0, le=100)
    scalability_score: float = Field(ge=0, le=100)
    ui_ux_score: float = Field(ge=0, le=100)
    real_world_impact_score: float = Field(ge=0, le=100)
    
    # Explanations for each score
    innovation_explanation: str = ""
    technical_depth_explanation: str = ""
    problem_relevance_explanation: str = ""
    feasibility_explanation: str = ""
    scalability_explanation: str = ""
    ui_ux_explanation: str = ""
    real_world_impact_explanation: str = ""
    
    # Penalty information
    buzzword_penalty: float = 0.0
    vagueness_penalty: float = 0.0
    overclaim_penalty: float = 0.0
    ai_generated_penalty: float = 0.0
    total_penalty: float = 0.0
    
    # Final weighted score
    raw_score: float = Field(ge=0, le=100)
    final_score: float = Field(ge=0, le=100)
    
    # Feedback
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    verdict: str = ""
    verdict_emoji: str = ""
    verdict_explanation: str = ""
    
    def get_criterion_scores(self) -> dict:
        """Get all criterion scores as a dictionary."""
        return {
            "innovation": {
                "score": self.innovation_score,
                "explanation": self.innovation_explanation
            },
            "technical_depth": {
                "score": self.technical_depth_score,
                "explanation": self.technical_depth_explanation
            },
            "problem_relevance": {
                "score": self.problem_relevance_score,
                "explanation": self.problem_relevance_explanation
            },
            "feasibility": {
                "score": self.feasibility_score,
                "explanation": self.feasibility_explanation
            },
            "scalability": {
                "score": self.scalability_score,
                "explanation": self.scalability_explanation
            },
            "ui_ux": {
                "score": self.ui_ux_score,
                "explanation": self.ui_ux_explanation
            },
            "real_world_impact": {
                "score": self.real_world_impact_score,
                "explanation": self.real_world_impact_explanation
            }
        }
