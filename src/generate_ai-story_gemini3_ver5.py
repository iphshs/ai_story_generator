import datetime
import os
import logging
import time
import json
import random
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv # Added for loading .env file

# --- Configuration ---
LOG_DIR = "./log"
STORIES_DIR = "../stories"
NUM_REVISION_PASSES = 1 # How many times to run the review/revise pass
GEMINI_MODEL_NAME = "gemini-1.5-flash" # Or another suitable model like gemini-1.5-flash

# --- Logging Setup ---
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIR, f"story_log_{timestamp}.txt")

# Configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- Load Environment Variables from .env file ---
# Create a .env file in the same directory with:
# GOOGLE_API_KEY='YOUR_API_KEY'
load_dotenv()
logging.info("Attempted to load environment variables from .env file.")

# --- API Key Configuration ---
# Now attempts to read the key loaded by dotenv or already set in environment
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # If still not found after load_dotenv(), raise error
        raise ValueError("API Key not found. Set GOOGLE_API_KEY in your .env file or environment variables.")
    genai.configure(api_key=api_key)
    logging.info("Gemini API Key configured successfully.")
except ValueError as e:
    logging.error(f"API Configuration Error: {e}")
    exit(f"Exiting: {e}") # Exit with the specific error message
except Exception as e:
    logging.error(f"An unexpected error occurred during API configuration: {e}")
    exit("Exiting due to unexpected API configuration error.")


# --- Gemini Model Initialization ---
# This step implicitly checks if the configuration was okay enough to proceed
model = None # Initialize model to None
model_initialized = False
try:
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    logging.info(f"Gemini model '{GEMINI_MODEL_NAME}' initialized.")
    # Set a flag indicating successful initialization
    model_initialized = True
except Exception as e:
    logging.error(f"Failed to initialize Gemini model: {e}")
    # Keep model_initialized as False


# --- Default Options for Random Selection ---
RANDOM_DEFAULTS = {
    "characters": [
        "Leo the lion cub and Sky the wise old owl",
        "Pip the adventurous squirrel and Barnaby the badger",
        "Lily the lost lamb and Finley the firefly",
        "Captain Bluejay and the Space Mice",
        "Zara the young inventor and Bolt her robot dog"
    ],
    "setting": [
        "the Whispering Savannah at twilight", # Corrected multiline string
        "a bustling city park full of secrets",
        "a magical forest where mushrooms glow",
        "a creaky old attic filled with forgotten toys",
        "a spaceship exploring colorful nebulae"
    ],
    "theme": [
        "overcoming fear of the dark",
        "the importance of friendship",
        "the joy of discovery",
        "learning to share",
        "being brave even when scared"
    ],
    "genre": [
        "gentle adventure / bedtime story",
        "mystery",
        "fantasy",
        "science fiction",
        "slice of life"
    ],
    "reading_level": ["K", "1", "2"],
    "age_appropriate": ["3-5", "4-6", "5-7"],
    "read_aloud_time": ["5", "7", "10"],
    "other_details": [
        "Include twinkling stars and friendly fireflies.",
        "Features a hidden map.",
        "A magical object plays a key role.",
        "A funny misunderstanding happens.",
        "They have to build something together."
    ],
    "avoid_content": [
        "predators, danger, complex words",
        "scary monsters, sadness",
        "anything too noisy or chaotic",
        "complex family situations",
        "violence of any kind"
    ]
}

# --- User Input Function ---
def get_user_input(use_defaults=False):
    """
    Collects detailed user preferences for the story.
    If the user presses Enter without input, assigns a random default.
    """
    print("\n--- Story Preferences (Press Enter for random defaults) ---")
    logging.info("Collecting user preferences...")

    preferences = {}

    preference_prompts = [
        ("characters", "1. Characters?"),
        ("setting", "2. Setting?"),
        ("theme", "3. Theme?"),
        ("genre", "4. Genre?"),
        ("reading_level", "5. Reading Level?"),
        ("age_appropriate", "6. Age Range?"),
        ("read_aloud_time", "7. Read Time (min)?"),
        ("other_details", "8. Other Details?"),
        ("avoid_content", "9. Avoid Content?")
    ]

    for key, prompt_text in preference_prompts:
        user_input = input(f"{prompt_text}: ").strip()
        if not user_input:
            random_value = random.choice(RANDOM_DEFAULTS[key])
            preferences[key] = random_value
            print(f"   > No input provided. Using random default: '{random_value}'")
            logging.info(f"User provided no input for '{key}'. Assigned random default: '{random_value}'")
        else:
            preferences[key] = user_input
            logging.info(f"User provided input for '{key}': '{user_input}'")

    # Initialize state holders
    preferences["story_plan"] = {}
    preferences["story_plot"] = {}
    preferences["draft_story"] = ""
    preferences["revised_story"] = ""
    preferences["final_story_with_prompts"] = ""
    preferences["image_prompts"] = []

    logging.info(f"Final Preferences Collected: {preferences}")
    return preferences


# --- Actual Gemini API Call ---
def call_gemini_api(prompt, task_description):
    """
    Calls the configured Gemini API model with the given prompt.
    Logs the prompt and response, handles potential API errors.
    Returns the response text or None on failure.
    """
    global model # Ensure we're using the globally initialized model
    if not model: # Check if model was initialized successfully
         logging.error(f"Gemini model not initialized. Cannot make API call for '{task_description}'.")
         return None

    logging.info(f"\n--- Calling Gemini API: {task_description} ---")
    logging.info(f"PROMPT:\n------\n{prompt}\n------")

    try:
        # Make the API call
        generation_config = None
        if "Plan Story Elements" in task_description or "Plot Narrative Outline" in task_description:
             generation_config=genai.types.GenerationConfig(
                 candidate_count=1,
                 # response_mime_type="application/json", # Keep commented unless sure it's supported
             )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
            )

        # Log the raw response text
        # Use response.text directly as it handles potential resolution/errors gracefully
        response_text = response.text
        logging.info(f"API RESPONSE (Text):\n-------------------\n{response_text}\n-------------------")

        # Check for safety blocks (more robust check)
        if not response.candidates:
             # Check if prompt feedback indicates blocking
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                  logging.error(f"API call blocked for prompt. Reason: {response.prompt_feedback.block_reason}")
                  return None
             else:
                  # No candidates and no explicit block reason - might be another issue
                  logging.error("API response missing candidates, but no block reason given.")
                  # Log the full response for debugging if possible
                  try:
                      logging.debug(f"Full API response object: {response}")
                  except Exception:
                      logging.debug("Could not log full API response object.")
                  return None # Or handle as appropriate

        # Access the first candidate safely after checking existence
        candidate = response.candidates[0]

        # Check finish reason if needed
        # *** CORRECTED FinishReason ACCESS ***
        if candidate.finish_reason != genai.FinishReason.STOP:
             logging.warning(f"API response finished with reason: {candidate.finish_reason}")
             # Check for safety issues in the candidate itself
             if candidate.safety_ratings:
                 for rating in candidate.safety_ratings:
                      # *** CORRECTED HarmProbability ACCESS ***
                      if rating.probability != genai.HarmProbability.NEGLIGIBLE:
                           logging.error(f"API response flagged for safety: Category {rating.category}, Probability {rating.probability}")
                           # Decide if you want to return None based on safety flags
                           # return None

        return response_text

    except google_exceptions.GoogleAPIError as e:
        logging.error(f"Google API Error during '{task_description}': {e}")
        return None
    except AttributeError as e:
        # Catch potential attribute errors during response processing
        logging.error(f"Attribute error processing API response for '{task_description}': {e}", exc_info=True)
        # Log the problematic response object if possible
        try:
            logging.debug(f"Problematic API response object: {response}")
        except Exception:
             logging.debug("Could not log problematic API response object.")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during Gemini API call for '{task_description}': {e}", exc_info=True)
        return None


# --- Story Generation Passes (Using Actual API Calls) ---

def plan_story_elements(current_state):
    """Pass 1: Plan key story elements using Gemini."""
    logging.info("=== PASS 1: Planning Story Elements ===")
    prompt = f"""
    Based on the following user preferences for a children's story, outline the key elements.
    Provide a structured JSON response containing ONLY the JSON object, no introductory text or markdown formatting.

    Preferences:
    - Characters: {current_state['characters']}
    - Setting: {current_state['setting']}
    - Theme: {current_state['theme']}
    - Genre: {current_state['genre']}
    - Age Appropriate: {current_state['age_appropriate']}
    - Other Details: {current_state['other_details']}
    - Avoid Content: {current_state['avoid_content']}

    JSON Structure:
    {{
      "detailed_characters": "Brief descriptions focusing on traits relevant to the theme.",
      "setting_details": "Specific sensory details or features of the setting.",
      "key_plot_points": ["List", "of", "3-5 bullet points", "outlining core story progression."],
      "extra_elements": "Mention how 'other_details' can be woven in."
    }}
    """
    response_text = call_gemini_api(prompt, "Plan Story Elements")
    if response_text:
        try:
            cleaned_response = response_text.strip().removeprefix('```json').removesuffix('```').strip()
            current_state['story_plan'] = json.loads(cleaned_response)
            logging.info("Successfully parsed story plan from API response.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse story plan JSON from API response: {e}. Response was:\n{response_text}")
            current_state['story_plan'] = {"error": "Failed to parse plan JSON", "raw_response": response_text}
    else:
        logging.error("No response received from API for story planning or API call failed.")
        current_state['story_plan'] = {"error": "API call failed or returned no text"}


def plot_narrative(current_state):
    """Pass 2: Create a structured plot outline using Gemini."""
    logging.info("=== PASS 2: Plotting Narrative Outline ===")
    if not current_state.get('story_plan') or 'error' in current_state.get('story_plan', {}):
        logging.warning("Skipping plot narrative due to missing or failed previous step (Story Plan).")
        return

    prompt = f"""
    Using the story plan below, create a structured narrative plot outline for a children's story ({current_state['genre']}, age {current_state['age_appropriate']}).
    Provide a structured JSON response containing ONLY the JSON object, no introductory text or markdown formatting.

    Story Plan:
    {json.dumps(current_state['story_plan'], indent=2)}

    User Preferences Summary:
    - Theme: {current_state['theme']}
    - Characters: {current_state['characters']}
    - Setting: {current_state['setting']}
    - Read Aloud Time: ~{current_state['read_aloud_time']} mins

    JSON Structure:
    {{
      "title_suggestion": "A suitable title.",
      "logline": "A one-sentence summary.",
      "outline": {{
        "beginning": "Brief description of the beginning.",
        "rising_action": "Brief description of the rising action.",
        "climax": "Brief description of the climax.",
        "falling_action": "Brief description of the falling action.",
        "resolution": "Brief description of the resolution."
      }}
    }}
    """
    response_text = call_gemini_api(prompt, "Plot Narrative Outline")
    if response_text:
        try:
            cleaned_response = response_text.strip().removeprefix('```json').removesuffix('```').strip()
            current_state['story_plot'] = json.loads(cleaned_response)
            logging.info("Successfully parsed story plot from API response.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse story plot JSON from API response: {e}. Response was:\n{response_text}")
            current_state['story_plot'] = {"error": "Failed to parse plot JSON", "raw_response": response_text}
    else:
        logging.error("No response received from API for story plotting or API call failed.")
        current_state['story_plot'] = {"error": "API call failed or returned no text"}


def flesh_out_story(current_state):
    """Pass 3: Write the full story draft using Gemini."""
    logging.info("=== PASS 3: Fleshing Out Story Draft ===")
    if not current_state.get('story_plot') or 'error' in current_state.get('story_plot', {}):
        logging.warning("Skipping story draft due to missing or failed previous step (Story Plot).")
        return

    prompt = f"""
    Write the full text for a children's story based on the plot outline and elements below.
    Return ONLY the story text, with no introductory or concluding phrases like "Here is the story:".

    Target Audience: Age {current_state['age_appropriate']}, Reading Level {current_state['reading_level']}
    Genre: {current_state['genre']}
    Theme: {current_state['theme']}
    Approximate Length: Suitable for {current_state['read_aloud_time']} min read-aloud.
    Content to Avoid: {current_state['avoid_content']}
    Include: {current_state['other_details']}

    Plot Outline:
    {json.dumps(current_state['story_plot'], indent=2)}

    Story Plan Elements:
    {json.dumps(current_state['story_plan'], indent=2)}

    Write the story clearly and engagingly for young children. Ensure paragraphs are well-separated.
    """
    response_text = call_gemini_api(prompt, "Flesh Out Story")
    if response_text:
        current_state['draft_story'] = response_text.strip() # Store the raw text
        logging.info("Successfully received draft story text from API.")
    else:
         logging.error("No response received from API for story drafting or API call failed.")
         current_state['draft_story'] = "# Error: API call failed during story drafting."


def review_and_revise(current_state, pass_num):
    """Pass 4 (and potentially more): Review and revise the draft using Gemini."""
    logging.info(f"=== PASS 4.{pass_num}: Reviewing and Revising Story ===")
    story_to_review = current_state.get('revised_story') or current_state.get('draft_story') # Use latest version
    if not story_to_review or "Error" in story_to_review[:10]: # Check start for error marker
         logging.warning("Skipping review/revision due to missing or invalid story draft.")
         return

    prompt = f"""
    Review the following children's story draft. Check for:
    - Coherence and logical flow (beginning, middle, end).
    - Character consistency and believability (for the context).
    - Clear integration of the theme: '{current_state['theme']}'.
    - Age appropriateness (language, concepts) for age {current_state['age_appropriate']} / level {current_state['reading_level']}.
    - Engaging narrative style for the genre: '{current_state['genre']}'.
    - Adherence to avoidance criteria: '{current_state['avoid_content']}'.
    - Approximate length suitable for {current_state['read_aloud_time']} mins.

    Provide ONLY the revised version of the story text, incorporating improvements based on the review criteria. Do not include feedback commentary, just the improved story text.

    Draft to Review:
    ---
    {story_to_review}
    ---
    """
    response_text = call_gemini_api(prompt, f"Review and Revise Pass {pass_num}")
    if response_text:
        current_state['revised_story'] = response_text.strip()
        logging.info("Successfully received revised story text from API.")
    else:
        logging.error("No response received from API for story revision or API call failed.")
        # Keep the previous version if revision fails
        logging.warning("Keeping previous story version as revision API call failed.")
        if not current_state.get('revised_story'): # Only overwrite if it wasn't already set by a successful previous revision
             current_state['revised_story'] = story_to_review


def add_image_prompts(current_state):
    """Pass 5: Identify key scenes and add image prompts using Gemini."""
    logging.info("=== PASS 5: Adding Image Prompts ===")
    story_to_illustrate = current_state.get('revised_story') or current_state.get('draft_story')
    if not story_to_illustrate or "Error" in story_to_illustrate[:10]:
        logging.warning("Skipping image prompt addition due to missing or invalid story.")
        return

    prompt = f"""
    Read the following children's story ({current_state['genre']}, age {current_state['age_appropriate']}).
    Identify 3 key scenes that would benefit from an illustration (beginning, middle, end if possible).
    Insert text-to-image prompts directly into the story text at appropriate locations.
    The prompts should be enclosed in square brackets, like [IMAGE: description]. Ensure there is a blank line before and after each prompt.
    The description should be concise but evocative, specifying the style (e.g., gentle illustration, cartoonish, watercolor) and key elements of the scene relevant to the story and age group.

    Return ONLY the complete story text with the prompts inserted. Do not add any other commentary.

    Story Text:
    ---
    {story_to_illustrate}
    ---
    """
    response_text = call_gemini_api(prompt, "Add Image Prompts")
    if response_text:
        current_state['final_story_with_prompts'] = response_text.strip()
        # Also extract prompts separately if needed
        current_state['image_prompts'] = [line.strip() for line in response_text.split('\n') if line.strip().startswith("[IMAGE:")]
        logging.info(f"Successfully received story with {len(current_state['image_prompts'])} image prompts from API.")
    else:
        logging.error("No response received from API for adding image prompts or API call failed.")
        current_state['final_story_with_prompts'] = f"# Error adding prompts: API call failed.\n\n{story_to_illustrate}" # Fallback


def finalize_story(current_state):
    """Pass 6: Final check and preparation for output."""
    logging.info("=== PASS 6: Finalizing Story ===")
    # Use the latest available version, prioritizing the one with prompts
    final_content = (
        current_state.get('final_story_with_prompts') or
        current_state.get('revised_story') or
        current_state.get('draft_story')
    )

    # Check if the best available content is still None or an error dict/string
    content_is_valid = True
    if not final_content:
        content_is_valid = False
    elif isinstance(final_content, dict) and 'error' in final_content:
        content_is_valid = False
        final_content = f"# Story Generation Failed: {final_content.get('error', 'Unknown error')}"
    elif isinstance(final_content, str) and final_content.startswith("# Error:"):
        content_is_valid = False
        logging.warning(f"Finalizing story, but content indicates an error state: {final_content[:100]}...")


    if not content_is_valid:
        logging.error("Cannot finalize story - no valid story content available.")
        current_state['final_story_output'] = "# Story Generation Failed"
        return

    # Assign the best available version to the output key
    current_state['final_story_output'] = final_content
    logging.info("Final story prepared for saving.")


# --- Orchestration Logic ---
def generate_story_multi_pass(user_preferences):
    """Orchestrates the multi-pass story generation process using Gemini API."""
    logging.info("\n--- Starting Multi-Pass Story Generation (with Gemini API) ---")
    current_state = user_preferences.copy()

    # Run the passes sequentially
    plan_story_elements(current_state)
    if 'error' in current_state.get('story_plan', {}):
        logging.critical("Story planning failed. Cannot proceed.")
        finalize_story(current_state) # Attempt to finalize with error state
        return current_state

    plot_narrative(current_state)
    if 'error' in current_state.get('story_plot', {}):
        logging.critical("Story plotting failed. Cannot proceed.")
        finalize_story(current_state) # Attempt to finalize with error state
        return current_state

    flesh_out_story(current_state)
    if current_state.get('draft_story', '').startswith("# Error:"):
        logging.critical("Story drafting failed. Cannot proceed with revisions.")
        finalize_story(current_state) # Attempt to finalize with error state
        return current_state

    for i in range(NUM_REVISION_PASSES):
        review_and_revise(current_state, pass_num=i+1)
        # If revision failed, the previous state is kept, so we can continue
        if current_state.get('revised_story', '').startswith("# Error:"):
             logging.warning(f"Revision pass {i+1} failed. Proceeding with previous version.")
             # Ensure 'revised_story' holds the last known good version for the next step
             current_state['revised_story'] = current_state.get('draft_story') if i == 0 else current_state['revised_story']


    add_image_prompts(current_state)
    # Check if adding prompts failed, but don't necessarily stop
    if current_state.get('final_story_with_prompts', '').startswith("# Error:"):
        logging.warning("Adding image prompts failed. Final story will not include prompts.")

    finalize_story(current_state) # Finalize with the best available content

    logging.info("\n--- Multi-Pass Story Generation Finished ---")
    return current_state


def save_story_to_markdown(final_state):
    """Saves the final story to a markdown file."""
    os.makedirs(STORIES_DIR, exist_ok=True)
    char_filename = "".join(c if c.isalnum() else "_" for c in final_state.get('characters', 'MyStory'))[:30]
    filename = f"story_{char_filename}_{timestamp}.md"
    file_path = os.path.join(STORIES_DIR, filename)

    logging.info(f"\nSaving final story to: {file_path}")

    try:
        with open(file_path, "w", encoding="utf-8") as md_file:
            final_story_content = final_state.get('final_story_output', '# Error: Final Story Not Generated')
            if not isinstance(final_story_content, str):
                final_story_content = str(final_story_content)
            md_file.write(final_story_content)
        logging.info("Story saved successfully.")
    except IOError as e:
        logging.error(f"Error writing story file: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during file saving: {e}", exc_info=True)


# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Children's Story Generator (Multi-Pass + Gemini API)...")

    # Check if model was initialized successfully before proceeding
    if not model_initialized:
         logging.critical("Gemini model was not initialized successfully. Please check API key and configuration.")
    else:
        use_defaults_for_testing = False # Set to False to enable interactive prompts
        user_prefs = get_user_input(use_defaults=use_defaults_for_testing)
        final_story_state = generate_story_multi_pass(user_prefs)
        save_story_to_markdown(final_story_state)
        logging.info("\nScript finished.")
        print(f"\nProcess complete. Check '{STORIES_DIR}' for the story and '{LOG_DIR}' for the log file ({log_file_path}).")

