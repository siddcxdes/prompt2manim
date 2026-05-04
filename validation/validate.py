"""
Validation - checks if a plan from the AI is valid before we try to use it.
Makes sure the plan has the right structure and all required fields.
"""


def validate_plan(plan):
    """
    Check if the plan is valid.
    Returns True if it's good, False if something is wrong.
    """

    # plan must exist
    if plan is None:
        return False

    # plan must be a dict (like {"steps": [...]})
    if not isinstance(plan, dict):
        return False

    # plan must have a "steps" key
    if "steps" not in plan:
        return False

    # steps must be a list
    if not isinstance(plan["steps"], list):
        return False

    # steps list can't be empty
    if len(plan["steps"]) == 0:
        return False

    # can't have more than 50 steps
    if len(plan["steps"]) > 50:
        return False

    # check each step
    for i in range(len(plan["steps"])):
        step = plan["steps"][i]
        if not validate_step(step, i):
            return False

    return True


def validate_step(step, index):
    """Check if a single step is valid."""

    # step must be a dict
    if not isinstance(step, dict):
        return False

    # must have "type" key
    if "type" not in step:
        return False

    # must have "content" key
    if "content" not in step:
        return False

    # check the type is one we know
    step_type = str(step["type"]).lower().strip()
    allowed = ["text", "equation", "wait", "shape", "animation", "graph"]

    if step_type not in allowed:
        return False

    # content can't be empty
    content = str(step["content"]).strip()
    if content == "":
        return False

    # content can't be too long
    if len(content) > 500:
        return False

    # special check for wait: content must be a number
    if step_type == "wait":
        try:
            wait_time = float(content)
            if wait_time < 0:
                return False
        except:
            return False

    return True


def get_validation_report(plan):
    """
    Get a detailed report about what's wrong with a plan.
    Returns a dict with is_valid, total_steps, step_types, and issues.
    """

    report = {
        "is_valid": True,
        "total_steps": 0,
        "step_types": [],
        "issues": [],
    }

    if plan is None:
        report["is_valid"] = False
        report["issues"].append("Plan is empty")
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
        report["issues"].append("Steps is not a list")
        return report

    if len(steps) == 0:
        report["is_valid"] = False
        report["issues"].append("Steps list is empty")
        return report

    report["total_steps"] = len(steps)

    allowed = ["text", "equation", "wait", "shape", "animation", "graph"]

    for i in range(len(steps)):
        step = steps[i]

        if not isinstance(step, dict):
            report["is_valid"] = False
            report["issues"].append("Step " + str(i) + " is not a dictionary")
            continue

        if "type" in step:
            step_type = str(step["type"]).lower().strip()
            report["step_types"].append(step_type)

            if step_type not in allowed:
                report["is_valid"] = False
                report["issues"].append("Step " + str(i) + " has invalid type: " + step_type)
        else:
            report["is_valid"] = False
            report["issues"].append("Step " + str(i) + " is missing type")

        if "content" not in step:
            report["is_valid"] = False
            report["issues"].append("Step " + str(i) + " is missing content")
        else:
            content = str(step["content"]).strip()
            if content == "":
                report["is_valid"] = False
                report["issues"].append("Step " + str(i) + " has empty content")

    return report
