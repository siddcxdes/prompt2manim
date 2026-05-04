import os
import json
import re
import requests
from dotenv import load_dotenv

# load the .env file so we can use the API key
load_dotenv()


def get_plan_from_user(user_prompt):
    """
    Takes what the user typed and sends it to Pollination AI.
    Returns two things: the plan (dict) and an error message (string).
    If it works, error will be None. If it fails, plan will be None.
    """

    # check if the user actually typed something
    if not user_prompt or user_prompt.strip() == "":
        return None, "Please type something first."

    # build the system message (instructions for the AI)
    system_message = build_system_prompt()

    # try up to 2 times in case the AI gives bad output
    tries = 0
    max_tries = 2

    while tries < max_tries:
        tries = tries + 1

        # call the AI
        ai_text = call_ai(system_message, user_prompt)

        # if the AI didn't respond, try again
        if ai_text is None:
            continue

        # try to get JSON from the AI's response
        plan = get_json_from_text(ai_text)

        # if we got a valid plan, return it
        if plan is not None:
            return plan, None

    # if we get here, all tries failed
    return None, "Could not generate an animation plan. Please try again."


def build_system_prompt():
    """
    This is the instruction we give to the AI so it knows
    what kind of output we want (a JSON animation plan).
    """

    prompt = """You are an animation planner for Manim (math animation library).
Your job is to turn the user's request into a JSON animation plan.

IMPORTANT: Reply ONLY with JSON. No other text. No markdown. Just JSON.

The JSON format is:
{
  "steps": [
    {"type": "text", "content": "Title Here", "duration": 2},
    {"type": "equation", "content": "a^2 + b^2 = c^2", "duration": 3}
  ]
}

Here are the step types you can use:

1. text - for showing text on screen
   Example: {"type": "text", "content": "Hello World", "duration": 2}

2. equation - for math formulas (use LaTeX)
   Example: {"type": "equation", "content": "E = mc^2", "duration": 3}

3. graph - for plotting math functions
   Works with: sin(x), cos(x), tan(x), x^2, x^3, sqrt(x)
   Example: {"type": "graph", "content": "sin(x)", "duration": 4}

4. shape - for drawing shapes
   Works with: circle, square, triangle, rectangle, line, star
   Example: {"type": "shape", "content": "circle", "duration": 2}

5. animation - for animating the last object
   Works with: rotate, scale, move
   Example: {"type": "animation", "content": "rotate", "duration": 2}

6. wait - for pausing
   Example: {"type": "wait", "content": "1", "duration": 1}

Rules:
- Output must start with { and end with }
- Must have a "steps" array
- Each step needs "type", "content", and "duration"
- Max 15 steps
- Keep text under 60 characters
- Start with a title, then visuals, then equations
- Make it visually interesting with graphs and shapes

Example for "Show sine wave":
{
  "steps": [
    {"type": "text", "content": "The Sine Wave", "duration": 2},
    {"type": "graph", "content": "sin(x)", "duration": 4},
    {"type": "equation", "content": "y = sin(x)", "duration": 3},
    {"type": "text", "content": "Oscillates between -1 and 1", "duration": 2}
  ]
}

Now create a plan for the user's request."""

    return prompt


def call_ai(system_message, user_prompt):
    """
    Sends the prompt to Pollination AI and gets back the response text.
    Returns None if something goes wrong.
    """

    # get the API key from .env file
    api_key = os.getenv("POLLINATION_API_KEY")

    # set up the headers
    headers = {
        "Content-Type": "application/json",
    }

    # add API key if we have one
    if api_key:
        headers["Authorization"] = "Bearer " + api_key

    # build the request body (this is what we send to the AI)
    body = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 4096,
    }

    # send the request
    try:
        response = requests.post(
            "https://gen.pollinations.ai/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=60,
        )

        # check if the request was successful
        if response.status_code != 200:
            print("AI returned error status: " + str(response.status_code))
            return None

        # get the response data
        data = response.json()

        # pull out the AI's message
        ai_message = data["choices"][0]["message"]["content"]
        return ai_message

    except Exception as error:
        print("Error calling AI: " + str(error))
        return None


def get_json_from_text(text):
    """
    Takes the AI's response text and tries to extract JSON from it.
    Returns a dict if successful, None if not.
    """

    if not text:
        return None

    # clean up the text
    text = text.strip()

    # remove markdown code fences if the AI wrapped it in ```json ... ```
    if text.startswith("```"):
        # remove the opening fence
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # remove the closing fence
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    # try to parse it directly
    try:
        result = json.loads(text)
        if "steps" in result:
            return result
    except:
        pass

    # if that didn't work, try to find JSON in the text
    # look for anything between { and }
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            result = json.loads(match.group(0))
            if "steps" in result:
                return result
        except:
            pass

    return None
