"""
AI Hackathon Judge System - NLP Analyzer

This module provides NLP-based text analysis for hackathon project submissions,
including TF-IDF analysis, semantic coherence checking, and substance detection.
"""

import re
from typing import Dict, List, Tuple, Set
from collections import Counter
import math


class NLPAnalyzer:
    """
    NLP analyzer for hackathon project text analysis.
    
    This analyzer:
    - Calculates text statistics and readability
    - Detects substance vs fluff ratio
    - Identifies key concepts using TF-IDF
    - Checks semantic coherence between sections
    - Validates tech stack mentions
    """
    
    def __init__(self):
        """Initialize the NLP analyzer with stop words and patterns."""
        self.stop_words = self._get_stop_words()
        self.technical_terms = self._get_technical_terms()
    
    def _get_stop_words(self) -> Set[str]:
        """Get common English stop words."""
        return {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare", "ought",
            "used", "it", "its", "this", "that", "these", "those", "i", "we", "you",
            "he", "she", "they", "me", "us", "him", "her", "them", "my", "our", "your",
            "his", "their", "what", "which", "who", "whom", "whose", "when", "where",
            "why", "how", "all", "each", "every", "both", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "also", "now", "here", "there", "then", "once"
        }
    
    def _get_technical_terms(self) -> Set[str]:
        """Get common technical terms that indicate substance."""
        return {
            "algorithm", "api", "architecture", "authentication", "authorization",
            "backend", "frontend", "database", "cache", "server", "client",
            "framework", "library", "module", "component", "service", "microservice",
            "container", "docker", "kubernetes", "deployment", "ci/cd", "pipeline",
            "testing", "unit", "integration", "e2e", "performance", "optimization",
            "security", "encryption", "protocol", "http", "rest", "graphql", "websocket",
            "machine learning", "neural", "model", "training", "inference", "dataset",
            "preprocessing", "feature", "classification", "regression", "clustering",
            "validation", "cross-validation", "accuracy", "precision", "recall",
            "react", "vue", "angular", "node", "python", "javascript", "typescript",
            "sql", "nosql", "mongodb", "postgresql", "redis", "elasticsearch",
            "aws", "gcp", "azure", "cloud", "serverless", "lambda", "function"
        }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dict: Analysis results including statistics and scores
        """
        # Basic statistics
        words = self._tokenize(text)
        sentences = self._split_sentences(text)
        
        # Calculate metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = word_count / max(1, sentence_count)
        
        # Vocabulary richness
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / max(1, word_count)
        
        # Technical content ratio
        technical_words = [w for w in words if w.lower() in self.technical_terms]
        technical_ratio = len(technical_words) / max(1, word_count)
        
        # Substance score (higher = more substantive)
        substance_score = self._calculate_substance_score(
            words, vocabulary_richness, technical_ratio, avg_sentence_length
        )
        
        # Readability score
        readability_score = self._calculate_readability(words, sentences)
        
        # Key concepts using TF-IDF-like approach
        key_concepts = self._extract_key_concepts(words)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "vocabulary_richness": round(vocabulary_richness, 3),
            "technical_ratio": round(technical_ratio, 3),
            "substance_score": round(substance_score, 1),
            "readability_score": round(readability_score, 1),
            "key_concepts": key_concepts[:10]
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        # Filter out stop words and very short words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        return words
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _calculate_substance_score(self, words: List[str], vocab_richness: float,
                                    tech_ratio: float, avg_sent_len: float) -> float:
        """
        Calculate a substance score indicating how substantive the text is.
        
        High scores indicate substantive content.
        Low scores indicate fluff or filler content.
        """
        score = 50  # Base score
        
        # Reward vocabulary richness
        if vocab_richness > 0.6:
            score += 15
        elif vocab_richness > 0.4:
            score += 8
        
        # Reward technical content
        if tech_ratio > 0.05:
            score += 20
        elif tech_ratio > 0.02:
            score += 10
        
        # Optimal sentence length (not too short, not too long)
        if 12 <= avg_sent_len <= 25:
            score += 10
        elif avg_sent_len < 8:
            score -= 10  # Too choppy
        elif avg_sent_len > 35:
            score -= 5  # Too complex
        
        # Word count contribution
        word_count = len(words)
        if word_count > 300:
            score += 5
        elif word_count < 100:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_readability(self, words: List[str], sentences: List[str]) -> float:
        """
        Calculate a readability score (0-100).
        
        Based on simplified Flesch-like formula.
        Higher = more readable.
        """
        if not words or not sentences:
            return 50
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        avg_sent_length = len(words) / len(sentences)
        
        # Simplified readability: penalize long words and long sentences
        score = 100 - (avg_word_length * 5) - (avg_sent_length * 1.5)
        
        return max(0, min(100, score))
    
    def _extract_key_concepts(self, words: List[str]) -> List[str]:
        """
        Extract key concepts using term frequency.
        
        Uses a TF-IDF-like approach to find important terms.
        """
        # Count word frequencies
        word_freq = Counter(words)
        
        # Filter to meaningful words (appear at least twice or are technical)
        meaningful = {
            word: freq for word, freq in word_freq.items()
            if freq >= 2 or word in self.technical_terms
        }
        
        # Sort by frequency
        sorted_words = sorted(meaningful.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:10]]
    
    def check_coherence(self, problem: str, solution: str, innovation: str) -> Dict:
        """
        Check semantic coherence between problem, solution, and innovation.
        
        Args:
            problem: Problem statement text
            solution: Solution description text
            innovation: Innovation description text
            
        Returns:
            Dict: Coherence analysis results
        """
        # Tokenize each section
        problem_words = set(self._tokenize(problem))
        solution_words = set(self._tokenize(solution))
        innovation_words = set(self._tokenize(innovation))
        
        # Calculate overlaps (measure of coherence)
        prob_sol_overlap = len(problem_words & solution_words) / max(1, len(problem_words | solution_words))
        sol_innov_overlap = len(solution_words & innovation_words) / max(1, len(solution_words | innovation_words))
        
        # Coherence score
        coherence_score = ((prob_sol_overlap + sol_innov_overlap) / 2) * 100
        
        # Identify shared concepts
        all_shared = problem_words & solution_words & innovation_words
        
        return {
            "problem_solution_coherence": round(prob_sol_overlap * 100, 1),
            "solution_innovation_coherence": round(sol_innov_overlap * 100, 1),
            "overall_coherence": round(coherence_score, 1),
            "shared_concepts": list(all_shared)[:5],
            "is_coherent": coherence_score > 15
        }
    
    def detect_copy_paste(self, text: str) -> Dict:
        """
        Detect signs of copy-paste or template content.
        
        Looks for:
        - Placeholder patterns
        - Generic template phrases
        - Inconsistent formatting
        """
        text_lower = text.lower()
        
        # Check for placeholder patterns
        placeholders = [
            "[insert", "[your", "[project name]", "lorem ipsum",
            "xxx", "todo", "tbd", "placeholder", "[description]",
            "example.com", "sample text", "your company"
        ]
        placeholder_count = sum(1 for p in placeholders if p in text_lower)
        
        # Check for template phrases
        templates = [
            "our innovative solution", "cutting-edge technology",
            "revolutionize the industry", "game-changing approach",
            "state-of-the-art", "best-in-class", "world-class",
            "leveraging the power of", "harnessing the potential"
        ]
        template_count = sum(1 for t in templates if t in text_lower)
        
        # Calculate copy-paste score
        copy_paste_score = min(100, (placeholder_count * 20) + (template_count * 10))
        
        return {
            "placeholder_count": placeholder_count,
            "template_phrase_count": template_count,
            "copy_paste_score": copy_paste_score,
            "is_likely_template": copy_paste_score > 30
        }
    
    def analyze_tech_stack(self, tech_stack: str) -> Dict:
        """
        Analyze the tech stack for validity and depth.
        
        Args:
            tech_stack: The tech stack string
            
        Returns:
            Dict: Tech stack analysis
        """
        tech_lower = tech_stack.lower()
        
        # Known technologies by category
        categories = {
            "frontend": ["react", "vue", "angular", "svelte", "next.js", "nuxt", "html", "css", "tailwind"],
            "backend": ["node", "express", "django", "flask", "fastapi", "spring", "rails", "nest"],
            "database": ["postgresql", "mysql", "mongodb", "redis", "firebase", "supabase", "sqlite"],
            "ml_ai": ["tensorflow", "pytorch", "sklearn", "keras", "openai", "langchain", "huggingface"],
            "cloud": ["aws", "gcp", "azure", "vercel", "netlify", "heroku", "docker", "kubernetes"],
            "mobile": ["react native", "flutter", "swift", "kotlin", "expo"]
        }
        
        detected = {}
        for category, techs in categories.items():
            found = [tech for tech in techs if tech in tech_lower]
            if found:
                detected[category] = found
        
        # Count total technologies
        total_techs = sum(len(techs) for techs in detected.values())
        
        # Calculate tech depth score
        category_count = len(detected)
        depth_score = min(100, (category_count * 20) + (total_techs * 5))
        
        return {
            "detected_technologies": detected,
            "total_tech_count": total_techs,
            "category_count": category_count,
            "tech_depth_score": depth_score,
            "is_full_stack": "frontend" in detected and "backend" in detected,
            "has_database": "database" in detected,
            "has_ml": "ml_ai" in detected
        }


def get_text_statistics(text: str) -> Dict:
    """
    Quick utility function to get basic text statistics.
    
    Args:
        text: Input text
        
    Returns:
        Dict: Basic statistics
    """
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    
    return {
        "character_count": len(text),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": text.count('\n\n') + 1,
        "avg_word_length": sum(len(w) for w in words) / max(1, len(words))
    }
