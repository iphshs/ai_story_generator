import uuid
import re
from typing import List, Dict, Tuple
import random

# Define constants
N_TURNS = 5
AGENTS = [
    "Storyteller",
    "Character Designer",
    "World Builder",
    "Dialog Coach",
    "Children Linguist",
    "Conceptual Children Illustrator",
    "Visual Design Editor",
    "Final Preprint Editor"
]

def collect_user_input() -> Dict:
    """Collects user input for story specifications."""
    print("Welcome to the Children's Story Generator!")
    user_input = {}
    
    user_input['characters'] = input("Who are the main characters? (e.g., a clever raccoon, young girl, superhero): ").strip()
    user_input['setting'] = input("What is the setting? (e.g., school, enchanted forest, space): ").strip()
    user_input['theme'] = input("What is the theme? (e.g., honesty, friendship): ").strip()
    user_input['genre'] = input("What is the genre? (e.g., adventure, mystery, fantasy): ").strip()
    user_input['reading_level'] = input("What is the self-reading grade level? (e.g., K-2, 3-5): ").strip()
    user_input['age_appropriate'] = input("What age group is this for? (e.g., 4-6, 7-10): ").strip()
    user_input['read_aloud_time'] = input("Estimated read-aloud time in minutes? (5-30): ").strip()
    user_input['details'] = input("Any specific details to include? (e.g., a magical artifact, a specific event): ").strip()
    user_input['avoid_content'] = input("Any content to avoid? (e.g., violence, scary themes): ").strip()
    
    return user_input

def validate_input(user_input: Dict) -> bool:
    """Validates user input."""
    if not all(user_input.values()):
        print("All fields must be filled.")
        return False
    try:
        read_time = int(user_input['read_aloud_time'])
        if not (5 <= read_time <= 30):
            print("Read-aloud time must be between 5 and 30 minutes.")
            return False
    except ValueError:
        print("Read-aloud time must be a number.")
        return False
    return True

def initialize_story(user_input: Dict) -> Dict:
    """Initializes the story structure."""
    return {
        'title': '',
        'characters': user_input['characters'].split(', '),
        'setting': user_input['setting'],
        'theme': user_input['theme'],
        'genre': user_input['genre'],
        'reading_level': user_input['reading_level'],
        'age_appropriate': user_input['age_appropriate'],
        'read_aloud_time': int(user_input['read_aloud_time']),
        'details': user_input['details'],
        'avoid_content': user_input['avoid_content'].split(', '),
        'scenes': [],
        'image_prompts': []
    }

def agent_contribution(agent: str, story: Dict, turn: int) -> Dict:
    """Simulates contribution from each agent."""
    if agent == "Storyteller":
        if turn == 1:
            story['title'] = f"The {story['genre'].capitalize()} of {story['characters'][0]}"
            num_scenes = max(3, story['read_aloud_time'] // 2)
            story['scenes'] = [{'text': '', 'image_prompt': ''} for _ in range(num_scenes)]
            story['scenes'][0]['text'] = f"In the {story['setting']}, {story['characters'][0]} discovered a {story['details']}."
        
    elif agent == "Character Designer":
        for i, char in enumerate(story['characters']):
            story['characters'][i] = f"{char} with a knack for {story['theme'].lower()}"
    
    elif agent == "World Builder":
        for scene in story['scenes']:
            if not scene['text']:
                scene['text'] = f"{story['setting']} sparkled with {story['genre'].lower()} wonders."
    
    elif agent == "Dialog Coach":
        for scene in story['scenes']:
            if scene['text']:
                scene['text'] += f" '{story['theme'].capitalize()} is key,' said {story['characters'][0]}."
    
    elif agent == "Children Linguist":
        for scene in story['scenes']:
            if scene['text']:
                # Simplify language for younger readers
                scene['text'] = scene['text'].replace('discovered', 'found').replace('sparkled', 'shined')
    
    elif agent == "Conceptual Children Illustrator":
        for i, scene in enumerate(story['scenes']):
            if not scene['image_prompt']:
                scene['image_prompt'] = f"A vibrant {story['genre']} scene in {story['setting']} with {story['characters'][0]}"
    
    elif agent == "Visual Design Editor":
        for scene in story['scenes']:
            if scene['image_prompt']:
                scene['image_prompt'] += ", colorful, age-appropriate, avoiding " + ", ".join(story['avoid_content'])
    
    elif agent == "Final Preprint Editor":
        story['title'] = story['title'].title()
        for scene in story['scenes']:
            scene['text'] = scene['text'].capitalize()
            scene['text'] += " And so, the adventure continued!"
    
    return story

def multi_agent_pipeline(story: Dict) -> Dict:
    """Runs the multi-agent pipeline for story synthesis."""
    for turn in range(N_TURNS):
        for agent in AGENTS:
            story = agent_contribution(agent, story, turn + 1)
    return story

def generate_story_text(story: Dict) -> str:
    """Generates the final story text with embedded image prompts."""
    story_text = f"# {story['title']}\n\n"
    for i, scene in enumerate(story['scenes']):
        story_text += f"## Scene {i + 1}\n{scene['text']}\n\n"
        story_text += f"[Image Prompt: {scene['image_prompt']}]\n\n"
    return story_text

def main():
    user_input = collect_user_input()
    if not validate_input(user_input):
        print("Invalid input. Please try again.")
        return
    
    story = initialize_story(user_input)
    story = multi_agent_pipeline(story)
    final_story = generate_story_text(story)
    
    with open("generated_childrens_story.md", "w") as f:
        f.write(final_story)
    print("Story generated and saved as 'generated_childrens_story.md'.")

if __name__ == "__main__":
    main()