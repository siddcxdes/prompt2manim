"""
Streamlit frontend for Prompt2Manim - Animation Generator
Run with: streamlit run app.py
"""

import streamlit as st
import json
import os
import subprocess
import tempfile
from pathlib import Path

from llm.planner import get_plan_from_user
from validation.validate import validate_plan, get_validation_report
from validation.normalize import normalize_plan
from renderer.actions import ActionFactory, actions_summary
from scenes.generated_scene import apply_scene_config

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


# Page configuration
st.set_page_config(
    page_title="Prompt2Manim",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Global Theme */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Default Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hero Section */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #A0AEC0;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Card Styles */
    .css-1r6slb0 {  /* Streamlit container class */
        border: 1px solid #2D3748;
        border-radius: 16px;
        padding: 1.5rem;
        background-color: #1A202C;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Preview Step Cards */
    .step-card {
        background: rgba(26, 32, 44, 0.8);
        -webkit-backdrop-filter: blur(10px);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .step-card:hover {
        transform: translateY(-2px);
        border-color: #764ba2;
    }
    
    .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .step-type {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }
    
    /* Type Colors */
    .type-text { background-color: rgba(66, 153, 225, 0.2); color: #63B3ED; }
    .type-equation { background-color: rgba(236, 201, 75, 0.2); color: #F6E05E; }
    .type-graph { background-color: rgba(72, 187, 120, 0.2); color: #68D391; }
    .type-shape { background-color: rgba(237, 100, 166, 0.2); color: #F687B3; }
    .type-animation { background-color: rgba(159, 122, 234, 0.2); color: #B794F4; }
    .type-wait { background-color: rgba(113, 128, 150, 0.2); color: #CBD5E0; }
    
    .step-content {
        font-size: 1rem;
        color: #E2E8F0;
        font-weight: 400;
        line-height: 1.5;
    }
    
    .step-duration {
        font-size: 0.8rem;
        color: #718096;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    /* Stats Row */
    .stats-container {
        display: flex;
        justify-content: space-between;
        background: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        border-radius: 12px;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FAFAFA;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Custom Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Primary Button Gradient */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 14px 0 rgba(118, 75, 162, 0.39);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(118, 75, 162, 0.5);
    }
    
    /* Text Area Styling */
    .stTextArea > div > div > textarea {
        background-color: #1A202C !important;
        color: #FAFAFA !important;
        border: 1px solid #2D3748 !important;
        border-radius: 12px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }

</style>
""", unsafe_allow_html=True)


def init_session_state():
    if "plan" not in st.session_state:
        st.session_state.plan = None
    if "clean_plan" not in st.session_state:
        st.session_state.clean_plan = None
    if "actions" not in st.session_state:
        st.session_state.actions = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "prompt_value" not in st.session_state:
        st.session_state.prompt_value = ""


def display_step(step, index):
    step_type = step.get("type", "unknown").lower()
    content = step.get("content", "")
    duration = step.get("duration", 1)
    
    # CSS class for dynamic coloring
    type_class = f"type-{step_type}"
    
    html = f"""
    <div class="step-card">
        <div class="step-header">
            <span class="step-type {type_class}">{step_type}</span>
            <span class="step-duration">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {duration}s
            </span>
        </div>
        <div class="step-content">{content}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def display_plan_preview(plan):
    steps = plan.get("steps", [])
    
    st.markdown("#### 📋 Animation Steps")
    
    # Scrollable container for steps
    with st.container():
        for i, step in enumerate(steps):
            display_step(step, i)


def display_stats(actions):
    summary = actions_summary(actions)
    
    html = f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-value">{summary['total_actions']}</div>
            <div class="stat-label">Steps</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{summary['total_duration']:.1f}s</div>
            <div class="stat-label">Duration</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{len(summary['action_types'])}</div>
            <div class="stat-label">Types</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def generate_plan(prompt):
    return get_plan_from_user(prompt)


def validate_and_normalize(plan):
    is_valid = validate_plan(plan)
    if not is_valid:
        return None
    
    clean_plan = normalize_plan(plan)
    return clean_plan


def create_actions(plan):
    try:
        actions = ActionFactory.create_all(plan)
        return actions
    except Exception as e:
        st.error(f"Error creating actions: {e}")
        return None


def render_animation(plan, quality):
    quality_flags = {
        "fast": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "4k": "-qk"
    }
    
    flag = quality_flags.get(quality, "-qm")
    
    scene_code = f'''
from manim import *
from renderer.actions import ActionFactory, GraphAction
from renderer.executor import execute_actions

class StreamlitScene(Scene):
    def construct(self):
        plan = {json.dumps(plan)}
        actions = ActionFactory.create_all(plan)
        execute_actions(self, actions)
'''
    
    temp_path = Path("temp_scene.py")
    temp_path.write_text(scene_code)
    
    try:
        # Use simple environment where possible, or ensure manim is in path
        cmd = ["manim", flag, str(temp_path), "StreamlitScene", "--format=mp4"]
        
        # Create progress placeholder
        progress_text = "Rendering animation... This might take a moment."
        my_bar = st.progress(0, text=progress_text)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        my_bar.progress(100, text="Rendering complete!")
        
        if result.returncode == 0:
            # Locate the output file
            # Manim output structure: media/videos/temp_scene/quality/StreamlitScene.mp4
            quality_dir_map = {
                "fast": "480p15",
                "medium": "720p30",
                "high": "1080p60", 
                "4k": "2160p30"
            }
            # Note: actual dir name depends on manim version and config, strictly searching is safer
            media_dir = Path("media/videos/temp_scene")
            
            if media_dir.exists():
                videos = list(media_dir.rglob("*.mp4"))
                if videos:
                    return str(max(videos, key=lambda p: p.stat().st_mtime))
        else:
             st.error(f"Manim Error: {result.stderr}")
             
        return None
    except Exception as e:
        st.error(f"Render Execution Error: {e}")
        return None
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main():
    init_session_state()
    
    # Hero Section
    st.markdown('<div class="hero-title">Prompt2Manim</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Transform your ideas into beautiful math animations</div>', unsafe_allow_html=True)
    
    # Main Layout
    col1, spacing, col2 = st.columns([1, 0.1, 1])
    
    with col1:
        st.markdown("### 🎨 Create")
        
        with st.container():
            prompt = st.text_area(
                "What would you like to animate?",
                value=st.session_state.prompt_value,
                placeholder="e.g., Show a sine wave transforming into a cosine wave...",
                height=150,
                label_visibility="collapsed"
            )
            
            # Quick Actions
            st.markdown("###### Try these:")
            q1, q2, q3 = st.columns(3)
            if q1.button("Quadratic Eq", use_container_width=True):
                st.session_state.prompt_value = "Show the quadratic formula with an example"
                st.rerun()
            if q2.button("Sine Wave", use_container_width=True):
                st.session_state.prompt_value = "Show a sine wave graph"
                st.rerun()
            if q3.button("Pythagoras", use_container_width=True):
                st.session_state.prompt_value = "Visualize the Pythagorean theorem"
                st.rerun()
                
            st.divider()
            
            # Settings
            s1, s2 = st.columns([2, 1])
            with s1:
                quality = st.select_slider(
                    "Render Quality",
                    options=["fast", "medium", "high", "4k"],
                    value="medium"
                )
            
            st.markdown("") # Spacer
            
            generate_btn = st.button("✨ Generate Animation", type="primary", use_container_width=True)
            
            if generate_btn and prompt:
                # Reset previous state
                st.session_state.plan = None
                st.session_state.actions = None
                st.session_state.video_path = None
                
                with st.spinner("🤖 Dreaming up animation steps..."):
                    plan = generate_plan(prompt)
                    if plan:
                        st.session_state.plan = plan
                        clean_plan = validate_and_normalize(plan)
                        if clean_plan:
                            st.session_state.clean_plan = clean_plan
                            actions = create_actions(clean_plan)
                            if actions:
                                st.session_state.actions = actions
                st.rerun()

    with col2:
        st.markdown("### 👁️ Preview")
        
        if st.session_state.plan:
            # Stats Summary
            if st.session_state.actions:
                display_stats(st.session_state.actions)
            
            # Use tabs for Plan vs Video choice
            tab1, tab2 = st.tabs(["📝 Steps", "🎥 Video"])
            
            with tab1:
                plan_to_show = st.session_state.clean_plan or st.session_state.plan
                display_plan_preview(plan_to_show)
                
                st.divider()
                if st.button("🎬 Render Now", type="primary", use_container_width=True):
                    with st.spinner(f"Rendering in {quality} quality..."):
                        video_path = render_animation(st.session_state.clean_plan, quality)
                        if video_path:
                            st.session_state.video_path = video_path
                    st.rerun()

            with tab2:
                if st.session_state.video_path:
                    video_file = Path(st.session_state.video_path)
                    if video_file.exists():
                        st.video(str(video_file))
                        
                        with open(video_file, "rb") as f:
                            st.download_button(
                                "⬇️ Download MP4",
                                f,
                                file_name=f"p2m_{video_file.stem}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                else:
                    st.info("Render the animation to see the video here!")
                    
        else:
            # Empty state
            st.markdown("""
            <div style="text-align: center; padding: 4rem 2rem; border: 2px dashed #2D3748; border-radius: 12px; opacity: 0.5;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎨</div>
                <h3>Ready to Create</h3>
                <p>Enter a prompt on the left to see your animation plan here.</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
