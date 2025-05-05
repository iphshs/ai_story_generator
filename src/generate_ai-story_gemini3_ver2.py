import datetime
import os
import logging
import time # Optional: for slight delay between agent turns

# --- Configuration ---
LOG_DIR = "./log"
STORIES_DIR = "./stories"
N_TURNS = 10 # Number of turns in the agent debate

# --- Logging Setup ---
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIR, f"story_log_{timestamp}.txt")

# Configure logging to write to both file and console
# Ensure handlers are cleared if script is run multiple times in same session (e.g., in notebooks)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', # Keep the format clean for the log file
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'), # Specify encoding
        logging.StreamHandler() # This will print to console
    ]
)

# --- Default User Inputs for Quick Testing ---
DEFAULT_PREFERENCES = {
    "characters": "Pip the adventurous squirrel",
    "setting": "a bustling city park",
    "theme": "curiosity and discovery",
    "genre": "gentle adventure",
    "reading_level": "1",
    "age_appropriate": "4-6",
    "read_aloud_time": "7",
    "other_details": "Include a friendly dog character.",
    "avoid_content": "scary monsters, sadness",
}

# --- User Input Function ---
def get_user_input(use_defaults=False):
    """Collects detailed user preferences for the story."""
    print("\n--- Story Preferences ---")
    logging.info("Collecting user preferences...")

    if use_defaults:
        print("Using default preferences for quick testing.")
        logging.info("Using default preferences.")
        # Initialize story elements and image prompts for defaults
        prefs = DEFAULT_PREFERENCES.copy()
        prefs["story_elements"] = {'scenes': [], 'character_notes': [], 'setting_details': [], 'dialogue': []}
        prefs["image_prompts"] = []
        logging.info(f"Default Preferences: {prefs}")
        return prefs

    # Use descriptive variable names matching the questions
    characters = input(f"1. Who are the main characters? (default: {DEFAULT_PREFERENCES['characters']}): ") or DEFAULT_PREFERENCES['characters']
    setting = input(f"2. What is the primary setting? (default: {DEFAULT_PREFERENCES['setting']}): ") or DEFAULT_PREFERENCES['setting']
    theme = input(f"3. What is the central theme? (default: {DEFAULT_PREFERENCES['theme']}): ") or DEFAULT_PREFERENCES['theme']
    genre = input(f"4. What is the genre? (default: {DEFAULT_PREFERENCES['genre']}): ") or DEFAULT_PREFERENCES['genre']
    reading_level = input(f"5. Target self-reading grade level? (default: {DEFAULT_PREFERENCES['reading_level']}): ") or DEFAULT_PREFERENCES['reading_level']
    age_appropriate = input(f"6. Target age range for listeners? (default: {DEFAULT_PREFERENCES['age_appropriate']}): ") or DEFAULT_PREFERENCES['age_appropriate']
    read_aloud_time = input(f"7. Estimated read-aloud time (minutes)? (default: {DEFAULT_PREFERENCES['read_aloud_time']}): ") or DEFAULT_PREFERENCES['read_aloud_time']
    other_details = input(f"8. Any other specific details or elements to include? (default: {DEFAULT_PREFERENCES['other_details']}): ") or DEFAULT_PREFERENCES['other_details']
    avoid_content = input(f"9. Any specific content, words, or themes to avoid? (default: {DEFAULT_PREFERENCES['avoid_content']}): ") or DEFAULT_PREFERENCES['avoid_content']

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
        "story_elements": {'scenes': [], 'character_notes': [], 'setting_details': [], 'dialogue': []}, # Initialize structured elements
        "image_prompts": [] # Initialize list for image prompts
    }
    logging.info(f"User Preferences Received: {preferences}")
    return preferences

# --- Agent Framework ---

class Agent:
    """Base class for specialized agents."""
    def __init__(self, name):
        self.name = name

    def generate_response(self, current_state, history_summary):
        """
        Generates the agent's contribution based on the current state and history.
        This should be overridden by subclasses.

        Args:
            current_state (dict): The current dictionary holding all story elements and preferences.
            history_summary (str): A distilled summary of relevant past conversation.

        Returns:
            str: The agent's utterance/contribution description.
                 The actual state modification happens within this method.
        """
        raise NotImplementedError("Subclasses must implement generate_response")

    def _create_prompt(self, current_state, history_summary, task_description):
        """Helper to create a detailed prompt for a language model (simulated here)."""
        # Limit the length of the state representation in the prompt if it gets too large
        state_repr = str(current_state)[:1000] + "..." if len(str(current_state)) > 1000 else str(current_state)
        return (
            f"--- Agent: {self.name} ---\n"
            f"Task: {task_description}\n\n"
            f"Relevant History:\n{history_summary}\n\n"
            f"Current Story State (summary):\n{state_repr}\n\n"
            f"{self.name}'s Contribution:"
        )

    def _simulate_llm_call(self, prompt, current_state):
        """
        Simulates a call to a large language model.
        Now correctly uses the passed current_state.

        Args:
            prompt (str): The generated prompt for the LLM.
            current_state (dict): The current state dictionary.

        Returns:
            str: A simulated response based on agent type and current state.
        """
        logging.debug(f"Simulating LLM call for {self.name} with prompt:\n{prompt}") # Log the prompt if needed

        # Basic simulation - refine based on agent type using current_state
        if "Storyteller" in self.name:
            # Simulate adding a scene based on current state
            last_scene_num = len(current_state['story_elements'].get('scenes', []))
            new_scene = f"Scene {last_scene_num + 1}: In the {current_state.get('setting', 'setting')}, {current_state.get('characters', 'characters')} encountered a challenge related to {current_state.get('theme', 'the theme')}."
            current_state['story_elements'].setdefault('scenes', []).append(new_scene)
            return f"Drafted '{new_scene[:50]}...'" # Return description of action
        elif "Character Designer" in self.name:
            note = f"Note: {current_state.get('characters', 'Character')} shows {current_state.get('theme', 'theme-related trait')} when interacting with {current_state.get('other_details', 'others')}."
            current_state['story_elements'].setdefault('character_notes', []).append(note)
            return f"Added character note: '{note[:50]}...'"
        elif "World Builder" in self.name:
            detail = f"Detail: The {current_state.get('setting', 'setting')} has a unique feature: {current_state.get('genre', 'genre-specific element')}."
            current_state['story_elements'].setdefault('setting_details', []).append(detail)
            return f"Added setting detail: '{detail[:50]}...'"
        elif "Dialog Coach" in self.name:
            dialogue = f"Dialogue: '{current_state.get('characters', 'Char1')} said something simple and engaging fitting age {current_state.get('age_appropriate', 'range')}.'"
            current_state['story_elements'].setdefault('dialogue', []).append(dialogue)
            return f"Crafted dialogue snippet: '{dialogue[:50]}...'"
        elif "Children Linguist" in self.name:
            # Simulate checking language - doesn't modify state directly here
            return f"Reviewed language for grade {current_state.get('reading_level', 'level')} and flow. Avoided: '{current_state.get('avoid_content', 'none')}'. Looks okay."
        elif "Conceptual Illustrator" in self.name:
            # Generate prompt based on the *last added scene* if available
            last_scene = current_state['story_elements'].get('scenes', [])[-1] if current_state['story_elements'].get('scenes') else "a key moment"
            image_prompt = f"[IMAGE: A {current_state.get('genre','gentle')} style illustration for age {current_state.get('age_appropriate')}: {last_scene}]"
            current_state.setdefault('image_prompts', []).append(image_prompt)
            return f"Suggested image prompt: '{image_prompt[:60]}...'"
        elif "Visual Design Editor" in self.name:
            # Simulate reviewing prompts - doesn't modify state directly here
            prompt_count = len(current_state.get('image_prompts', []))
            return f"Reviewed {prompt_count} image prompts for consistency and appeal."
        elif "Final Preprint Editor" in self.name:
            # --- Simulation of Final Story Assembly ---
            story_parts = []
            story_parts.append(f"# Story: The Tale of {current_state.get('characters', 'Our Heroes')}\n")
            story_parts.append(f"**Theme:** {current_state.get('theme', 'A valuable lesson')}")
            story_parts.append(f"**Genre:** {current_state.get('genre', 'An exciting tale')}\n")

            # Weave in elements - very basic weaving for simulation
            elements = current_state.get('story_elements', {})
            prompts = current_state.get('image_prompts', [])
            prompt_idx = 0

            # Add opening scene / description
            if elements.get('setting_details'):
                 story_parts.append(elements['setting_details'][0]) # Add first setting detail
            if elements.get('character_notes'):
                 story_parts.append(elements['character_notes'][0]) # Add first character note

            # Add scenes and prompts
            scenes = elements.get('scenes', ['Once upon a time...'])
            dialogues = elements.get('dialogue', [])
            dialogue_idx = 0
            for i, scene in enumerate(scenes):
                story_parts.append(scene)
                # Add a prompt roughly every other scene (adjust logic as needed)
                if i % 2 == 0 and prompt_idx < len(prompts):
                    story_parts.append(f"\n{prompts[prompt_idx]}\n")
                    prompt_idx += 1
                # Add dialogue snippets intermittently
                if i % 2 != 0 and dialogue_idx < len(dialogues):
                    story_parts.append(dialogues[dialogue_idx])
                    dialogue_idx +=1


            # Add remaining prompts if any
            while prompt_idx < len(prompts):
                 story_parts.append(f"\n{prompts[prompt_idx]}\n")
                 prompt_idx += 1

            story_parts.append("The End.")
            final_story_text = "\n\n".join(story_parts)
            current_state['final_story'] = final_story_text
            # --- End Simulation ---
            return "Compiled final story from elements, added prompts, and performed final review."
        else:
            return f"Agent {self.name} contributing..."

# --- Specific Agent Implementations ---
# These now primarily define the task and call the simulation,
# which handles basic state updates.

class StorytellerAgent(Agent):
    def generate_response(self, current_state, history_summary):
        scene_count = len(current_state['story_elements'].get('scenes', []))
        if scene_count == 0:
            task = f"Draft the **opening scene** of the story in the {current_state.get('setting')}, introducing {current_state.get('characters')}. Hint at the theme ({current_state.get('theme')}). Aim for a {current_state.get('genre')} feel and reading level {current_state.get('reading_level')}."
        elif scene_count < 3: # Example: Add middle parts
             task = f"Draft the **next part** of the story, developing the plot and incorporating the theme ({current_state.get('theme')}). Consider recent dialogue or character notes."
        else: # Example: Add concluding part
            task = f"Draft the **concluding part** of the story, resolving the main challenge and reinforcing the theme ({current_state.get('theme')})."

        prompt = self._create_prompt(current_state, history_summary, task)
        # The simulation call now updates the state
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc # Return description of what was done

class CharacterDesignerAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Add a specific detail or trait to {current_state.get('characters')} based on their actions so far or related to the theme ({current_state.get('theme')}). Consider {current_state.get('other_details')}."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc

class WorldBuilderAgent(Agent):
     def generate_response(self, current_state, history_summary):
        task = f"Add a vivid sensory detail or interesting feature to the {current_state.get('setting')} that enhances the {current_state.get('genre')} atmosphere or relates to the current scene."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc

class DialogCoachAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Write a short, engaging dialogue exchange between characters relevant to the current scene. Ensure it sounds natural for the {current_state.get('age_appropriate')} age range and moves the plot slightly."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc

class ChildrenLinguistAgent(Agent):
    def generate_response(self, current_state, history_summary):
        # This agent primarily reviews, simulation reflects this
        task = f"Review the story text generated so far (scenes, dialogue) for language complexity (target grade {current_state.get('reading_level')}), flow, rhythm, and age-appropriateness ({current_state.get('age_appropriate')}). Flag any potential issues or violations of avoidance criteria: {current_state.get('avoid_content')}."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc # Describes the review action

class ConceptualIllustratorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = "Generate a text-to-image prompt for the most recently added story scene. The style should match the genre and age group. Ensure it visually represents the scene's content."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc # Describes the prompt generation

class VisualDesignEditorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        # This agent primarily reviews
        task = "Review all generated image prompts. Check for clarity, consistency with the story's tone and visual style, age appropriateness, and feasibility. Suggest improvements if needed (simulation just acknowledges review)."
        prompt = self._create_prompt(current_state, history_summary, task)
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc # Describes the review action

class FinalPreprintEditorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"""
        Assemble the final story narrative using all generated elements from 'story_elements' (scenes, character notes, setting details, dialogue).
        Ensure a logical flow: beginning, middle, end.
        Integrate the generated 'image_prompts' at appropriate points within the narrative.
        Perform a final check for overall coherence, consistent tone, theme ({current_state.get('theme')}), age appropriateness ({current_state.get('age_appropriate')}), reading level ({current_state.get('reading_level')}), and ensure content to avoid ('{current_state.get('avoid_content')}') is excluded.
        Format the final story clearly in Markdown.
        """
        prompt = self._create_prompt(current_state, history_summary, task)
        # Simulation performs the assembly and stores in current_state['final_story']
        response_desc = self._simulate_llm_call(prompt, current_state)
        return response_desc # Describes the final editing action


# --- Orchestration Logic ---

def run_agent_pipeline(user_preferences):
    """Manages the multi-agent debate/pipeline."""
    logging.info("\n--- Starting Agent Pipeline ---")

    # Define the sequence of agents for the pipeline
    # More turns allow for more refinement and detail
    agents = [
        StorytellerAgent("Storyteller - Opening"),
        CharacterDesignerAgent("Character Designer"),
        WorldBuilderAgent("World Builder"),
        ConceptualIllustratorAgent("Conceptual Illustrator 1"),
        DialogCoachAgent("Dialog Coach 1"),
        ChildrenLinguistAgent("Children Linguist Review 1"),
        StorytellerAgent("Storyteller - Middle"),
        ConceptualIllustratorAgent("Conceptual Illustrator 2"),
        DialogCoachAgent("Dialog Coach 2"),
        VisualDesignEditorAgent("Visual Design Editor"), # Review prompts before final story
        # Add more turns for refinement if N_TURNS is higher
        # e.g., another Storyteller, Linguist review, etc.
        FinalPreprintEditorAgent("Final Preprint Editor") # Always last
    ]

    current_state = user_preferences.copy() # Start with user prefs
    conversation_history = []

    num_pipeline_steps = len(agents)
    actual_turns = min(N_TURNS, num_pipeline_steps) # Use N_TURNS or length of defined pipeline

    logging.info(f"Running pipeline for {actual_turns} turns.")

    for i in range(actual_turns):
        # Ensure the final editor is always the last step if N_TURNS >= num_pipeline_steps
        if N_TURNS >= num_pipeline_steps and i == actual_turns - 1:
            agent = agents[-1] # Force the last defined agent (Final Editor)
        else:
             agent = agents[i]

        logging.info(f"\n--- Turn {i+1}/{actual_turns} | Agent: {agent.name} ---")

        # Create a distilled summary of the last few turns (e.g., last 3-4)
        history_summary = "\n".join(conversation_history[-4:]) if conversation_history else "No previous discussion yet."

        # Agent performs its action (which now modifies current_state)
        try:
            response_description = agent.generate_response(current_state, history_summary)
            agent_utterance = f"**{agent.name}:** {response_description}" # Log the description of the action
            logging.info(agent_utterance)
            conversation_history.append(agent_utterance) # Log the description
            # Log state change summary (optional, can be verbose)
            # logging.debug(f"State after turn {i+1}: {current_state}")
        except Exception as e:
            logging.error(f"Error during agent {agent.name} turn: {e}", exc_info=True) # Log traceback
            # Decide whether to continue or stop
            logging.warning("Continuing pipeline after error.")
            continue # Continue to the next agent

        # Optional delay
        # time.sleep(0.5)

    logging.info("\n--- Agent Pipeline Finished ---")

    # Final check if story exists, create fallback if editor failed silently
    if 'final_story' not in current_state or not current_state['final_story']:
         logging.warning("Final story not found or empty in state after pipeline. Attempting fallback assembly.")
         # Basic fallback: concatenate available elements
         fallback_parts = [f"# Fallback Story for {current_state.get('characters', 'Character')}\n"]
         elements = current_state.get('story_elements', {})
         prompts = current_state.get('image_prompts', [])
         fallback_parts.extend(elements.get('scenes', ["Once upon a time..."]))
         fallback_parts.extend(elements.get('dialogue', []))
         fallback_parts.extend(prompts)
         fallback_parts.append("\n(Fallback Assembly) The End.")
         current_state['final_story'] = "\n\n".join(fallback_parts)
         logging.info("Fallback story generated.")

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
            final_story_content = final_state.get('final_story', '# Error: Story Not Generated')
            md_file.write(final_story_content)
        logging.info("Story saved successfully.")
    except IOError as e:
        logging.error(f"Error writing story file: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during file saving: {e}", exc_info=True)


# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Children's Story Generator...")
    # Set use_defaults=True for quick testing without prompts
    use_defaults_for_testing = True # <--- Set to False to enter details manually
    user_prefs = get_user_input(use_defaults=use_defaults_for_testing)
    final_story_state = run_agent_pipeline(user_prefs)
    save_story_to_markdown(final_story_state)
    logging.info("\nScript finished.")
    print(f"\nProcess complete. Check '{STORIES_DIR}' for the story and '{LOG_DIR}' for the log file ({log_file_path}).")
