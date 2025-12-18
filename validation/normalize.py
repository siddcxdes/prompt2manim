def normalize_plan(plan):
    if not plan:
        print("  error: plan is none or empty")
        return None

    normalized_plan = {
        "steps": []
    }
    
    for index, step in enumerate(plan.get("steps", [])):
        normalized_step = normalize_step(step, index)
        
        if normalized_step is not None:
            normalized_plan["steps"].append(normalized_step)
  
    if len(normalized_plan["steps"]) == 0:
        print("  error: no valid steps after normalization")
        return None
    
    print(f"  normalization complete: {len(normalized_plan['steps'])} steps normalized")
    return normalized_plan


def normalize_step(step, index):
    if not step:
        print(f"   warning: step {index} is empty, skipping")
        return None
    
    step_type = normalize_type(step.get("type", "text"))
    
    if step_type is None:
        print(f"   warning: step {index} has invalid type, skipping")
        return None
    
    content = normalize_content(step.get("content", ""), step_type)
    
    if content is None:
        print(f"   warning: step {index} has no content, skipping")
        return None
    
    duration = normalize_duration(step.get("duration", 1), step_type)
    
    normalized_step = {
        "type": step_type,
        "content": content,
        "duration": duration
    }
    
    return normalized_step


def normalize_type(step_type):
    
    step_type = str(step_type).lower().strip()
    
    type_mapping = {
        "text": "text",
        "txt": "text",
        "label": "text",
        "title": "text",
        "t": "text",
        

        "equation": "equation",
        "eq": "equation",
        "math": "equation",
        "latex": "equation",
        "formula": "equation",
        "e": "equation",

        "wait": "wait",
        "pause": "wait",
        "sleep": "wait",
        "delay": "wait",
        "w": "wait",

        "shape": "shape",
        "geometry": "shape",
        "diagram": "shape",
        "draw": "shape",
        "s": "shape",

        "animation": "animation",
        "animate": "animation",
        "move": "animation",
        "motion": "animation",
        "a": "animation",
        
        # Graph types
        "graph": "graph",
        "plot": "graph",
        "chart": "graph",
        "function": "graph",
        "curve": "graph",
        "g": "graph",
    }
    
    if step_type in type_mapping:
        return type_mapping[step_type]
    else:
        return None


def normalize_content(content, step_type):

    content = str(content).strip()

    content = " ".join(content.split())
    
    if not content:
        return None
    
    if step_type == "text":
        return content
    
    elif step_type == "equation":
        return content
    
    elif step_type == "wait":
        try:
            wait_time = float(content)
            return str(int(wait_time)) if wait_time == int(wait_time) else str(wait_time)
        except ValueError:
            return None
    
    elif step_type == "shape" or step_type == "animation":
        return content
    
    else:
        return content


def normalize_duration(duration, step_type):
 
    try:
        duration = float(duration)
    except (ValueError, TypeError):
        duration = 1

    if duration < 0:
        duration = 1
    
    if step_type == "wait":
        return duration

    if duration > 60:
        duration = 60 
    
    return duration


def normalize_all_types(plan):

    if not plan or "steps" not in plan:
        return plan
    
    for step in plan["steps"]:
        if "type" in step:
            normalized_type = normalize_type(step["type"])
            if normalized_type:
                step["type"] = normalized_type
    
    return plan


def normalize_all_content(plan):
    if not plan or "steps" not in plan:
        return plan
    
    for step in plan["steps"]:
        if "content" in step:
            # Clean up the content
            content = str(step["content"]).strip()
            content = " ".join(content.split())
            step["content"] = content
    
    return plan


def add_default_durations(plan, default_duration=1):

    if not plan or "steps" not in plan:
        return plan
    
    for step in plan["steps"]:
        if "duration" not in step:
            step["duration"] = default_duration
    
    return plan
