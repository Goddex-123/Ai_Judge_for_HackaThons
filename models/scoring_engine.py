"""
AI Hackathon Judge System - Scoring Engine

This is the core scoring logic that evaluates hackathon projects across
7 weighted criteria with penalties for buzzwords, vagueness, and overclaiming.
"""

import re
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SCORING_CRITERIA, BUZZWORDS, VAGUE_PHRASES, OVERCLAIM_PHRASES,
    TECHNICAL_DEPTH_SIGNALS, FEASIBILITY_SIGNALS, INNOVATION_SIGNALS,
    AI_GENERATED_PATTERNS, MAX_BUZZWORD_DENSITY, BUZZWORD_PENALTY,
    VAGUENESS_PENALTY, OVERCLAIM_PENALTY, AI_GENERATED_PENALTY,
    TECH_CATEGORIES, COMPLEXITY_LEVELS
)
from models.project import HackathonProject, ProjectScore


class ScoringEngine:
    """
    Core scoring engine for evaluating hackathon projects.
    
    This engine:
    - Scores projects across 7 weighted criteria
    - Detects and penalizes buzzword stuffing
    - Identifies vague descriptions
    - Catches overclaiming without evidence
    - Detects AI-generated content patterns
    - Adjusts expectations based on project complexity
    """
    
    def __init__(self):
        """Initialize the scoring engine with configuration."""
        self.criteria = SCORING_CRITERIA
        self.buzzwords = [b.lower() for b in BUZZWORDS]
        self.vague_phrases = [v.lower() for v in VAGUE_PHRASES]
        self.overclaim_phrases = [o.lower() for o in OVERCLAIM_PHRASES]
        self.ai_patterns = [a.lower() for a in AI_GENERATED_PATTERNS]
        self.tech_signals = [t.lower() for t in TECHNICAL_DEPTH_SIGNALS]
        self.feasibility_signals = [f.lower() for f in FEASIBILITY_SIGNALS]
        self.innovation_signals = [i.lower() for i in INNOVATION_SIGNALS]
    
    def evaluate_project(self, project: HackathonProject) -> ProjectScore:
        """
        Evaluate a hackathon project and return detailed scores.
        
        Args:
            project: The hackathon project to evaluate
            
        Returns:
            ProjectScore: Complete evaluation with scores, penalties, and feedback
        """
        # Get all text for analysis
        full_text = project.get_all_text().lower()
        word_count = project.get_word_count()
        
        # Determine project complexity level
        complexity_level = self._determine_complexity(project)
        
        # Score each criterion
        innovation_score, innovation_exp = self._score_innovation(project, full_text)
        technical_score, technical_exp = self._score_technical_depth(project, full_text)
        relevance_score, relevance_exp = self._score_problem_relevance(project, full_text)
        feasibility_score, feasibility_exp = self._score_feasibility(project, full_text)
        scalability_score, scalability_exp = self._score_scalability(project, full_text)
        ui_ux_score, ui_ux_exp = self._score_ui_ux(project, full_text)
        impact_score, impact_exp = self._score_real_world_impact(project, full_text)
        
        # Calculate penalties
        buzzword_penalty = self._calculate_buzzword_penalty(full_text, word_count)
        vagueness_penalty = self._calculate_vagueness_penalty(full_text)
        overclaim_penalty = self._calculate_overclaim_penalty(full_text)
        ai_penalty = self._calculate_ai_generated_penalty(full_text)
        
        total_penalty = min(30, buzzword_penalty + vagueness_penalty + overclaim_penalty + ai_penalty)
        
        # Calculate weighted raw score
        raw_score = (
            innovation_score * (self.criteria["innovation"]["weight"] / 100) +
            technical_score * (self.criteria["technical_depth"]["weight"] / 100) +
            relevance_score * (self.criteria["problem_relevance"]["weight"] / 100) +
            feasibility_score * (self.criteria["feasibility"]["weight"] / 100) +
            scalability_score * (self.criteria["scalability"]["weight"] / 100) +
            ui_ux_score * (self.criteria["ui_ux"]["weight"] / 100) +
            impact_score * (self.criteria["real_world_impact"]["weight"] / 100)
        )
        
        # Apply complexity multiplier and penalties
        complexity_multiplier = COMPLEXITY_LEVELS[complexity_level]["score_multiplier"]
        final_score = max(0, min(100, (raw_score * complexity_multiplier) - total_penalty))
        
        # Create and return the score object
        return ProjectScore(
            project_title=project.project_title,
            innovation_score=innovation_score,
            technical_depth_score=technical_score,
            problem_relevance_score=relevance_score,
            feasibility_score=feasibility_score,
            scalability_score=scalability_score,
            ui_ux_score=ui_ux_score,
            real_world_impact_score=impact_score,
            innovation_explanation=innovation_exp,
            technical_depth_explanation=technical_exp,
            problem_relevance_explanation=relevance_exp,
            feasibility_explanation=feasibility_exp,
            scalability_explanation=scalability_exp,
            ui_ux_explanation=ui_ux_exp,
            real_world_impact_explanation=impact_exp,
            buzzword_penalty=buzzword_penalty,
            vagueness_penalty=vagueness_penalty,
            overclaim_penalty=overclaim_penalty,
            ai_generated_penalty=ai_penalty,
            total_penalty=total_penalty,
            raw_score=round(raw_score, 1),
            final_score=round(final_score, 1)
        )
    
    def _determine_complexity(self, project: HackathonProject) -> str:
        """Determine the complexity level of a project based on team size and tech stack."""
        tech_count = len(project.tech_stack.split(','))
        
        if project.team_size <= 2 and tech_count <= 3:
            return "beginner"
        elif project.team_size >= 4 or tech_count >= 6:
            return "advanced"
        else:
            return "intermediate"
    
    def _score_innovation(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score the innovation and originality of the project.
        
        Looks for:
        - Novel approaches and unique combinations
        - Creative problem-solving
        - Fresh perspectives on existing problems
        """
        score = 50  # Base score
        reasons = []
        
        # Check for innovation signals
        innovation_count = sum(1 for signal in self.innovation_signals if signal in full_text)
        if innovation_count >= 3:
            score += 25
            reasons.append("Strong innovation signals detected")
        elif innovation_count >= 1:
            score += 15
            reasons.append("Some innovative elements present")
        
        # Check innovation description quality
        innovation_text = project.innovation_description.lower()
        if len(innovation_text.split()) >= 50:
            score += 10
            reasons.append("Detailed innovation explanation")
        
        # Check for specific differentiators
        differentiators = ["unlike", "different from", "improves", "addresses gap", "first to"]
        diff_count = sum(1 for d in differentiators if d in innovation_text)
        if diff_count >= 2:
            score += 10
            reasons.append("Clear differentiation from existing solutions")
        
        # Check for generic descriptions (penalty)
        generic_phrases = ["use ai", "machine learning solution", "web app", "mobile app"]
        generic_count = sum(1 for g in generic_phrases if g in innovation_text)
        if generic_count >= 2:
            score -= 15
            reasons.append("Innovation description is too generic")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Average innovation level"
        
        return score, explanation
    
    def _score_technical_depth(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score the technical sophistication of the project.
        
        Looks for:
        - Real engineering terminology
        - Specific technical decisions
        - Architecture considerations
        """
        score = 40  # Base score
        reasons = []
        
        # Count technical signals
        tech_signal_count = sum(1 for signal in self.tech_signals if signal in full_text)
        if tech_signal_count >= 10:
            score += 35
            reasons.append("Excellent technical depth with specific implementation details")
        elif tech_signal_count >= 5:
            score += 25
            reasons.append("Good technical vocabulary and understanding")
        elif tech_signal_count >= 2:
            score += 10
            reasons.append("Basic technical concepts mentioned")
        else:
            reasons.append("Lacks technical specificity")
        
        # Analyze tech stack
        tech_stack = project.tech_stack.lower()
        tech_categories_used = 0
        for category, techs in TECH_CATEGORIES.items():
            if any(tech in tech_stack for tech in techs):
                tech_categories_used += 1
        
        if tech_categories_used >= 4:
            score += 15
            reasons.append("Well-rounded tech stack covering multiple domains")
        elif tech_categories_used >= 2:
            score += 8
            reasons.append("Reasonable tech stack variety")
        
        # Check solution description for technical depth
        solution = project.solution_description.lower()
        if "architecture" in solution or "system design" in solution:
            score += 5
            reasons.append("Discusses system architecture")
        
        if "api" in solution or "database" in solution:
            score += 5
            reasons.append("Mentions data/API layer")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Limited technical depth"
        
        return score, explanation
    
    def _score_problem_relevance(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score how relevant and important the problem is.
        
        Looks for:
        - Clear problem definition
        - Evidence of real need
        - Specific target audience
        """
        score = 50  # Base score
        reasons = []
        
        problem = project.problem_statement.lower()
        target = project.target_users.lower()
        
        # Check problem statement quality
        if len(problem.split()) >= 75:
            score += 15
            reasons.append("Thorough problem description")
        elif len(problem.split()) >= 40:
            score += 8
            reasons.append("Adequate problem description")
        
        # Check for specific pain points
        pain_indicators = ["struggle", "challenge", "difficult", "problem", "issue", 
                          "pain point", "frustrat", "inefficient", "costly", "time-consuming"]
        pain_count = sum(1 for p in pain_indicators if p in problem)
        if pain_count >= 3:
            score += 15
            reasons.append("Clear articulation of pain points")
        elif pain_count >= 1:
            score += 8
            reasons.append("Some pain points identified")
        
        # Check target audience specificity
        specific_indicators = ["developer", "student", "enterprise", "small business", 
                               "healthcare", "education", "finance", "retail", "startup"]
        specific_count = sum(1 for s in specific_indicators if s in target)
        if specific_count >= 2:
            score += 10
            reasons.append("Well-defined target audience")
        elif specific_count >= 1:
            score += 5
            reasons.append("Target audience mentioned")
        
        # Check for data/statistics (adds credibility)
        if re.search(r'\d+%|\d+ million|\d+ billion|\d+ users', full_text):
            score += 10
            reasons.append("Includes supporting data/statistics")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Problem relevance unclear"
        
        return score, explanation
    
    def _score_feasibility(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score how feasible the project is to build and deploy.
        
        Looks for:
        - Working prototype/demo
        - Realistic scope
        - Practical implementation details
        """
        score = 45  # Base score
        reasons = []
        
        # Check for feasibility signals
        feasibility_count = sum(1 for signal in self.feasibility_signals if signal in full_text)
        if feasibility_count >= 5:
            score += 30
            reasons.append("Strong evidence of practical implementation")
        elif feasibility_count >= 2:
            score += 15
            reasons.append("Some practical considerations mentioned")
        
        # Check for demo link (big bonus)
        if project.demo_link:
            score += 20
            reasons.append("Working demo available")
        
        # Check for GitHub link quality hints
        github = project.github_link.lower()
        if "readme" in full_text or "documentation" in full_text:
            score += 5
            reasons.append("Documentation mentioned")
        
        # Check for realistic scope indicators
        solution = project.solution_description.lower()
        scope_indicators = ["mvp", "prototype", "phase 1", "initial version", "proof of concept"]
        if any(s in solution for s in scope_indicators):
            score += 10
            reasons.append("Realistic scope with phased approach")
        
        # Penalty for over-ambitious claims without evidence
        ambitious = ["entire industry", "all users", "everyone", "complete solution"]
        if any(a in solution for a in ambitious) and not project.demo_link:
            score -= 10
            reasons.append("Ambitious scope without demo evidence")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Feasibility not clearly demonstrated"
        
        return score, explanation
    
    def _score_scalability(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score the scalability potential of the project.
        
        Looks for:
        - Architecture for growth
        - Clear scaling strategy
        - Extensibility considerations
        """
        score = 45  # Base score
        reasons = []
        
        future = project.future_scope.lower()
        solution = project.solution_description.lower()
        combined = future + " " + solution
        
        # Check for scalability keywords
        scale_keywords = ["scale", "scalab", "microservice", "cloud", "distributed",
                         "horizontal", "vertical", "load balanc", "container", "kubernetes",
                         "elastic", "auto-scal", "serverless"]
        scale_count = sum(1 for k in scale_keywords if k in combined)
        
        if scale_count >= 4:
            score += 30
            reasons.append("Excellent scalability architecture")
        elif scale_count >= 2:
            score += 15
            reasons.append("Some scalability considerations")
        
        # Check for future scope quality
        if len(future.split()) >= 60:
            score += 10
            reasons.append("Detailed future roadmap")
        
        # Check for extensibility
        extend_keywords = ["plugin", "modular", "extensible", "api", "integration", "customize"]
        extend_count = sum(1 for e in extend_keywords if e in combined)
        if extend_count >= 2:
            score += 10
            reasons.append("Good extensibility considerations")
        
        # Check for monetization/sustainability
        sustain_keywords = ["revenue", "monetiz", "subscription", "freemium", "enterprise", "pricing"]
        if any(s in combined for s in sustain_keywords):
            score += 5
            reasons.append("Business sustainability considered")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Scalability plan not evident"
        
        return score, explanation
    
    def _score_ui_ux(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score the UI/UX and presentation quality.
        
        Looks for:
        - User-centric design mentions
        - Accessibility considerations
        - Polish and attention to detail
        """
        score = 50  # Base score
        reasons = []
        
        # Check for UI/UX keywords
        ux_keywords = ["user experience", "user interface", "ui", "ux", "design",
                      "intuitive", "user-friendly", "accessible", "responsive",
                      "figma", "mockup", "wireframe", "usability", "user testing",
                      "user research", "persona", "journey"]
        ux_count = sum(1 for k in ux_keywords if k in full_text)
        
        if ux_count >= 5:
            score += 25
            reasons.append("Strong UX focus with user-centric approach")
        elif ux_count >= 2:
            score += 12
            reasons.append("Some UX considerations mentioned")
        
        # Check for demo (visual evidence)
        if project.demo_link:
            score += 15
            reasons.append("Demo available for visual assessment")
        
        # Check for frontend technologies
        tech = project.tech_stack.lower()
        frontend_techs = ["react", "vue", "angular", "svelte", "tailwind", "css", "figma"]
        if any(f in tech for f in frontend_techs):
            score += 10
            reasons.append("Modern frontend technology stack")
        
        # Check for accessibility
        if "accessib" in full_text or "wcag" in full_text or "a11y" in full_text:
            score += 10
            reasons.append("Accessibility considered")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "UI/UX details not provided"
        
        return score, explanation
    
    def _score_real_world_impact(self, project: HackathonProject, full_text: str) -> Tuple[float, str]:
        """
        Score the potential real-world impact.
        
        Looks for:
        - Tangible benefits
        - Scale of impact
        - Social or economic value
        """
        score = 50  # Base score
        reasons = []
        
        # Check for impact keywords
        impact_keywords = ["impact", "benefit", "improve", "save time", "save money",
                          "reduce", "increase", "help", "solve", "address",
                          "community", "society", "environment", "sustainable"]
        impact_count = sum(1 for k in impact_keywords if k in full_text)
        
        if impact_count >= 6:
            score += 25
            reasons.append("Clear articulation of real-world benefits")
        elif impact_count >= 3:
            score += 12
            reasons.append("Some impact considerations")
        
        # Check for quantified impact
        if re.search(r'\d+%\s*(faster|better|cheaper|reduction|improvement)', full_text):
            score += 15
            reasons.append("Quantified impact metrics")
        
        # Check for specific beneficiaries
        target = project.target_users.lower()
        if len(target.split()) >= 30:
            score += 10
            reasons.append("Well-defined beneficiary group")
        
        score = max(0, min(100, score))
        explanation = "; ".join(reasons) if reasons else "Real-world impact not clearly defined"
        
        return score, explanation
    
    def _calculate_buzzword_penalty(self, text: str, word_count: int) -> float:
        """Calculate penalty for buzzword stuffing."""
        buzzword_count = sum(1 for bw in self.buzzwords if bw in text)
        
        # Calculate density (buzzwords per 100 words)
        density = (buzzword_count / max(1, word_count)) * 100
        
        if density > MAX_BUZZWORD_DENSITY:
            excess = density - MAX_BUZZWORD_DENSITY
            return min(15, excess * BUZZWORD_PENALTY)
        
        return 0.0
    
    def _calculate_vagueness_penalty(self, text: str) -> float:
        """Calculate penalty for vague descriptions."""
        vague_count = sum(1 for vp in self.vague_phrases if vp in text)
        
        if vague_count > 3:
            return min(10, (vague_count - 3) * VAGUENESS_PENALTY)
        
        return 0.0
    
    def _calculate_overclaim_penalty(self, text: str) -> float:
        """Calculate penalty for overclaiming without evidence."""
        overclaim_count = sum(1 for oc in self.overclaim_phrases if oc in text)
        
        if overclaim_count > 0:
            return min(15, overclaim_count * OVERCLAIM_PENALTY)
        
        return 0.0
    
    def _calculate_ai_generated_penalty(self, text: str) -> float:
        """Calculate penalty for suspected AI-generated content."""
        ai_pattern_count = sum(1 for ap in self.ai_patterns if ap in text)
        
        # High threshold - we don't want false positives
        if ai_pattern_count >= 5:
            return AI_GENERATED_PENALTY
        
        return 0.0
