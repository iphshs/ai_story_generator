import datetime
import os
import logging

# --- Configuration ---
LOG_DIR = "./log"
STORIES_DIR = "./stories"
N_TURNS = 10 # Number of turns in the agent debate

# --- Logging Setup ---
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(LOG_DIR, f"story_log_{timestamp}.txt")

# Configure logging to write to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', # Keep the format clean for the log file
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler() # This will print to console
    ]
)

# --- User Input Function ---
def get_user_input():
    """Collects detailed user preferences for the story."""
    print("\n--- Story Preferences ---")
    logging.info("Collecting user preferences...") # Log start of input collection

    # Use descriptive variable names matching the questions
    characters = input("1. Who are the main characters? (e.g., a clever raccoon, young girl, a superhero): ")
    setting = input("2. What is the primary setting? (e.g., a school, enchanted forest, space): ")
    theme = input("3. What is the central theme? (e.g., honesty, friendship, courage): ")
    genre = input("4. What is the genre? (e.g., adventure, mystery, fantasy, sci-fi): ")
    reading_level = input("5. Target self-reading grade level? (e.g., K, 1, 3): ")
    age_appropriate = input("6. Target age range for listeners? (e.g., 3-5, 6-8): ")
    read_aloud_time = input("7. Estimated read-aloud time (minutes)? (e.g., 5, 10, 20): ")
    other_details = input("8. Any other specific details or elements to include? ")
    avoid_content = input("9. Any specific content, words, or themes to avoid? ")

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
        "story_elements": {}, # Initialize a dict to hold generated story parts
        "image_prompts": [] # Initialize a list for image prompts
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
            str: The agent's utterance/contribution.
        """
        raise NotImplementedError("Subclasses must implement generate_response")

    def _create_prompt(self, current_state, history_summary, task_description):
        """Helper to create a detailed prompt for a language model (simulated here)."""
        return (
            f"--- Agent: {self.name} ---\n"
            f"Task: {task_description}\n\n"
            f"Relevant History:\n{history_summary}\n\n"
            f"Current Story State:\n{current_state}\n\n"
            f"{self.name}'s Contribution:"
        )

    def _simulate_llm_call(self, prompt):
        """
        Simulates a call to a large language model.
        In a real application, this would involve API calls (e.g., to Gemini).
        For this script, it returns a placeholder based on the agent type.
        """
        # Basic simulation - refine based on agent type
        if "Storyteller" in self.name:
            return f"Okay, let's start the story in the {current_state.get('setting', 'specified setting')} with {current_state.get('characters', 'the characters')}..."
        elif "Character Designer" in self.name:
            return f"Adding details to {current_state.get('characters', 'the characters')}, focusing on traits related to {current_state.get('theme', 'the theme')}."
        elif "World Builder" in self.name:
            return f"Elaborating on the {current_state.get('setting', 'setting')} to enhance the {current_state.get('genre', 'genre')} feel."
        elif "Dialog Coach" in self.name:
            return f"Crafting some simple, engaging dialogue suitable for {current_state.get('age_appropriate', 'the target age')}."
        elif "Children Linguist" in self.name:
            return f"Checking the language for flow, rhyme (if applicable), and age-appropriateness ({current_state.get('reading_level', 'target level')})."
        elif "Conceptual Illustrator" in self.name:
            scene_desc = current_state.get('story_elements', {}).get('last_scene', 'a key moment')
            return f"Suggesting image prompt for {scene_desc}: [IMAGE: A simple, clear illustration of {scene_desc}, {current_state.get('genre', 'genre')} style.]"
        elif "Visual Design Editor" in self.name:
            return "Reviewing image prompts for consistency and appeal."
        elif "Final Preprint Editor" in self.name:
            return "Compiling all elements into a cohesive story, ensuring logical flow (beginning, middle, end) and checking against avoidance criteria."
        else:
            return f"Agent {self.name} contributing..."

# --- Specific Agent Implementations (Simplified) ---

class StorytellerAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Draft the next part of the story, incorporating characters, setting, and theme ({current_state.get('theme')}). Aim for a {current_state.get('genre')} feel and reading level {current_state.get('reading_level')}."
        prompt = self._create_prompt(current_state, history_summary, task)
        # Simulate adding a story segment
        response = self._simulate_llm_call(prompt) # Placeholder response
        # In a real scenario, parse LLM output to update current_state['story_elements']
        current_state['story_elements']['last_scene'] = f"the beginning in {current_state.get('setting')}" # Example update
        return response + f"\n[Adding opening scene to story_elements]"

class CharacterDesignerAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Flesh out the characters ({current_state.get('characters')}) with personalities and motivations relevant to the theme ({current_state.get('theme')})."
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt)
        # Update current_state['story_elements']['character_notes']
        return response + "\n[Adding character notes to story_elements]"

class WorldBuilderAgent(Agent):
     def generate_response(self, current_state, history_summary):
        task = f"Add descriptive details to the setting ({current_state.get('setting')}) to make it more vivid and align with the {current_state.get('genre')} genre."
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt)
        # Update current_state['story_elements']['setting_details']
        return response + "\n[Adding setting details to story_elements]"

class DialogCoachAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Write a short dialogue exchange between characters that fits the {current_state.get('age_appropriate')} age range and moves the plot forward."
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt)
        # Update current_state['story_elements']['dialogue_snippets']
        return response + "\n[Adding dialogue snippet to story_elements]"

class ChildrenLinguistAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"Review the current text for language complexity (target grade {current_state.get('reading_level')}), flow, rhythm, and age-appropriateness ({current_state.get('age_appropriate')}). Check against content to avoid: {current_state.get('avoid_content')}."
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt)
        # Potentially suggest revisions or flag issues
        return response + "\n[Performing linguistic review]"

class ConceptualIllustratorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = "Generate a text-to-image prompt for a key scene described recently in the story elements. The style should match the genre and age group."
        prompt = self._create_prompt(current_state, history_summary, task)
        # Simulate generating a prompt and adding it
        simulated_prompt_text = f"[IMAGE: A {current_state.get('genre','colorful')} illustration of {current_state.get('story_elements',{}).get('last_scene', 'a scene')} featuring {current_state.get('characters', 'characters')}, suitable for {current_state.get('age_appropriate')} year olds.]"
        current_state['image_prompts'].append(simulated_prompt_text)
        response = self._simulate_llm_call(prompt) # Base simulation
        return f"Suggested Prompt: {simulated_prompt_text}" # Return the actual prompt generated

class VisualDesignEditorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = "Review the generated image prompts for clarity, consistency with the story's tone, visual appeal for the target age, and feasibility."
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt)
        # Could potentially modify prompts in current_state['image_prompts']
        return response + "\n[Reviewing visual prompts]"

class FinalPreprintEditorAgent(Agent):
    def generate_response(self, current_state, history_summary):
        task = f"""
        Assemble the final story from all generated elements (scenes, characters, setting details, dialogue).
        Ensure a clear beginning, middle, and end.
        Integrate image prompts logically within the narrative flow.
        Perform a final check for coherence, theme ({current_state.get('theme')}), age appropriateness, reading level, and ensure avoided content ({current_state.get('avoid_content')}) is excluded.
        Format the output clearly, marking image prompt locations.
        """
        prompt = self._create_prompt(current_state, history_summary, task)
        response = self._simulate_llm_call(prompt) # Simulates the editing process

        # --- Simulation of Final Story Assembly ---
        # In reality, this agent would parse current_state['story_elements']
        # and construct the final narrative.
        final_story_text = (
            f"# Story: The Adventures of {current_state.get('characters', 'Our Heroes')}\n\n"
            f"**Theme:** {current_state.get('theme', 'A valuable lesson')}\n"
            f"**Genre:** {current_state.get('genre', 'An exciting tale')}\n\n"
            f"Once upon a time, in the magical {current_state.get('setting', 'land')}, lived {current_state.get('characters', 'some interesting characters')}.\n\n"
            f"{current_state.get('image_prompts')[0] if current_state.get('image_prompts') else '[IMAGE: Placeholder for opening scene]'}\n\n"
            f"They embarked on an adventure...\n"
            f"(... Placeholder for middle of the story derived from story_elements ...)\n\n"
            f"{current_state.get('image_prompts')[1] if len(current_state.get('image_prompts', [])) > 1 else '[IMAGE: Placeholder for middle scene]'}\n\n"
            f"In the end, they learned about {current_state.get('theme', 'something important')}.\n\n"
            f"{current_state.get('image_prompts')[2] if len(current_state.get('image_prompts', [])) > 2 else '[IMAGE: Placeholder for final scene]'}\n\n"
            f"The End."
        )
        current_state['final_story'] = final_story_text
        # --- End Simulation ---

        return f"Final story compiled and reviewed. Ready for output.\n[Final story stored in current_state['final_story']]"


# --- Orchestration Logic ---

def run_agent_pipeline(user_preferences):
    """Manages the multi-agent debate/pipeline."""
    logging.info("\n--- Starting Agent Pipeline ---")

    agents = [
        StorytellerAgent("Storyteller"),
        CharacterDesignerAgent("Character Designer"),
        WorldBuilderAgent("World Builder"),
        ConceptualIllustratorAgent("Conceptual Illustrator 1"), # First image prompt early
        DialogCoachAgent("Dialog Coach"),
        ChildrenLinguistAgent("Children Linguist"),
        StorytellerAgent("Storyteller - Middle"), # Continue story
        ConceptualIllustratorAgent("Conceptual Illustrator 2"), # Second image prompt
        VisualDesignEditorAgent("Visual Design Editor"), # Review prompts so far
        FinalPreprintEditorAgent("Final Preprint Editor") # Compile and finalize
    ]
    # Adjust agent order and repetition based on N_TURNS and desired flow

    current_state = user_preferences.copy() # Start with user prefs
    conversation_history = []

    num_actual_turns = min(N_TURNS, len(agents)) # Limit turns if N_TURNS > len(agents)

    for i in range(num_actual_turns):
        agent = agents[i]
        logging.info(f"\n--- Turn {i+1}/{num_actual_turns} | Agent: {agent.name} ---")

        # Create a distilled summary of the last few turns (e.g., last 3)
        history_summary = "\n".join(conversation_history[-3:]) if conversation_history else "No previous discussion yet."

        # Agent performs its action
        try:
            response = agent.generate_response(current_state, history_summary)
            agent_utterance = f"**{agent.name}:** {response}"
            logging.info(agent_utterance)
            conversation_history.append(agent_utterance) # Log the full utterance
        except Exception as e:
            logging.error(f"Error during agent {agent.name} turn: {e}")
            # Optionally, decide whether to continue or stop the pipeline on error
            continue # Continue to the next agent

        # Optional: Add a small delay or a point for user intervention if needed
        # time.sleep(1)

    logging.info("\n--- Agent Pipeline Finished ---")

    # Ensure the final editor (if included) has placed the story in current_state
    if 'final_story' not in current_state:
         logging.warning("Final story not found in state. Attempting fallback generation.")
         # Fallback: simple concatenation if editor failed or wasn't last
         fallback_story = f"# Fallback Story for {current_state.get('characters')}\n\n"
         fallback_story += current_state.get('story_elements', {}).get('opening', 'Once upon a time...') + "\n\n"
         fallback_story += "\n\n".join(current_state.get('image_prompts', [])) + "\n\n"
         fallback_story += current_state.get('story_elements', {}).get('ending', 'The End.')
         current_state['final_story'] = fallback_story


    return current_state


def save_story_to_markdown(final_state):
    """Saves the final story to a markdown file."""
    os.makedirs(STORIES_DIR, exist_ok=True)
    story_title = final_state.get('characters', 'My Story').replace(' ', '_')
    filename = f"story_{story_title}_{timestamp}.md"
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
        logging.error(f"An unexpected error occurred during file saving: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Starting Children's Story Generator...")
    user_prefs = get_user_input()
    final_story_state = run_agent_pipeline(user_prefs)
    save_story_to_markdown(final_story_state)
    logging.info("\nScript finished.")
    print(f"\nProcess complete. Check '{STORIES_DIR}' for the story and '{LOG_DIR}' for the log file ({log_file_path}).")
