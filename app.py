"""
AI Hackathon Judge System - Main Streamlit Application

A production-ready, AI-powered hackathon project evaluation system that
mimics real expert panel judging with NLP analysis, weighted scoring,
and brutally honest feedback.

Usage:
    streamlit run app.py
"""

import streamlit as st
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.project import HackathonProject, ProjectScore
from models.scoring_engine import ScoringEngine
from models.feedback_generator import FeedbackGenerator
from utils.validators import validate_project_data, get_field_help_text, get_field_placeholder
from utils.leaderboard import Leaderboard
from utils.nlp_analyzer import NLPAnalyzer
from config.settings import SCORING_CRITERIA, UI_CONFIG


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"]
)


# =============================================================================
# Load Custom CSS
# =============================================================================

def load_css():
    """Load custom CSS styles."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# =============================================================================
# Initialize Session State
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if "leaderboard" not in st.session_state:
        storage_path = Path(__file__).parent / "data" / "leaderboard.json"
        st.session_state.leaderboard = Leaderboard(str(storage_path))
    
    if "current_score" not in st.session_state:
        st.session_state.current_score = None
    
    if "current_project" not in st.session_state:
        st.session_state.current_project = None
    
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    
    if "show_sample" not in st.session_state:
        st.session_state.show_sample = False


# =============================================================================
# UI Components
# =============================================================================

def render_header():
    """Render the application header."""
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="margin: 0; font-size: 2.5rem;">
                🏆 AI Hackathon Judge
            </h1>
            <p style="color: #64748b; font-size: 1.1rem; margin-top: 8px;">
                Objective, AI-powered project evaluation with real hackathon judging criteria
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
        if st.button(f"{theme_icon} Theme", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()


def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        st.markdown("### 📋 Navigation")
        
        page = st.radio(
            "Go to",
            ["🎯 Submit Project", "📊 Leaderboard", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### ⚖️ Scoring Criteria")
        for key, criteria in SCORING_CRITERIA.items():
            st.markdown(f"{criteria['icon']} **{criteria['name']}**: {criteria['weight']}%")
        
        st.markdown("---")
        
        st.markdown("### 🎯 Verdicts")
        st.markdown("🏆 **Winner Material**: 85-100")
        st.markdown("✅ **Strong Contender**: 70-84")
        st.markdown("⚠️ **Average**: 50-69")
        st.markdown("❌ **Not Ready**: 0-49")
        
        st.markdown("---")
        
        st.markdown("### 📈 Stats")
        stats = st.session_state.leaderboard.get_statistics()
        st.metric("Total Projects", stats["total_projects"])
        if stats["total_projects"] > 0:
            st.metric("Average Score", f"{stats['average_score']:.1f}")
        
        return page


def render_input_form():
    """Render the project submission form."""
    st.markdown("### 📝 Submit Your Project")
    
    with st.form("project_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            project_title = st.text_input(
                "Project Title *",
                placeholder=get_field_placeholder("project_title"),
                help=get_field_help_text("project_title")
            )
        
        with col2:
            team_size = st.number_input(
                "Team Size *",
                min_value=1,
                max_value=10,
                value=3,
                help=get_field_help_text("team_size")
            )
        
        problem_statement = st.text_area(
            "Problem Statement *",
            placeholder=get_field_placeholder("problem_statement"),
            help=get_field_help_text("problem_statement"),
            height=120
        )
        
        solution_description = st.text_area(
            "Solution Description *",
            placeholder=get_field_placeholder("solution_description"),
            help=get_field_help_text("solution_description"),
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            tech_stack = st.text_input(
                "Tech Stack *",
                placeholder=get_field_placeholder("tech_stack"),
                help=get_field_help_text("tech_stack")
            )
        
        with col2:
            target_users = st.text_input(
                "Target Users / Industry *",
                placeholder=get_field_placeholder("target_users"),
                help=get_field_help_text("target_users")
            )
        
        innovation_description = st.text_area(
            "Innovation Description *",
            placeholder=get_field_placeholder("innovation_description"),
            help=get_field_help_text("innovation_description"),
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            github_link = st.text_input(
                "GitHub Repository Link *",
                placeholder=get_field_placeholder("github_link"),
                help=get_field_help_text("github_link")
            )
        
        with col2:
            demo_link = st.text_input(
                "Demo Link (Optional)",
                placeholder=get_field_placeholder("demo_link"),
                help=get_field_help_text("demo_link")
            )
        
        future_scope = st.text_area(
            "Future Scope / Scalability *",
            placeholder=get_field_placeholder("future_scope"),
            help=get_field_help_text("future_scope"),
            height=100
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submitted = st.form_submit_button(
                "🚀 Evaluate Project",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.form_submit_button("📋 Load Sample", use_container_width=True):
                st.session_state.show_sample = True
        
        with col3:
            if st.form_submit_button("🗑️ Clear", use_container_width=True):
                st.session_state.current_score = None
                st.session_state.current_project = None
    
    if submitted:
        # Validate and process submission
        form_data = {
            "project_title": project_title,
            "team_size": team_size,
            "problem_statement": problem_statement,
            "solution_description": solution_description,
            "tech_stack": tech_stack,
            "innovation_description": innovation_description,
            "github_link": github_link,
            "demo_link": demo_link,
            "target_users": target_users,
            "future_scope": future_scope
        }
        
        is_valid, errors, cleaned_data = validate_project_data(form_data)
        
        if not is_valid:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            with st.spinner("🔍 Analyzing project..."):
                try:
                    # Create project and evaluate
                    project = HackathonProject(**cleaned_data)
                    
                    # Score the project
                    scoring_engine = ScoringEngine()
                    score = scoring_engine.evaluate_project(project)
                    
                    # Generate feedback
                    feedback_gen = FeedbackGenerator()
                    score = feedback_gen.generate_feedback(project, score)
                    
                    # Add to leaderboard
                    rank = st.session_state.leaderboard.add_project(score)
                    
                    # Store in session
                    st.session_state.current_score = score
                    st.session_state.current_project = project
                    
                    st.success(f"✅ Project evaluated! Ranked #{rank} on the leaderboard.")
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error evaluating project: {str(e)}")


def render_score_display(score: ProjectScore):
    """Render the score display with visualizations."""
    st.markdown("---")
    st.markdown("## 📊 Evaluation Results")
    
    # Main score display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Score circle
        score_color = get_score_color(score.final_score)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 24px;">
            <div style="
                width: 180px;
                height: 180px;
                margin: 0 auto;
                border-radius: 50%;
                background: conic-gradient(
                    {score_color} {score.final_score * 3.6}deg,
                    #e2e8f0 {score.final_score * 3.6}deg
                );
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            ">
                <div style="
                    width: 150px;
                    height: 150px;
                    border-radius: 50%;
                    background: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <span style="font-size: 3rem; font-weight: 800; color: {score_color};">
                        {score.final_score:.0f}
                    </span>
                    <span style="font-size: 0.9rem; color: #64748b;">out of 100</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Verdict badge
        verdict_class = get_verdict_class(score.verdict)
        st.markdown(f"""
        <div style="text-align: center; margin-top: 16px;">
            <span class="verdict-badge {verdict_class}">
                {score.verdict_emoji} {score.verdict}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Category breakdown
    st.markdown("### 📈 Category Scores")
    
    criteria_data = [
        ("💡 Innovation", score.innovation_score, score.innovation_explanation, SCORING_CRITERIA["innovation"]["weight"]),
        ("⚙️ Technical Depth", score.technical_depth_score, score.technical_depth_explanation, SCORING_CRITERIA["technical_depth"]["weight"]),
        ("🎯 Problem Relevance", score.problem_relevance_score, score.problem_relevance_explanation, SCORING_CRITERIA["problem_relevance"]["weight"]),
        ("🔧 Feasibility", score.feasibility_score, score.feasibility_explanation, SCORING_CRITERIA["feasibility"]["weight"]),
        ("📈 Scalability", score.scalability_score, score.scalability_explanation, SCORING_CRITERIA["scalability"]["weight"]),
        ("🎨 UI/UX", score.ui_ux_score, score.ui_ux_explanation, SCORING_CRITERIA["ui_ux"]["weight"]),
        ("🌍 Real-World Impact", score.real_world_impact_score, score.real_world_impact_explanation, SCORING_CRITERIA["real_world_impact"]["weight"])
    ]
    
    for name, criterion_score, explanation, weight in criteria_data:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{name}** ({weight}%)")
            st.progress(criterion_score / 100)
            st.caption(explanation if explanation else "No specific feedback")
        
        with col2:
            score_color = get_score_color(criterion_score)
            st.markdown(f"""
            <div style="
                text-align: center;
                font-size: 1.5rem;
                font-weight: 700;
                color: {score_color};
                padding-top: 8px;
            ">{criterion_score:.0f}</div>
            """, unsafe_allow_html=True)
    
    # Penalties section
    if score.total_penalty > 0:
        st.markdown("### ⚠️ Penalties Applied")
        
        penalty_cols = st.columns(4)
        
        with penalty_cols[0]:
            if score.buzzword_penalty > 0:
                st.metric("Buzzwords", f"-{score.buzzword_penalty:.1f}")
        
        with penalty_cols[1]:
            if score.vagueness_penalty > 0:
                st.metric("Vagueness", f"-{score.vagueness_penalty:.1f}")
        
        with penalty_cols[2]:
            if score.overclaim_penalty > 0:
                st.metric("Overclaiming", f"-{score.overclaim_penalty:.1f}")
        
        with penalty_cols[3]:
            if score.ai_generated_penalty > 0:
                st.metric("AI-Generated", f"-{score.ai_generated_penalty:.1f}")
        
        st.info(f"📉 Total penalty: -{score.total_penalty:.1f} points")


def render_feedback(score: ProjectScore):
    """Render the detailed feedback sections."""
    st.markdown("---")
    st.markdown("## 📝 Detailed Feedback")
    
    # Strengths
    st.markdown("""
    <div class="feedback-section feedback-strengths">
        <h4 style="margin: 0 0 12px 0;">💪 Strengths</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for strength in score.strengths:
        st.markdown(f"• {strength}")
    
    st.markdown("")
    
    # Weaknesses
    st.markdown("""
    <div class="feedback-section feedback-weaknesses">
        <h4 style="margin: 0 0 12px 0;">📉 Areas for Improvement</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for weakness in score.weaknesses:
        st.markdown(f"• {weakness}")
    
    st.markdown("")
    
    # Suggestions
    st.markdown("""
    <div class="feedback-section feedback-suggestions">
        <h4 style="margin: 0 0 12px 0;">💡 Recommendations</h4>
    </div>
    """, unsafe_allow_html=True)
    
    for suggestion in score.suggestions:
        st.markdown(f"• {suggestion}")
    
    # Verdict explanation
    st.markdown("---")
    st.markdown("### 📜 Judge's Verdict")
    st.markdown(f"> {score.verdict_explanation}")


def render_leaderboard():
    """Render the leaderboard page."""
    st.markdown("## 📊 Leaderboard")
    
    rankings = st.session_state.leaderboard.get_rankings()
    
    if not rankings:
        st.info("🏁 No projects submitted yet. Be the first to submit!")
        return
    
    # Statistics
    stats = st.session_state.leaderboard.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", stats["total_projects"])
    
    with col2:
        st.metric("Average Score", f"{stats['average_score']:.1f}")
    
    with col3:
        st.metric("🏆 Winner Material", stats["winner_material_count"])
    
    with col4:
        st.metric("✅ Strong Contenders", stats["strong_contender_count"])
    
    st.markdown("---")
    
    # Winner explanation
    if len(rankings) >= 2:
        winner_explanation = st.session_state.leaderboard.explain_winner()
        st.markdown(winner_explanation)
        st.markdown("")
    
    # Leaderboard table
    for ranking in rankings:
        rank = ranking["rank"]
        
        # Determine styling
        if rank == 1:
            medal = "🥇"
            bg_color = "rgba(251, 191, 36, 0.1)"
            border_color = "#fbbf24"
        elif rank == 2:
            medal = "🥈"
            bg_color = "rgba(156, 163, 175, 0.1)"
            border_color = "#9ca3af"
        elif rank == 3:
            medal = "🥉"
            bg_color = "rgba(180, 83, 9, 0.1)"
            border_color = "#b45309"
        else:
            medal = f"#{rank}"
            bg_color = "transparent"
            border_color = "#e2e8f0"
        
        score_color = get_score_color(ranking["final_score"])
        
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 16px;
            background: {bg_color};
            border: 1px solid {border_color};
            border-radius: 12px;
            margin-bottom: 8px;
        ">
            <div style="font-size: 1.5rem; width: 50px; text-align: center;">{medal}</div>
            <div style="flex: 1; margin-left: 12px;">
                <div style="font-weight: 600; font-size: 1.1rem;">{ranking["project_title"]}</div>
                <div style="color: #64748b; font-size: 0.9rem;">{ranking["verdict_emoji"]} {ranking["verdict"]}</div>
            </div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {score_color};
            ">{ranking["final_score"]:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Clear leaderboard option
    st.markdown("---")
    if st.button("🗑️ Clear Leaderboard", type="secondary"):
        st.session_state.leaderboard.clear()
        st.success("Leaderboard cleared!")
        st.rerun()


def render_about():
    """Render the about page."""
    st.markdown("## ℹ️ About AI Hackathon Judge")
    
    st.markdown("""
    ### 🎯 What is this?
    
    AI Hackathon Judge is a production-ready, AI-powered system that evaluates 
    hackathon projects like a real expert panel. It provides objective scoring,
    detailed feedback, and rankings based on industry-standard judging criteria.
    
    ### ⚖️ How Scoring Works
    
    Projects are evaluated across **7 weighted criteria**:
    
    | Criteria | Weight | Description |
    |----------|--------|-------------|
    | 💡 Innovation & Originality | 25% | Uniqueness and creativity of the solution |
    | ⚙️ Technical Depth | 20% | Sophistication of implementation |
    | 🎯 Problem Relevance | 15% | Importance of the problem being solved |
    | 🔧 Feasibility | 15% | Practicality and achievability |
    | 📈 Scalability | 10% | Growth potential and extensibility |
    | 🎨 UI/UX & Presentation | 10% | Design and user experience quality |
    | 🌍 Real-World Impact | 5% | Tangible benefits to users/society |
    
    ### 🔍 Detection Systems
    
    The judge also detects and penalizes:
    
    - **Buzzword Stuffing**: Overuse of marketing terms without substance
    - **Vague Descriptions**: Non-specific or generic explanations
    - **Overclaiming**: Bold claims without supporting evidence
    - **AI-Generated Content**: Template or formulaic writing patterns
    
    ### 🏆 Verdict Levels
    
    - **🏆 Winner Material (85-100)**: Exceptional work ready to compete
    - **✅ Strong Contender (70-84)**: Solid project with minor improvements needed
    - **⚠️ Average (50-69)**: Has potential but needs significant work
    - **❌ Not Ready (0-49)**: Requires fundamental rethinking
    
    ### 💻 Built With
    
    - Python 3.10+
    - Streamlit
    - Pydantic
    - NLP (TF-IDF-based analysis)
    - Custom scoring algorithms
    
    ---
    
    Made with ❤️ for hackathon participants and organizers everywhere.
    """)


# =============================================================================
# Helper Functions
# =============================================================================

def get_score_color(score: float) -> str:
    """Get color based on score value."""
    if score >= 85:
        return "#10b981"  # Green
    elif score >= 70:
        return "#22c55e"  # Light green
    elif score >= 50:
        return "#f59e0b"  # Orange
    else:
        return "#ef4444"  # Red


def get_verdict_class(verdict: str) -> str:
    """Get CSS class based on verdict."""
    if "Winner" in verdict:
        return "verdict-winner"
    elif "Strong" in verdict:
        return "verdict-strong"
    elif "Average" in verdict:
        return "verdict-average"
    else:
        return "verdict-not-ready"


def load_sample_projects():
    """Load sample projects from JSON file."""
    sample_path = Path(__file__).parent / "data" / "sample_projects.json"
    if sample_path.exists():
        with open(sample_path) as f:
            return json.load(f)
    return []


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Initialize
    load_css()
    init_session_state()
    
    # Apply theme
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .stApp { background-color: #0f172a; color: #f8fafc; }
            .stMarkdown { color: #f8fafc; }
        </style>
        """, unsafe_allow_html=True)
    
    # Render header
    render_header()
    
    # Render sidebar and get current page
    page = render_sidebar()
    
    # Render main content based on page
    if "Submit" in page:
        render_input_form()
        
        # Show results if available
        if st.session_state.current_score:
            render_score_display(st.session_state.current_score)
            render_feedback(st.session_state.current_score)
    
    elif "Leaderboard" in page:
        render_leaderboard()
    
    elif "About" in page:
        render_about()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem;">
        🏆 AI Hackathon Judge | Built for objective, fair hackathon evaluation
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
