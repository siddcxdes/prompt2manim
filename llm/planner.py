import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

"""this get_plan_from_user take user prompt as input and it send it to llm along with the system message"""
def get_plan_from_user(user_prompt):
    if not user_prompt or not user_prompt.strip():
        print("error: please provide a prompt (don't leave it empty)")
        return None
    
    system_message = create_system_message()
    
    ai_response = call_gemini_api(system_message, user_prompt)
    
    if ai_response is None:
        print("error: failed to get response from gemini api")
        return None

    plan = extract_json_from_response(ai_response)
    
    if plan is None:
        print("error: could not extract plan from ai response")
        return None
    
    return plan

"""the system message is the prompt that we give to the llm to generate animation planner in json format"""
def create_system_message():
    
    message = """You are an animation planner for Manim (math animation library). 
Your job is to create visual animation steps that look AMAZING.

When the user asks for an animation, respond ONLY with valid JSON.
Do NOT write anything else, just the JSON.

Response format:
{
  "steps": [
    {"type": "text", "content": "your text here", "duration": 2},
    {"type": "equation", "content": "a^2 + b^2 = c^2", "duration": 3}
  ]
}

## Available Types:

1. text - for titles and labels
   Example: {"type": "text", "content": "Pythagorean Theorem", "duration": 2}

2. equation - for math formulas (use LaTeX format)
   Important: Use DOUBLE BACKSLASHES for all LaTeX commands!
   Example: {"type": "equation", "content": "E = mc^2", "duration": 3}
   Example: {"type": "equation", "content": "\\\\frac{1}{2}", "duration": 3}

3. graph - for plotting mathematical functions (VERY VISUAL!)
   Supported: sin, cos, tan, x^2, x^3, sqrt, exp, log, linear
   Example: {"type": "graph", "content": "sin(x)", "duration": 4}
   Example: {"type": "graph", "content": "x^2", "duration": 4}

4. shape - for geometric shapes
   Supported: circle, square, triangle, rectangle, line, star
   Example: {"type": "shape", "content": "triangle", "duration": 2}

5. animation - for movement animations
   Supported: rotate, bounce, scale, color_change
   Example: {"type": "animation", "content": "rotate", "duration": 2}

6. wait - to pause between steps
   Example: {"type": "wait", "content": "1", "duration": 1}

## Rules:
1. Always start with { and end with }
2. Always include "steps" key with an array
3. Each step MUST have "type", "content", and "duration" keys
4. Maximum 50 steps per request
5. Use graphs and shapes to make it visually interesting!
6. Start with a title (text), show visuals (graph/shape), then equations

## Example for "Show the quadratic function":
{
  "steps": [
    {"type": "text", "content": "Quadratic Function", "duration": 2},
    {"type": "graph", "content": "x^2", "duration": 4},
    {"type": "equation", "content": "f(x) = x^2", "duration": 3},
    {"type": "text", "content": "The parabola shape!", "duration": 2}
  ]
}

## Example for "Explain sine wave":
{
  "steps": [
    {"type": "text", "content": "The Sine Wave", "duration": 2},
    {"type": "graph", "content": "sin(x)", "duration": 5},
    {"type": "equation", "content": "y = \\\\sin(x)", "duration": 3},
    {"type": "text", "content": "Oscillates between -1 and 1", "duration": 2}
  ]
}

Now create a VISUAL animation plan for the user's request. USE GRAPHS AND SHAPES!"""
    
    return message

"""this call the gemini_api"""
def call_gemini_api(system_message, user_prompt):
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("error: GEMINI_API_KEY environment variable not set")
        return None
    
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            generation_config=generation_config,
            system_instruction=system_message,
        )
        
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_prompt)
        return response.text
        
    except Exception as error:
        print(f"error connecting to gemini api: {error}")
        return None

'''this is for the safe side , to extract the json from the llm response, ignoring the rest of the message'''
def extract_json_from_response(response_text):
    try:
        plan = json.loads(response_text)
        return plan
    except json.JSONDecodeError:
        pass
    import re
    
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    if json_match:
        json_text = json_match.group(0)
        try:
            plan = json.loads(json_text)
            return plan
        except json.JSONDecodeError:
            pass

    return None
