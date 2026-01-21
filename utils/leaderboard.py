"""
AI Hackathon Judge System - Leaderboard

This module provides project ranking, comparison, and leaderboard
functionality for evaluating multiple hackathon submissions.
"""

import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.project import ProjectScore


class Leaderboard:
    """
    Leaderboard system for ranking hackathon projects.
    
    Features:
    - Automatic ranking by score
    - Top 3 highlighting
    - Winner explanation
    - Score comparison
    - Persistence to JSON
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the leaderboard.
        
        Args:
            storage_path: Optional path to JSON file for persistence
        """
        self.projects: List[Dict] = []
        self.storage_path = storage_path
        
        if storage_path and os.path.exists(storage_path):
            self._load()
    
    def add_project(self, score: ProjectScore) -> int:
        """
        Add a scored project to the leaderboard.
        
        Args:
            score: The project's evaluation score
            
        Returns:
            int: The project's rank (1-indexed)
        """
        project_data = {
            "project_title": score.project_title,
            "final_score": score.final_score,
            "raw_score": score.raw_score,
            "innovation_score": score.innovation_score,
            "technical_depth_score": score.technical_depth_score,
            "problem_relevance_score": score.problem_relevance_score,
            "feasibility_score": score.feasibility_score,
            "scalability_score": score.scalability_score,
            "ui_ux_score": score.ui_ux_score,
            "real_world_impact_score": score.real_world_impact_score,
            "total_penalty": score.total_penalty,
            "verdict": score.verdict,
            "verdict_emoji": score.verdict_emoji,
            "submitted_at": datetime.now().isoformat()
        }
        
        self.projects.append(project_data)
        self._sort()
        
        if self.storage_path:
            self._save()
        
        # Find and return rank
        for i, p in enumerate(self.projects):
            if p["project_title"] == score.project_title:
                return i + 1
        
        return len(self.projects)
    
    def get_rankings(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get ranked list of projects.
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List of project data with ranks
        """
        self._sort()
        
        rankings = []
        for i, project in enumerate(self.projects[:limit] if limit else self.projects):
            project_with_rank = project.copy()
            project_with_rank["rank"] = i + 1
            project_with_rank["is_top_3"] = i < 3
            rankings.append(project_with_rank)
        
        return rankings
    
    def get_top_3(self) -> List[Dict]:
        """Get the top 3 projects."""
        return self.get_rankings(limit=3)
    
    def get_winner(self) -> Optional[Dict]:
        """Get the winning project."""
        rankings = self.get_rankings(limit=1)
        return rankings[0] if rankings else None
    
    def get_project_rank(self, project_title: str) -> Optional[int]:
        """
        Get the rank of a specific project.
        
        Args:
            project_title: The project's title
            
        Returns:
            The rank (1-indexed) or None if not found
        """
        self._sort()
        
        for i, project in enumerate(self.projects):
            if project["project_title"].lower() == project_title.lower():
                return i + 1
        
        return None
    
    def explain_winner(self) -> str:
        """
        Generate an explanation for why #1 won.
        
        Returns:
            String explanation of the winner's victory
        """
        if len(self.projects) < 1:
            return "No projects submitted yet."
        
        winner = self.projects[0]
        
        if len(self.projects) == 1:
            return f"**{winner['project_title']}** is the only submission with a score of {winner['final_score']}/100 ({winner['verdict']})."
        
        runner_up = self.projects[1]
        score_diff = winner["final_score"] - runner_up["final_score"]
        
        # Find where winner excels
        criteria = [
            ("Innovation", winner["innovation_score"], runner_up["innovation_score"]),
            ("Technical Depth", winner["technical_depth_score"], runner_up["technical_depth_score"]),
            ("Problem Relevance", winner["problem_relevance_score"], runner_up["problem_relevance_score"]),
            ("Feasibility", winner["feasibility_score"], runner_up["feasibility_score"]),
            ("Scalability", winner["scalability_score"], runner_up["scalability_score"]),
            ("UI/UX", winner["ui_ux_score"], runner_up["ui_ux_score"]),
            ("Real-World Impact", winner["real_world_impact_score"], runner_up["real_world_impact_score"])
        ]
        
        advantages = [(name, w - r) for name, w, r in criteria if w > r]
        advantages.sort(key=lambda x: x[1], reverse=True)
        
        if score_diff >= 20:
            intensity = "dominating"
        elif score_diff >= 10:
            intensity = "convincing"
        elif score_diff >= 5:
            intensity = "solid"
        else:
            intensity = "narrow"
        
        explanation = f"🏆 **{winner['project_title']}** takes the top spot with a {intensity} {score_diff:.1f}-point lead over {runner_up['project_title']}."
        
        if advantages:
            top_advantages = [a[0] for a in advantages[:3]]
            explanation += f" Key advantages: strong performance in {', '.join(top_advantages)}."
        
        if winner["total_penalty"] < runner_up["total_penalty"]:
            explanation += " The winner also had fewer deductions for buzzwords or vague claims."
        
        return explanation
    
    def get_comparison(self, project1_title: str, project2_title: str) -> Dict:
        """
        Compare two projects head-to-head.
        
        Args:
            project1_title: First project's title
            project2_title: Second project's title
            
        Returns:
            Comparison data dictionary
        """
        project1 = None
        project2 = None
        
        for p in self.projects:
            if p["project_title"].lower() == project1_title.lower():
                project1 = p
            if p["project_title"].lower() == project2_title.lower():
                project2 = p
        
        if not project1 or not project2:
            return {"error": "One or both projects not found"}
        
        criteria = [
            "innovation_score", "technical_depth_score", "problem_relevance_score",
            "feasibility_score", "scalability_score", "ui_ux_score", "real_world_impact_score"
        ]
        
        comparison = {
            "project1": project1["project_title"],
            "project2": project2["project_title"],
            "score_difference": project1["final_score"] - project2["final_score"],
            "winner": project1["project_title"] if project1["final_score"] > project2["final_score"] 
                      else project2["project_title"] if project2["final_score"] > project1["final_score"]
                      else "Tie",
            "criteria_comparison": {}
        }
        
        for criterion in criteria:
            criterion_name = criterion.replace("_score", "").replace("_", " ").title()
            comparison["criteria_comparison"][criterion_name] = {
                "project1": project1[criterion],
                "project2": project2[criterion],
                "difference": project1[criterion] - project2[criterion]
            }
        
        return comparison
    
    def get_statistics(self) -> Dict:
        """
        Get overall leaderboard statistics.
        
        Returns:
            Dictionary of statistics
        """
        if not self.projects:
            return {
                "total_projects": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "score_range": 0
            }
        
        scores = [p["final_score"] for p in self.projects]
        
        return {
            "total_projects": len(self.projects),
            "average_score": round(sum(scores) / len(scores), 1),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "score_range": max(scores) - min(scores),
            "winner_material_count": sum(1 for p in self.projects if p["final_score"] >= 85),
            "strong_contender_count": sum(1 for p in self.projects if 70 <= p["final_score"] < 85),
            "average_count": sum(1 for p in self.projects if 50 <= p["final_score"] < 70),
            "not_ready_count": sum(1 for p in self.projects if p["final_score"] < 50)
        }
    
    def clear(self):
        """Clear all projects from the leaderboard."""
        self.projects = []
        if self.storage_path:
            self._save()
    
    def remove_project(self, project_title: str) -> bool:
        """
        Remove a project from the leaderboard.
        
        Args:
            project_title: Title of the project to remove
            
        Returns:
            True if removed, False if not found
        """
        for i, p in enumerate(self.projects):
            if p["project_title"].lower() == project_title.lower():
                self.projects.pop(i)
                if self.storage_path:
                    self._save()
                return True
        
        return False
    
    def _sort(self):
        """Sort projects by final score (descending), then by raw score for ties."""
        self.projects.sort(
            key=lambda x: (x["final_score"], x["raw_score"]),
            reverse=True
        )
    
    def _save(self):
        """Save leaderboard to JSON file."""
        if not self.storage_path:
            return
        
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        with open(self.storage_path, 'w') as f:
            json.dump(self.projects, f, indent=2)
    
    def _load(self):
        """Load leaderboard from JSON file."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                self.projects = json.load(f)
            self._sort()
        except (json.JSONDecodeError, IOError):
            self.projects = []


def format_leaderboard_table(rankings: List[Dict]) -> str:
    """
    Format leaderboard as a text table.
    
    Args:
        rankings: List of ranked projects
        
    Returns:
        Formatted table string
    """
    if not rankings:
        return "No projects submitted yet."
    
    lines = []
    lines.append("┌" + "─" * 6 + "┬" + "─" * 40 + "┬" + "─" * 8 + "┬" + "─" * 18 + "┐")
    lines.append("│ Rank │ Project" + " " * 32 + "│ Score  │ Verdict          │")
    lines.append("├" + "─" * 6 + "┼" + "─" * 40 + "┼" + "─" * 8 + "┼" + "─" * 18 + "┤")
    
    for r in rankings:
        rank_str = f"{r['rank']:^6}"
        title = r["project_title"][:38].ljust(40)
        score = f"{r['final_score']:>6.1f} "
        verdict = f"{r['verdict_emoji']} {r['verdict'][:13]:<13}"
        
        if r["is_top_3"]:
            medal = ["🥇", "🥈", "🥉"][r["rank"] - 1]
            rank_str = f"  {medal}   "
        
        lines.append(f"│{rank_str}│ {title}│{score}│ {verdict}│")
    
    lines.append("└" + "─" * 6 + "┴" + "─" * 40 + "┴" + "─" * 8 + "┴" + "─" * 18 + "┘")
    
    return "\n".join(lines)
