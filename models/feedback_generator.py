"""
AI Hackathon Judge System - Feedback Generator

This module generates judge-style feedback including strengths, weaknesses,
improvement suggestions, and verdicts that sound like a real hackathon jury.
"""

import random
from typing import List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    SCORING_CRITERIA, VERDICT_THRESHOLDS, FEEDBACK_TEMPLATES
)
from models.project import HackathonProject, ProjectScore


class FeedbackGenerator:
    """
    Generates professional, judge-style feedback for hackathon projects.
    
    The feedback is:
    - Honest and direct
    - Specific and actionable
    - Professional but not robotic
    - Encouraging where warranted, critical where needed
    """
    
    def __init__(self):
        """Initialize the feedback generator."""
        self.criteria = SCORING_CRITERIA
        self.thresholds = VERDICT_THRESHOLDS
        self.templates = FEEDBACK_TEMPLATES
    
    def generate_feedback(self, project: HackathonProject, score: ProjectScore) -> ProjectScore:
        """
        Generate complete feedback for a scored project.
        
        Args:
            project: The original project submission
            score: The calculated scores
            
        Returns:
            ProjectScore: Updated with feedback, verdict, and explanations
        """
        # Generate strengths
        strengths = self._generate_strengths(project, score)
        
        # Generate weaknesses
        weaknesses = self._generate_weaknesses(project, score)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(project, score, weaknesses)
        
        # Determine verdict
        verdict, emoji, explanation = self._determine_verdict(score)
        
        # Update and return score object
        score.strengths = strengths
        score.weaknesses = weaknesses
        score.suggestions = suggestions
        score.verdict = verdict
        score.verdict_emoji = emoji
        score.verdict_explanation = explanation
        
        return score
    
    def _generate_strengths(self, project: HackathonProject, score: ProjectScore) -> List[str]:
        """Identify and articulate project strengths."""
        strengths = []
        
        # Check each criterion for high scores
        criteria_scores = [
            ("innovation", score.innovation_score, score.innovation_explanation),
            ("technical_depth", score.technical_depth_score, score.technical_depth_explanation),
            ("problem_relevance", score.problem_relevance_score, score.problem_relevance_explanation),
            ("feasibility", score.feasibility_score, score.feasibility_explanation),
            ("scalability", score.scalability_score, score.scalability_explanation),
            ("ui_ux", score.ui_ux_score, score.ui_ux_explanation),
            ("real_world_impact", score.real_world_impact_score, score.real_world_impact_explanation)
        ]
        
        # Sort by score descending
        criteria_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take top performers (score >= 70)
        for criterion, criterion_score, explanation in criteria_scores[:4]:
            if criterion_score >= 70:
                criterion_name = self.criteria[criterion]["name"]
                icon = self.criteria[criterion]["icon"]
                
                if criterion_score >= 85:
                    prefix = f"{icon} **Outstanding {criterion_name}**"
                else:
                    prefix = f"{icon} **Strong {criterion_name}**"
                
                strengths.append(f"{prefix}: {explanation}")
        
        # Add strength for demo if available
        if project.demo_link:
            strengths.append("🎬 **Working Demo Available**: Having a live demo significantly strengthens your submission.")
        
        # Add strength for low penalties
        if score.total_penalty == 0:
            strengths.append("✨ **Clean Submission**: No buzzword stuffing or vague claims detected. Clear, honest communication.")
        
        # Add strength for comprehensive submission
        if project.get_word_count() >= 400:
            strengths.append("📝 **Comprehensive Documentation**: Thorough explanation of the project across all sections.")
        
        # Ensure at least one strength
        if not strengths:
            # Find the best criterion
            best = criteria_scores[0]
            criterion_name = self.criteria[best[0]]["name"]
            strengths.append(f"📌 **{criterion_name}**: {best[2]}")
        
        return strengths[:5]  # Max 5 strengths
    
    def _generate_weaknesses(self, project: HackathonProject, score: ProjectScore) -> List[str]:
        """Identify and articulate project weaknesses."""
        weaknesses = []
        
        # Check each criterion for low scores
        criteria_scores = [
            ("innovation", score.innovation_score, score.innovation_explanation),
            ("technical_depth", score.technical_depth_score, score.technical_depth_explanation),
            ("problem_relevance", score.problem_relevance_score, score.problem_relevance_explanation),
            ("feasibility", score.feasibility_score, score.feasibility_explanation),
            ("scalability", score.scalability_score, score.scalability_explanation),
            ("ui_ux", score.ui_ux_score, score.ui_ux_explanation),
            ("real_world_impact", score.real_world_impact_score, score.real_world_impact_explanation)
        ]
        
        # Sort by score ascending (worst first)
        criteria_scores.sort(key=lambda x: x[1])
        
        # Take bottom performers (score < 60)
        for criterion, criterion_score, explanation in criteria_scores[:4]:
            if criterion_score < 60:
                criterion_name = self.criteria[criterion]["name"]
                icon = self.criteria[criterion]["icon"]
                
                if criterion_score < 40:
                    prefix = f"{icon} **Critical Gap in {criterion_name}**"
                else:
                    prefix = f"{icon} **Needs Work: {criterion_name}**"
                
                # Generate specific weakness feedback
                weakness_text = self._get_weakness_detail(criterion, criterion_score, explanation)
                weaknesses.append(f"{prefix}: {weakness_text}")
        
        # Add weakness for penalties
        if score.buzzword_penalty > 5:
            weaknesses.append("🚨 **Buzzword Overload**: Too many marketing terms without substance. Let your work speak for itself.")
        
        if score.vagueness_penalty > 3:
            weaknesses.append("😶‍🌫️ **Vague Descriptions**: Replace generic phrases with specific details about your implementation.")
        
        if score.overclaim_penalty > 5:
            weaknesses.append("⚠️ **Overclaiming**: Bold claims require bold evidence. Back up statements with data or demos.")
        
        if score.ai_generated_penalty > 0:
            weaknesses.append("🤖 **Generic Writing Style**: The submission reads like templated or AI-generated content. Add your authentic voice.")
        
        # Add weakness for no demo
        if not project.demo_link and score.final_score < 80:
            weaknesses.append("📵 **No Demo**: A working prototype would significantly strengthen this submission.")
        
        return weaknesses[:5]  # Max 5 weaknesses
    
    def _get_weakness_detail(self, criterion: str, score: float, explanation: str) -> str:
        """Generate specific weakness detail based on criterion."""
        details = {
            "innovation": [
                "The solution doesn't clearly differentiate from existing approaches.",
                "Consider what unique angle or approach you bring to this problem.",
                "Innovation should be evident in either the problem framing or solution design."
            ],
            "technical_depth": [
                "The technical implementation lacks specificity.",
                "Describe your architecture decisions, algorithms, or engineering challenges.",
                "Judges want to see real engineering effort, not just tool integration."
            ],
            "problem_relevance": [
                "The problem statement needs more clarity on who this affects and why.",
                "Quantify the problem: how many people? What's the cost? What's the pain?",
                "A compelling problem makes the solution compelling."
            ],
            "feasibility": [
                "It's unclear whether this can actually be built and deployed.",
                "What's your MVP? What's achievable in a realistic timeframe?",
                "Show us that you've thought through the practical implementation."
            ],
            "scalability": [
                "The scaling strategy is not evident.",
                "What happens when you have 10x, 100x, 1000x the users?",
                "Consider technical and business scalability."
            ],
            "ui_ux": [
                "User experience considerations are minimal.",
                "How will users actually interact with this? What's the user journey?",
                "Even technical products need good UX."
            ],
            "real_world_impact": [
                "The real-world impact is unclear.",
                "Who benefits and how? What changes because this exists?",
                "Connect your technical solution to tangible outcomes."
            ]
        }
        
        if explanation and len(explanation) > 20:
            return explanation
        
        return random.choice(details.get(criterion, ["Needs improvement in this area."]))
    
    def _generate_suggestions(self, project: HackathonProject, score: ProjectScore, 
                             weaknesses: List[str]) -> List[str]:
        """Generate actionable improvement suggestions."""
        suggestions = []
        
        # Suggestions based on score level
        if score.final_score < 50:
            suggestions.append("🎯 **Focus on One Thing**: Pick your strongest feature and polish it. A great MVP beats a mediocre complete product.")
            suggestions.append("🔨 **Build First, Describe Later**: Get a working prototype before spending time on elaborate descriptions.")
        
        elif score.final_score < 70:
            suggestions.append("📊 **Add Evidence**: Include metrics, user feedback, or comparison data to support your claims.")
            suggestions.append("🎥 **Record a Demo**: A 2-minute video walkthrough can dramatically improve your presentation.")
        
        else:
            suggestions.append("🚀 **Go Deep on Uniqueness**: Clearly articulate what makes this different from alternatives.")
            suggestions.append("📈 **Show Growth Potential**: How does this become a sustainable project or business?")
        
        # Specific suggestions based on missing elements
        if not project.demo_link:
            suggestions.append("🌐 **Deploy a Demo**: Even a basic Streamlit or Vercel deployment shows execution ability.")
        
        if score.innovation_score < 60:
            suggestions.append("💡 **Clarify Innovation**: What specific novel approach does this take? Compare directly to existing solutions.")
        
        if score.technical_depth_score < 60:
            suggestions.append("⚙️ **Technical Documentation**: Add architecture diagrams, API documentation, or code walkthroughs.")
        
        if score.problem_relevance_score < 60:
            suggestions.append("📋 **User Research**: Interview potential users. Real quotes and pain points are compelling.")
        
        if project.get_word_count() < 200:
            suggestions.append("📝 **Expand Details**: Add more context to your problem statement and solution description.")
        
        # Add general advice
        if score.final_score >= 70:
            suggestions.append("🏆 **Polish for Finals**: Small improvements in presentation and documentation could push this into winner territory.")
        
        return suggestions[:5]  # Max 5 suggestions
    
    def _determine_verdict(self, score: ProjectScore) -> Tuple[str, str, str]:
        """Determine the final verdict based on score."""
        final = score.final_score
        
        if final >= self.thresholds["winner"][0]:
            verdict = self.thresholds["winner"][2]
            emoji = self.thresholds["winner"][3]
            explanation = random.choice(self.templates["winner_verdict"])
        
        elif final >= self.thresholds["strong"][0]:
            verdict = self.thresholds["strong"][2]
            emoji = self.thresholds["strong"][3]
            explanation = random.choice(self.templates["strong_verdict"])
        
        elif final >= self.thresholds["average"][0]:
            verdict = self.thresholds["average"][2]
            emoji = self.thresholds["average"][3]
            explanation = random.choice(self.templates["average_verdict"])
        
        else:
            verdict = self.thresholds["not_ready"][2]
            emoji = self.thresholds["not_ready"][3]
            explanation = random.choice(self.templates["not_ready_verdict"])
        
        return verdict, emoji, explanation
    
    def generate_comparison_text(self, winner: ProjectScore, runner_up: ProjectScore) -> str:
        """
        Generate explanation for why one project beat another.
        
        Args:
            winner: The higher-scoring project
            runner_up: The second-place project
            
        Returns:
            str: Explanation of why the winner won
        """
        score_diff = winner.final_score - runner_up.final_score
        
        # Find biggest scoring differences
        criteria_diffs = [
            ("Innovation", winner.innovation_score - runner_up.innovation_score),
            ("Technical Depth", winner.technical_depth_score - runner_up.technical_depth_score),
            ("Problem Relevance", winner.problem_relevance_score - runner_up.problem_relevance_score),
            ("Feasibility", winner.feasibility_score - runner_up.feasibility_score),
            ("Scalability", winner.scalability_score - runner_up.scalability_score),
            ("UI/UX", winner.ui_ux_score - runner_up.ui_ux_score),
            ("Real-World Impact", winner.real_world_impact_score - runner_up.real_world_impact_score)
        ]
        
        # Sort by difference
        criteria_diffs.sort(key=lambda x: x[1], reverse=True)
        
        # Build explanation
        top_advantages = [c for c in criteria_diffs[:3] if c[1] > 5]
        
        if not top_advantages:
            return f"**{winner.project_title}** edges out with a {score_diff:.1f} point lead through consistent performance across all criteria."
        
        advantages_text = ", ".join([c[0] for c in top_advantages])
        
        if score_diff > 15:
            return f"**{winner.project_title}** takes the top spot with a commanding {score_diff:.1f} point lead, particularly excelling in {advantages_text}."
        elif score_diff > 5:
            return f"**{winner.project_title}** secures the win with a {score_diff:.1f} point advantage, driven by stronger {advantages_text}."
        else:
            return f"In a close race, **{winner.project_title}** wins by {score_diff:.1f} points with slight edges in {advantages_text}."


def format_score_report(project: HackathonProject, score: ProjectScore) -> str:
    """
    Format a complete score report as text.
    
    Args:
        project: The project submission
        score: The complete evaluation
        
    Returns:
        str: Formatted report
    """
    report = []
    report.append("=" * 60)
    report.append(f"📋 EVALUATION REPORT: {project.project_title}")
    report.append("=" * 60)
    report.append("")
    
    # Final Score
    report.append(f"🎯 FINAL SCORE: {score.final_score}/100")
    report.append(f"   {score.verdict_emoji} Verdict: {score.verdict}")
    report.append("")
    
    # Score Breakdown
    report.append("📊 CATEGORY SCORES:")
    report.append("-" * 40)
    
    criteria_list = [
        ("💡 Innovation", score.innovation_score, score.innovation_explanation),
        ("⚙️ Technical Depth", score.technical_depth_score, score.technical_depth_explanation),
        ("🎯 Problem Relevance", score.problem_relevance_score, score.problem_relevance_explanation),
        ("🔧 Feasibility", score.feasibility_score, score.feasibility_explanation),
        ("📈 Scalability", score.scalability_score, score.scalability_explanation),
        ("🎨 UI/UX", score.ui_ux_score, score.ui_ux_explanation),
        ("🌍 Real-World Impact", score.real_world_impact_score, score.real_world_impact_explanation)
    ]
    
    for name, criterion_score, explanation in criteria_list:
        report.append(f"   {name}: {criterion_score}/100")
        report.append(f"      └─ {explanation}")
    
    report.append("")
    
    # Penalties
    if score.total_penalty > 0:
        report.append("⚠️ PENALTIES APPLIED:")
        report.append("-" * 40)
        if score.buzzword_penalty > 0:
            report.append(f"   Buzzword stuffing: -{score.buzzword_penalty:.1f}")
        if score.vagueness_penalty > 0:
            report.append(f"   Vague descriptions: -{score.vagueness_penalty:.1f}")
        if score.overclaim_penalty > 0:
            report.append(f"   Overclaiming: -{score.overclaim_penalty:.1f}")
        if score.ai_generated_penalty > 0:
            report.append(f"   AI-generated patterns: -{score.ai_generated_penalty:.1f}")
        report.append(f"   Total penalty: -{score.total_penalty:.1f}")
        report.append("")
    
    # Strengths
    report.append("💪 STRENGTHS:")
    report.append("-" * 40)
    for strength in score.strengths:
        report.append(f"   • {strength}")
    report.append("")
    
    # Weaknesses
    report.append("📉 AREAS FOR IMPROVEMENT:")
    report.append("-" * 40)
    for weakness in score.weaknesses:
        report.append(f"   • {weakness}")
    report.append("")
    
    # Suggestions
    report.append("💡 RECOMMENDATIONS:")
    report.append("-" * 40)
    for suggestion in score.suggestions:
        report.append(f"   • {suggestion}")
    report.append("")
    
    # Verdict
    report.append("📜 JUDGE'S VERDICT:")
    report.append("-" * 40)
    report.append(f"   {score.verdict_explanation}")
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)
