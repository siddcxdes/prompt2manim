"""
server.py - FastAPI backend for Prompt2Manim
Run with: uvicorn server:app --reload
"""

import os
import json
import uuid
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from llm.planner import get_plan_from_user
from validation.validate import validate_plan, get_validation_report
from validation.normalize import normalize_plan
from renderer.actions import ActionFactory, actions_summary

# load .env file
load_dotenv()

# create the app
app = FastAPI()

# folder where we keep rendered videos
VIDEOS_FOLDER = Path("rendered_videos")
VIDEOS_FOLDER.mkdir(exist_ok=True)

# serve the frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# --- request/response models ---

class GenerateRequest(BaseModel):
    prompt: str

class RenderRequest(BaseModel):
    plan: dict
    quality: str = "medium"


# --- routes ---

@app.get("/")
def home():
    """Serve the main page."""
    return FileResponse("frontend/index.html")


@app.post("/api/generate")
def generate_plan(request: GenerateRequest):
    """
    Take the user's prompt, send it to AI, and return an animation plan.
    """
    prompt = request.prompt.strip()

    if prompt == "":
        return JSONResponse(
            status_code=400,
            content={"error": "Please enter a prompt."}
        )

    # step 1: get plan from AI
    plan, error = get_plan_from_user(prompt)

    if plan is None:
        return JSONResponse(
            status_code=500,
            content={"error": error or "Failed to generate plan."}
        )

    # step 2: validate the plan
    is_valid = validate_plan(plan)

    if not is_valid:
        report = get_validation_report(plan)
        return JSONResponse(
            status_code=500,
            content={"error": "AI produced an invalid plan. Please try again.",
                      "details": report.get("issues", [])}
        )

    # step 3: normalize (clean up) the plan
    clean_plan = normalize_plan(plan)

    if clean_plan is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Could not process the plan. Please try again."}
        )

    # step 4: create actions and get summary
    actions = ActionFactory.create_all(clean_plan)
    summary = actions_summary(actions)

    # return everything to the frontend
    return {
        "plan": clean_plan,
        "summary": {
            "total_steps": summary["total_actions"],
            "total_duration": summary["total_duration"],
            "types": summary["action_types"],
        }
    }


@app.post("/api/render")
def render_video(request: RenderRequest):
    """
    Take a plan and render it into a video using Manim.
    """
    plan = request.plan
    quality = request.quality

    # pick the right manim quality flag
    quality_flags = {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
    }
    flag = quality_flags.get(quality, "-qm")

    # create a unique id for this render
    render_id = str(uuid.uuid4())[:8]
    scene_file = Path("temp_scene_" + render_id + ".py")

    # write the scene file
    scene_code = '''
from manim import *
from renderer.actions import ActionFactory
from renderer.executor import execute_actions
import json

class RenderScene(Scene):
    def construct(self):
        plan = json.loads("""''' + json.dumps(plan) + '''""")
        actions = ActionFactory.create_all(plan)
        execute_actions(self, actions)
'''

    scene_file.write_text(scene_code)

    try:
        # run manim to render the video
        cmd = [
            "manim", flag,
            str(scene_file), "RenderScene",
            "--format=mp4",
            "--media_dir", str(VIDEOS_FOLDER / render_id),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            error_msg = result.stderr
            # get the last few lines of the error
            lines = error_msg.strip().split("\n")
            short_error = "\n".join(lines[-5:]) if len(lines) > 5 else error_msg
            return JSONResponse(
                status_code=500,
                content={"error": "Manim rendering failed.", "details": short_error}
            )

        # find the output video file
        media_dir = VIDEOS_FOLDER / render_id
        video_files = list(media_dir.rglob("*.mp4"))

        if len(video_files) == 0:
            return JSONResponse(
                status_code=500,
                content={"error": "Rendering completed but no video file was found."}
            )

        # get the newest video file
        video_path = max(video_files, key=lambda f: f.stat().st_mtime)

        return {
            "video_url": "/api/video/" + render_id + "/" + video_path.name,
            "render_id": render_id,
        }

    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=500,
            content={"error": "Rendering took too long (over 5 minutes)."}
        )
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"error": "Rendering failed: " + str(error)}
        )
    finally:
        # clean up the temp file
        if scene_file.exists():
            scene_file.unlink()


@app.get("/api/video/{render_id}/{filename}")
def serve_video(render_id: str, filename: str):
    """Serve a rendered video file."""
    media_dir = VIDEOS_FOLDER / render_id
    video_files = list(media_dir.rglob(filename))

    if len(video_files) == 0:
        return JSONResponse(status_code=404, content={"error": "Video not found."})

    return FileResponse(
        str(video_files[0]),
        media_type="video/mp4",
        filename=filename,
    )
