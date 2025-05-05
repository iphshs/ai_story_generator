import datetime
import os
import logging
import time
import json # For potentially structured LLM responses

# --- Configuration ---
LOG_DIR = "./log"
STORIES_DIR = "./stories"
NUM_REVISION_PASSES = 1 # How many times to run the review/revise pass

# --- Logging Setup ---
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIR, f"story_log_{timestamp}.txt")

# Configure logging to write to both file and console
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', # Added timestamp and level
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
# Reduce console noise for basic info, show debug in file?
# Or use different loggers? For now, keep INFO for both.

# --- Default User Inputs for Quick Testing ---
DEFAULT_PREFERENCES = {
    "characters": "Leo the lion cub and Sky the wise old owl",
    "setting": "the Whispering Savannah at twilight",
    "theme": "overcoming fear of the dark",
    "genre": "gentle adventure / bedtime story",
    "reading_level": "K",
    "age_appropriate": "3-5",
    "read_aloud_time": "5",
    "other_details": "Include twinkling stars and friendly fireflies.",
    "avoid_content": "predators, danger, complex words",
}

# --- User Input Function ---
def get_user_input(use_defaults=False):
    """Collects detailed user preferences for the story."""
    print("\n--- Story Preferences ---")
    logging.info("Collecting user preferences...")

    if use_defaults:
        print("Using default preferences for quick testing.")
        logging.info("Using default preferences.")
        prefs = DEFAULT_PREFERENCES.copy()
        # Initialize structured state for story generation passes
        prefs["story_plan"] = {}
        prefs["story_plot"] = {}
        prefs["draft_story"] = ""
        prefs["revised_story"] = ""
        prefs["final_story_with_prompts"] = ""
        prefs["image_prompts"] = [] # Keep separate list as well
        logging.info(f"Default Preferences Loaded: {prefs}")
        return prefs

    # Collect input or use defaults
    characters = input(f"1. Characters? (default: {DEFAULT_PREFERENCES['characters']}): ") or DEFAULT_PREFERENCES['characters']
    setting = input(f"2. Setting? (default: {DEFAULT_PREFERENCES['setting']}): ") or DEFAULT_PREFERENCES['setting']
    theme = input(f"3. Theme? (default: {DEFAULT_PREFERENCES['theme']}): ") or DEFAULT_PREFERENCES['theme']
    genre = input(f"4. Genre? (default: {DEFAULT_PREFERENCES['genre']}): ") or DEFAULT_PREFERENCES['genre']
    reading_level = input(f"5. Reading Level? (default: {DEFAULT_PREFERENCES['reading_level']}): ") or DEFAULT_PREFERENCES['reading_level']
    age_appropriate = input(f"6. Age Range? (default: {DEFAULT_PREFERENCES['age_appropriate']}): ") or DEFAULT_PREFERENCES['age_appropriate']
    read_aloud_time = input(f"7. Read Time (min)? (default: {DEFAULT_PREFERENCES['read_aloud_time']}): ") or DEFAULT_PREFERENCES['read_aloud_time']
    other_details = input(f"8. Other Details? (default: {DEFAULT_PREFERENCES['other_details']}): ") or DEFAULT_PREFERENCES['other_details']
    avoid_content = input(f"9. Avoid Content? (default: {DEFAULT_PREFERENCES['avoid_content']}): ") or DEFAULT_PREFERENCES['avoid_content']

    preferences = {
        "characters": characters,
        "setting": setting,
        "theme": theme,
        "genre": genre,
        "reading_level": reading_level,
        "age_appropriate": age_appropriate,
        "read_aloud_time": read_aloud_time,
        "other_details": other_details,
        "avoid_content": avoid_content,
        # Initialize state holders
        "story_plan": {},
        "story_plot": {},
        "draft_story": "",
        "revised_story": "",
        "final_story_with_prompts": "",
        "image_prompts": []
    }
    logging.info(f"User Preferences Received: {preferences}")
    return preferences

# --- Simulated LLM Call ---
def simulate_gemini_call(prompt, task_description):
    """
    Simulates a call to a generative AI model (like Gemini).
    Logs the prompt and a simulated response based on the task.
    """
    logging.info(f"\n--- Simulating Gemini Call: {task_description} ---")
    logging.info(f"PROMPT:\n------\n{prompt}\n------")

    # Simulate response based on task description
    simulated_response = f"Simulated Gemini Response for '{task_description}':\n"
    if "Plan Story Elements" in task_description:
        simulated_response += json.dumps({
            "detailed_characters": "Leo: curious but timid lion cub. Sky: patient, knowledgeable owl.",
            "setting_details": "Savannah with soft grass, acacia trees, visible constellations.",
            "key_plot_points": ["Leo is scared of shadows", "Sky offers guidance", "They explore together", "Leo sees beauty in the night", "Leo feels brave"],
            "extra_elements": ["Friendly fireflies guide the way", "Stars twinkle reassuringly"]
        }, indent=2)
    elif "Plot Narrative Outline" in task_description:
        simulated_response += json.dumps({
            "title_suggestion": "Leo's Night Adventure",
            "logline": "A timid lion cub, guided by a wise owl, learns not to fear the dark savannah night.",
            "outline": {
                "beginning": "Leo hides as twilight falls, expressing fear. Sky introduces herself gently.",
                "rising_action": "Sky encourages Leo to explore. They observe nocturnal animals and fireflies. Leo shares his specific fears (shadows, noises).",
                "climax": "A sudden noise startles Leo. Sky helps him identify it (rustling leaves) and points out the beautiful stars.",
                "falling_action": "Leo looks at the stars, feeling calmer. He notices the fireflies' gentle light.",
                "resolution": "Leo thanks Sky, feeling brave and no longer scared. He curls up to sleep under the stars."
            }
        }, indent=2)
    elif "Flesh Out Story" in task_description:
        simulated_response += (
            "Okay, here is the story draft:\n\n"
            "Leo the lion cub shivered as the sun dipped low, painting the Whispering Savannah in shades of orange and purple. Long shadows stretched from the acacia trees, looking like spooky monsters to little Leo. 'Oh dear,' he whispered, tucking his head under his paws.\n\n"
            "Suddenly, a soft 'Hoo-hoo?' came from above. Leo peeked out and saw Sky, a kind owl with big, round eyes, perched on a branch. 'What troubles you, little one?' she asked gently.\n\n"
            "'The dark! It's full of scary shapes,' Leo whimpered.\n\n"
            "Sky hooted softly. 'The night has its own beauty, Leo. Come, let's see.' Tentatively, Leo followed Sky. Tiny fireflies blinked around them like floating jewels. 'Wow,' Leo breathed. But then, a leaf rustled loudly! Leo jumped. 'It's just the wind, little lion,' Sky explained patiently. She pointed her wing upwards. 'Look!'\n\n"
            "Above them, the sky was filled with twinkling stars, like diamonds scattered on dark velvet. Leo stared, forgetting his fear. The night wasn't scary; it was beautiful and peaceful.\n\n"
            "'Thank you, Sky,' Leo yawned, feeling brave now. He found a soft patch of grass and curled up, watching the stars until he drifted off to sleep."
        )
    elif "Review and Revise" in task_description:
        simulated_response += (
            "Review Feedback:\n"
            "- Coherence: Good flow from fear to bravery.\n"
            "- Characters: Consistent. Leo's fear and Sky's wisdom come through.\n"
            "- Theme: 'Overcoming fear' is clear.\n"
            "- Language: Simple, suitable for K/3-5 yrs. Avoided complex words.\n"
            "- Suggestions: Maybe add one more sensory detail (e.g., smell of night flowers) during the exploration.\n\n"
            "Revised Draft (incorporating suggestion):\n\n"
            "Leo the lion cub shivered as the sun dipped low, painting the Whispering Savannah in shades of orange and purple. Long shadows stretched from the acacia trees, looking like spooky monsters to little Leo. 'Oh dear,' he whispered, tucking his head under his paws.\n\n"
            "Suddenly, a soft 'Hoo-hoo?' came from above. Leo peeked out and saw Sky, a kind owl with big, round eyes, perched on a branch. 'What troubles you, little one?' she asked gently.\n\n"
            "'The dark! It's full of scary shapes,' Leo whimpered.\n\n"
            "Sky hooted softly. 'The night has its own beauty, Leo. Come, let's see.' Tentatively, Leo followed Sky. Tiny fireflies blinked around them like floating jewels. The sweet scent of night flowers filled the air. 'Wow,' Leo breathed. But then, a leaf rustled loudly! Leo jumped. 'It's just the wind, little lion,' Sky explained patiently. She pointed her wing upwards. 'Look!'\n\n"
            "Above them, the sky was filled with twinkling stars, like diamonds scattered on dark velvet. Leo stared, forgetting his fear. The night wasn't scary; it was beautiful and peaceful.\n\n"
            "'Thank you, Sky,' Leo yawned, feeling brave now. He found a soft patch of grass and curled up, watching the stars until he drifted off to sleep."
        )
    elif "Add Image Prompts" in task_description:
        # Simulate adding prompts into the *revised* story text
        # In a real scenario, the LLM would receive the text and return it with prompts inserted.
        # Here, we manually insert based on the revised text simulation.
        revised_text = ( # Re-paste the revised text from the simulation above
            "Leo the lion cub shivered as the sun dipped low, painting the Whispering Savannah in shades of orange and purple. Long shadows stretched from the acacia trees, looking like spooky monsters to little Leo. 'Oh dear,' he whispered, tucking his head under his paws.\n\n"
            "[IMAGE: Cute lion cub looking scared as long shadows stretch across a colorful twilight savannah. Style: gentle, warm illustration for ages 3-5.]\n\n"
            "Suddenly, a soft 'Hoo-hoo?' came from above. Leo peeked out and saw Sky, a kind owl with big, round eyes, perched on a branch. 'What troubles you, little one?' she asked gently.\n\n"
            "'The dark! It's full of scary shapes,' Leo whimpered.\n\n"
            "Sky hooted softly. 'The night has its own beauty, Leo. Come, let's see.' Tentatively, Leo followed Sky. Tiny fireflies blinked around them like floating jewels. The sweet scent of night flowers filled the air. 'Wow,' Leo breathed. But then, a leaf rustled loudly! Leo jumped. 'It's just the wind, little lion,' Sky explained patiently. She pointed her wing upwards. 'Look!'\n\n"
            "[IMAGE: Wise, friendly owl and timid lion cub looking up at a sky full of bright stars and fireflies over the savannah. Style: gentle, magical night illustration for ages 3-5.]\n\n"
            "Above them, the sky was filled with twinkling stars, like diamonds scattered on dark velvet. Leo stared, forgetting his fear. The night wasn't scary; it was beautiful and peaceful.\n\n"
            "'Thank you, Sky,' Leo yawned, feeling brave now. He found a soft patch of grass and curled up, watching the stars until he drifted off to sleep.\n\n"
            "[IMAGE: Contented lion cub sleeping peacefully under a starry night sky on the savannah. Style: gentle, serene bedtime illustration for ages 3-5.]"
        )
        simulated_response += "Inserted 3 image prompts into the story:\n\n" + revised_text
    else:
        simulated_response += "Placeholder response for unrecognized task."

    logging.info(f"SIMULATED RESPONSE:\n-------------------\n{simulated_response}\n-------------------")
    # time.sleep(1) # Optional delay
    return simulated_response

# --- Story Generation Passes ---

def plan_story_elements(current_state):
    """Pass 1: Plan key story elements."""
    logging.info("=== PASS 1: Planning Story Elements ===")
    prompt = f"""
    Based on the following user preferences for a children's story, outline the key elements:

    Preferences:
    - Characters: {current_state['characters']}
    - Setting: {current_state['setting']}
    - Theme: {current_state['theme']}
    - Genre: {current_state['genre']}
    - Age Appropriate: {current_state['age_appropriate']}
    - Other Details: {current_state['other_details']}
    - Avoid Content: {current_state['avoid_content']}

    Provide a structured response (e.g., JSON) with:
    - detailed_characters: Brief descriptions focusing on traits relevant to the theme.
    - setting_details: Specific sensory details or features of the setting.
    - key_plot_points: 3-5 bullet points outlining the core story progression.
    - extra_elements: Mention how 'other_details' can be woven in.
    """
    response = simulate_gemini_call(prompt, "Plan Story Elements")
    # Attempt to parse the simulated JSON response
    try:
        # Extract the JSON part of the response
        json_str = response.split(':', 1)[1].strip()
        current_state['story_plan'] = json.loads(json_str)
        logging.info("Successfully parsed story plan.")
    except (json.JSONDecodeError, IndexError, Exception) as e:
        logging.error(f"Failed to parse story plan JSON from simulated response: {e}")
        # Add fallback or default plan elements if parsing fails
        current_state['story_plan'] = {"error": "Failed to parse plan", "raw_response": response}

def plot_narrative(current_state):
    """Pass 2: Create a structured plot outline."""
    logging.info("=== PASS 2: Plotting Narrative Outline ===")
    if not current_state.get('story_plan') or 'error' in current_state.get('story_plan', {}):
        logging.warning("Skipping plot narrative due to missing or failed previous step.")
        return

    prompt = f"""
    Using the story plan below, create a structured narrative plot outline for a children's story ({current_state['genre']}, age {current_state['age_appropriate']}).

    Story Plan:
    {json.dumps(current_state['story_plan'], indent=2)}

    User Preferences Summary:
    - Theme: {current_state['theme']}
    - Characters: {current_state['characters']}
    - Setting: {current_state['setting']}
    - Read Aloud Time: ~{current_state['read_aloud_time']} mins

    Provide a structured response (e.g., JSON) with:
    - title_suggestion: A suitable title.
    - logline: A one-sentence summary.
    - outline: A dictionary with keys 'beginning', 'rising_action', 'climax', 'falling_action', 'resolution', each containing a brief description of that plot stage.
    """
    response = simulate_gemini_call(prompt, "Plot Narrative Outline")
    try:
        json_str = response.split(':', 1)[1].strip()
        current_state['story_plot'] = json.loads(json_str)
        logging.info("Successfully parsed story plot.")
    except (json.JSONDecodeError, IndexError, Exception) as e:
        logging.error(f"Failed to parse story plot JSON from simulated response: {e}")
        current_state['story_plot'] = {"error": "Failed to parse plot", "raw_response": response}

def flesh_out_story(current_state):
    """Pass 3: Write the full story draft."""
    logging.info("=== PASS 3: Fleshing Out Story Draft ===")
    if not current_state.get('story_plot') or 'error' in current_state.get('story_plot', {}):
        logging.warning("Skipping story draft due to missing or failed previous step.")
        return

    prompt = f"""
    Write the full text for a children's story based on the plot outline and elements below.

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

    Write the story clearly and engagingly for young children.
    """
    response = simulate_gemini_call(prompt, "Flesh Out Story")
    # Extract the story text part of the response
    try:
        story_text = response.split("Okay, here is the story draft:\n\n", 1)[1].strip()
        current_state['draft_story'] = story_text
        logging.info("Successfully extracted draft story text.")
    except (IndexError, Exception) as e:
         logging.error(f"Failed to extract draft story text from response: {e}")
         current_state['draft_story'] = f"Error extracting draft: {response}" # Store raw response on error

def review_and_revise(current_state, pass_num):
    """Pass 4 (and potentially more): Review and revise the draft."""
    logging.info(f"=== PASS 4.{pass_num}: Reviewing and Revising Story ===")
    story_to_review = current_state.get('revised_story') or current_state.get('draft_story') # Use latest version
    if not story_to_review or "Error" in story_to_review:
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

    Provide feedback and a revised version of the story addressing any issues found.

    Draft to Review:
    ---
    {story_to_review}
    ---
    """
    response = simulate_gemini_call(prompt, f"Review and Revise Pass {pass_num}")
    # Extract the revised story part
    try:
        revised_text = response.split("Revised Draft (incorporating suggestion):\n\n", 1)[1].strip()
        current_state['revised_story'] = revised_text
        logging.info("Successfully extracted revised story text.")
    except (IndexError, Exception) as e:
         logging.error(f"Failed to extract revised story text from response: {e}")
         # Keep the previous version if extraction fails
         logging.warning("Keeping previous story version as revision extraction failed.")
         if not current_state.get('revised_story'): # Only if it wasn't already set
             current_state['revised_story'] = story_to_review


def add_image_prompts(current_state):
    """Pass 5: Identify key scenes and add image prompts."""
    logging.info("=== PASS 5: Adding Image Prompts ===")
    story_to_illustrate = current_state.get('revised_story') or current_state.get('draft_story')
    if not story_to_illustrate or "Error" in story_to_illustrate:
        logging.warning("Skipping image prompt addition due to missing or invalid story.")
        return

    prompt = f"""
    Read the following children's story ({current_state['genre']}, age {current_state['age_appropriate']}).
    Identify 3 key scenes that would benefit from an illustration (beginning, middle, end if possible).
    Insert text-to-image prompts directly into the story text at appropriate locations.
    The prompts should be enclosed in square brackets, like [IMAGE: description].
    The description should be concise but evocative, specifying the style (e.g., gentle illustration, cartoonish, watercolor) and key elements of the scene relevant to the story and age group.

    Story Text:
    ---
    {story_to_illustrate}
    ---

    Return the complete story text with the prompts inserted.
    """
    response = simulate_gemini_call(prompt, "Add Image Prompts")
    # Extract the story with prompts
    try:
        story_with_prompts = response.split("Inserted 3 image prompts into the story:\n\n", 1)[1].strip()
        current_state['final_story_with_prompts'] = story_with_prompts
        # Also extract prompts separately if needed
        current_state['image_prompts'] = [line for line in story_with_prompts.split('\n') if line.strip().startswith("[IMAGE:")]
        logging.info(f"Successfully extracted story with {len(current_state['image_prompts'])} image prompts.")
    except (IndexError, Exception) as e:
         logging.error(f"Failed to extract story with image prompts from response: {e}")
         current_state['final_story_with_prompts'] = f"Error adding prompts: {story_to_illustrate}" # Fallback

def finalize_story(current_state):
    """Pass 6: Final check and preparation for output."""
    logging.info("=== PASS 6: Finalizing Story ===")
    if not current_state.get('final_story_with_prompts') or "Error" in current_state.get('final_story_with_prompts'):
        logging.error("Cannot finalize story - final version with prompts is missing or invalid.")
        # Attempt to use the best available version as fallback
        final_content = current_state.get('revised_story') or current_state.get('draft_story') or "# Story Generation Failed"
        current_state['final_story_output'] = final_content
        return

    # In a real scenario, might do final grammar/spell check here
    # For simulation, we just assign the version with prompts to the output key
    current_state['final_story_output'] = current_state['final_story_with_prompts']
    logging.info("Final story prepared for saving.")


# --- Orchestration Logic ---
def generate_story_multi_pass(user_preferences):
    """Orchestrates the multi-pass story generation process."""
    logging.info("\n--- Starting Multi-Pass Story Generation ---")
    current_state = user_preferences.copy()

    # Run the passes sequentially
    plan_story_elements(current_state)
    plot_narrative(current_state)
    flesh_out_story(current_state)

    for i in range(NUM_REVISION_PASSES):
        review_and_revise(current_state, pass_num=i+1)

    add_image_prompts(current_state)
    finalize_story(current_state)

    logging.info("\n--- Multi-Pass Story Generation Finished ---")
    return current_state


def save_story_to_markdown(final_state):
    """Saves the final story to a markdown file."""
    os.makedirs(STORIES_DIR, exist_ok=True)
    # Sanitize characters string for filename
    char_filename = "".join(c if c.isalnum() else "_" for c in final_state.get('characters', 'MyStory'))[:30]
    filename = f"story_{char_filename}_{timestamp}.md"
    file_path = os.path.join(STORIES_DIR, filename)

    logging.info(f"\nSaving final story to: {file_path}")

    try:
        with open(file_path, "w", encoding="utf-8") as md_file:
            # Use the dedicated output key from the finalize step
            final_story_content = final_state.get('final_story_output', '# Error: Final Story Not Generated')
            # Ensure content is string before writing
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
    logging.info("Starting Children's Story Generator (Multi-Pass Version)...")
    # Set use_defaults=True for quick testing without prompts
    use_defaults_for_testing = True # <--- Set to False to enter details manually
    user_prefs = get_user_input(use_defaults=use_defaults_for_testing)
    final_story_state = generate_story_multi_pass(user_prefs)
    save_story_to_markdown(final_story_state)
    logging.info("\nScript finished.")
    print(f"\nProcess complete. Check '{STORIES_DIR}' for the story and '{LOG_DIR}' for the log file ({log_file_path}).")

