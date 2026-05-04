"""
Normalize - cleans up the plan from the AI.
"""


def normalize_plan(plan):
    if not plan:
        return None

    clean_plan = {"steps": []}
    steps = plan.get("steps", [])

    for i in range(len(steps)):
        clean_step = normalize_step(steps[i])
        if clean_step is not None:
            clean_plan["steps"].append(clean_step)

    if len(clean_plan["steps"]) == 0:
        return None

    return clean_plan


def normalize_step(step):
    if not step:
        return None

    clean_type = normalize_type(step.get("type", "text"))
    if clean_type is None:
        return None

    clean_content = normalize_content(step.get("content", ""), clean_type)
    if clean_content is None:
        return None

    clean_duration = normalize_duration(step.get("duration", 1), clean_type)

    return {
        "type": clean_type,
        "content": clean_content,
        "duration": clean_duration,
    }


def normalize_type(raw_type):
    raw_type = str(raw_type).lower().strip()

    type_map = {
        "text": "text", "txt": "text", "label": "text", "title": "text",
        "equation": "equation", "eq": "equation", "math": "equation",
        "latex": "equation", "formula": "equation",
        "wait": "wait", "pause": "wait", "sleep": "wait", "delay": "wait",
        "shape": "shape", "geometry": "shape", "diagram": "shape", "draw": "shape",
        "animation": "animation", "animate": "animation", "move": "animation",
        "graph": "graph", "plot": "graph", "chart": "graph",
        "function": "graph", "curve": "graph",
    }

    if raw_type in type_map:
        return type_map[raw_type]
    return None


def normalize_content(content, step_type):
    content = str(content).strip()
    content = " ".join(content.split())

    if content == "":
        return None

    if step_type == "wait":
        try:
            num = float(content)
            if num == int(num):
                return str(int(num))
            return str(num)
        except:
            return None

    return content


def normalize_duration(duration, step_type):
    try:
        duration = float(duration)
    except:
        duration = 1

    if duration < 0:
        duration = 1
    if step_type != "wait" and duration > 60:
        duration = 60
    if duration < 0.5:
        duration = 0.5

    return duration
