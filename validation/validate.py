def validate_plan(plan):
    if plan is None:
        print(" validation failed: plan is none (empty)")
        return False
    
    if not isinstance(plan, dict):
        print("validation failed: plan must be a dictionary")
        return False
    
    if "steps" not in plan:
        print("validation failed: plan must have 'steps' key")
        return False
    
    if not isinstance(plan["steps"], list):
        print(" validation failed: 'steps' must be a list")
        return False

    if len(plan["steps"]) == 0:
        print("  validation failed: 'steps' list is empty (no steps)")
        return False

    if len(plan["steps"]) > 50:
        print(f"  validation failed: too many steps ({len(plan['steps'])}). maximum is 50")
        return False

    for index, step in enumerate(plan["steps"]):
        if not validate_step(step, index):
            return False

    print(f"validation passed: plan is valid ({len(plan['steps'])} steps)")
    return True


def validate_step(step, index):
   
    if not isinstance(step, dict):
        print(f"  validation failed: step {index} is not a dictionary (got {type(step).__name__})")
        return False
    
    if "type" not in step:
        print(f"  validation failed: step {index} is missing 'type' key")

    if "content" not in step:
        print(f"  validation failed: step {index} is missing 'content' key")
        return False

    step_type = str(step["type"]).lower().strip()
    
    allowed_types = ["text", "equation", "wait", "shape", "animation", "graph"]
    
    if step_type not in allowed_types:
        print(f"  validation failed: step {index} has invalid type '{step_type}'")
        print(f"   allowed types are: {', '.join(allowed_types)}")
        return False
    
    content = str(step["content"]).strip()
    
    if not content:
        print(f"  validation failed: step {index} has empty content")
        return False
    
    if len(content) > 500:
        print(f"  validation failed: step {index} content is too long ({len(content)} chars, max 500)")
        return False

    if step_type == "text":
        if len(content) > 100:
            print(f"warning: step {index} text is long ({len(content)} chars, recommended max 100)")
    
    elif step_type == "equation":
        if len(content) > 200:
            print(f"warning: step {index} equation is long ({len(content)} chars, recommended max 200)")
    
    elif step_type == "wait":
        try:
            wait_time = float(content)
            if wait_time < 0:
                print(f"  validation failed: step {index} wait time cannot be negative ({wait_time})")
                return False
            if wait_time > 60:
                print(f"warning: step {index} wait time is very long ({wait_time} seconds)")
        except ValueError:
            print(f"  validation failed: step {index} wait content must be a number (got '{content}')")
            return False
    
    return True


def get_validation_report(plan):
    report = {
        "is_valid": True,
        "total_steps": 0,
        "step_types": [],
        "issues": []
    }
  
    if plan is None:
        report["is_valid"] = False
        report["issues"].append("Plan is None")
        return report
  
    if not isinstance(plan, dict):
        report["is_valid"] = False
        report["issues"].append("Plan is not a dictionary")
        return report
  
    if "steps" not in plan:
        report["is_valid"] = False
        report["issues"].append("Plan has no 'steps' key")
        return report
    
    steps = plan["steps"]

    if not isinstance(steps, list):
        report["is_valid"] = False
        report["issues"].append("'steps' is not a list")
        return report
    
    if len(steps) == 0:
        report["is_valid"] = False
        report["issues"].append("'steps' list is empty")
        return report
    
    report["total_steps"] = len(steps)

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            report["is_valid"] = False
            report["issues"].append(f"Step {index} is not a dictionary")
            continue
        
        if "type" in step:
            step_type = str(step["type"]).lower().strip()
            report["step_types"].append(step_type)

            allowed_types = ["text", "equation", "wait", "shape", "animation", "graph"]
            if step_type not in allowed_types:
                report["is_valid"] = False
                report["issues"].append(f"Step {index} has invalid type '{step_type}'")
        else:
            report["is_valid"] = False
            report["issues"].append(f"Step {index} missing 'type' key")
        
        if "content" not in step:
            report["is_valid"] = False
            report["issues"].append(f"Step {index} missing 'content' key")
        else:
            content = str(step["content"]).strip()
            if not content:
                report["is_valid"] = False
                report["issues"].append(f"Step {index} has empty content")
    
    return report
