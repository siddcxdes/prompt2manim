from llm.planner import get_plan_from_user
from validation.validate import validate_plan, get_validation_report
from validation.normalize import normalize_plan
from renderer.actions import ActionFactory, actions_summary
from scenes.generated_scene import GeneratedScene, apply_scene_config


def main():
    
    print("\n" + "="*70)
    print("  welcome to prompt2manim - animation generator")
    print("="*70 + "\n")
    
    user_prompt = get_user_input()
    
    if not user_prompt:
        print("no prompt provided. exiting.")
        return False

    print("\n" + "-"*70)
    print("step 1: creating animation plan...")
    print("-"*70)
    
    plan = create_plan(user_prompt)
    
    if not plan:
        print("failed to create plan. exiting.")
        return False
    
    print("\n" + "-"*70)
    print("step 2: validating plan...")
    print("-"*70)
    
    if not validate_and_show(plan):
        print("plan validation failed. exiting.")
        return False
    
    print("\n" + "-"*70)
    print("step 3: normalizing plan...")
    print("-"*70)
    
    clean_plan = normalize_and_show(plan)
    
    if not clean_plan:
        print("normalization failed. exiting.")
        return False
    
    print("\n" + "-"*70)
    print("step 4: creating actions...")
    print("-"*70)
    
    actions = create_actions_and_show(clean_plan)
    
    if not actions:
        print("failed to create actions. exiting.")
        return False
    
    print("\n" + "-"*70)
    print("step 5: animation summary")
    print("-"*70)
    
    show_animation_summary(actions)

    print("\n" + "-"*70)
    print("step 6: ready to render")
    print("-"*70)
    
    if not confirm_rendering():
        print("rendering cancelled. exiting.")
        return False
    
    # Step 8: Get quality preference
    quality = get_quality_preference()
    
    # Step 9: Render with Manim
    print("\n" + "-"*70)
    print("step 7: rendering animation...")
    print("-"*70)
    
    success = render_animation(clean_plan, quality)
    
    if success:
        print("\n" + "="*70)
        print("  success! animation created!")
        print("="*70)
        print("\nyour video is ready in: media/videos/generated_scene/")
        return True
    else:
        print("\n" + "="*70)
        print("  failed! animation creation failed.")
        print("="*70)
        return False


def get_user_input():
    print("what animation would you like to create?")
    print("(example: 'show the pythagorean theorem')")
    print()
    
    user_input = input("enter your prompt: ").strip()
    
    if not user_input:
        return None
    
    return user_input


def create_plan(user_prompt):
    print(f"\ncreating plan for: '{user_prompt}'")
    
    plan = get_plan_from_user(user_prompt)
    
    if plan:
        print(f"plan created with {len(plan.get('steps', []))} steps")
        return plan
    else:
        print("failed to create plan")
        return None


def validate_and_show(plan):
    print("\nchecking plan structure...")
    
    is_valid = validate_plan(plan)
    
    if not is_valid:
        print("\nvalidation failed!")
        
        # show what's wrong
        report = get_validation_report(plan)
        if report["issues"]:
            print("\nissues found:")
            for issue in report["issues"]:
                print(f"  - {issue}")
        
        return False
    
    print("plan structure is valid!")
    return True

def normalize_and_show(plan):

    print("\ncleaning up plan...")
    
    clean_plan = normalize_plan(plan)
    
    if not clean_plan:
        print("normalization failed!")
        return None
    
    print("plan normalized successfully!")
    print("\nnormalized steps:")
    
    for i, step in enumerate(clean_plan["steps"]):
        print(f"  {i+1}. [{step['type']}] {step['content'][:50]} (duration: {step['duration']}s)")
    
    return clean_plan


def create_actions_and_show(plan):
    print("\nconverting to animation actions...")
    
    try:
        actions = ActionFactory.create_all(plan)
        print(f"created {len(actions)} actions")
        return actions
    except Exception as error:
        print(f"failed to create actions: {error}")
        return None


def show_animation_summary(actions):
    summary = actions_summary(actions)
    
    print(f"\ntotal actions: {summary['total_actions']}")
    print(f"total duration: {summary['total_duration']} seconds")
    print(f"action breakdown:")
    
    for action_type, count in summary["action_types"].items():
        print(f"  - {action_type}: {count}")

def confirm_rendering():
    print("\nready to render animation with manim")
    print("this may take a few minutes depending on quality...")
    print()
    
    response = input("do you want to continue? (yes/no): ").strip().lower()
    
    return response in ["yes", "y"]


def get_quality_preference():
    print("\nquality options:")
    print("  1. preview   - fast preview (480p, 15fps)")
    print("  2. hd        - hd quality (720p, 30fps) [default]")
    print("  3. fullscreen - full quality (1080p, 60fps)")
    print("  4. 4k        - 4k quality (2160p, 30fps)")
    print()
    
    choice = input("select quality (1-4) [default: 2]: ").strip()
    
    quality_map = {
        "1": "preview",
        "2": "hd",
        "3": "fullscreen",
        "4": "4k"
    }
    
    return quality_map.get(choice, "hd")

def render_animation(plan, quality):
    print(f"\nrendering with quality: {quality}")
    
    try:
        apply_scene_config(quality)
    
        scene = GeneratedScene(plan=plan)
        
        print("\nrendering... (this may take a few minutes)")
        print("   do not close this window until rendering is complete")

        # Actually render the scene - this was missing!
        scene.render()

        print("\nanimation rendered successfully!")
        print(f"   quality: {quality}")
        print(f"   output: media/videos/generated_scene/")
        
        return True
    
    except Exception as error:
        print(f"\nrendering failed: {error}")
        return False


def batch_mode(prompt, quality="hd"):

    print("\n" + "="*70)
    print("  batch mode - animation generator")
    print("="*70 + "\n")
    
    plan = create_plan(prompt)
    if not plan:
        return False
    
    if not validate_and_show(plan):
        return False

    clean_plan = normalize_and_show(plan)
    if not clean_plan:
        return False
    
    actions = create_actions_and_show(clean_plan)
    if not actions:
        return False

    show_animation_summary(actions)

    print(f"\nrendering with quality: {quality}")
    return render_animation(clean_plan, quality)