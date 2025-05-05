import uuid
import re
from typing import List, Dict, Tuple
import random

# Define constants
N_TURNS = 10
AGENTS = [
    "Storyteller",
    "Character Designer",
    "World Builder",
    "Dialog Coach",
    "Children Linguist",
    "Conceptual Children Illustrator",
    "Visual Design Editor",
    "Final Preprint Editor",
    "Continuity Manager"  # New agent for ensuring coherence
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
    """Initializes the story structure with a summary digest."""
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
        'image_prompts': [],
        'summary_digest': []  # Tracks contributions for continuity
    }

def agent_contribution(agent: str, story: Dict, turn: int) -> Dict:
    """Simulates contribution from each agent, using summary digest for coherence."""
    # Create a summary of previous contributions for the current turn
    current_summary = f"Turn {turn}: "
    
    if agent == "Storyteller":
        if turn == 1:
            story['title'] = f"The {story['genre'].capitalize()} of {story['characters'][0]} in {story['setting']}"
            num_scenes = max(3, story['read_aloud_time'] // 2)
            story['scenes'] = [{'text': '', 'image_prompt': ''} for _ in range(num_scenes)]
            story['scenes'][0]['text'] = f"In the heart of {story['setting']}, {story['characters'][0]} found {story['details']} that promised a {story['genre'].lower()} filled with {story['theme'].lower()}."
            current_summary += f"Storyteller set the title and initiated the first scene with {story['characters'][0]} finding {story['details']}."
        else:
            for i, scene in enumerate(story['scenes']):
                if not scene['text'] and i > 0:
                    prev_scene = story['scenes'][i-1]['text']
                    scene['text'] = f"Following {prev_scene.split('.')[0].lower()}, {story['characters'][0]} ventured deeper into {story['setting']} to uncover more about {story['theme'].lower()}."
                    current_summary += f"Storyteller added scene {i+1} continuing from previous scene."

    elif agent == "Character Designer":
        for i, char in enumerate(story['characters']):
            if turn == 1:
                story['characters'][i] = f"{char}, known for {story['theme'].lower()}"
                current_summary += f"Character Designer defined {char} with a trait tied to {story['theme'].lower()}."
            else:
                story['characters'][i] += f" and a love for {story['setting'].lower()}"
                current_summary += f"Character Designer enriched {char} with a connection to {story['setting']}."

    elif agent == "World Builder":
        for i, scene in enumerate(story['scenes']):
            if not scene['text']:
                scene['text'] = f"The {story['setting']} glowed with {story['genre'].lower()} magic, revealing {story['details']}."
                current_summary += f"World Builder described {story['setting']} in scene {i+1} with {story['genre']} elements."
            elif turn > 1:
                scene['text'] += f" The {story['setting']} hummed with secrets of {story['theme'].lower()}."
                current_summary += f"World Builder enhanced {story['setting']} in scene {i+1} with {story['theme']} secrets."

    elif agent == "Dialog Coach":
        for i, scene in enumerate(story['scenes']):
            if scene['text'] and f"said {story['characters'][0]}" not in scene['text']:
                prev_summary = story['summary_digest'][-1] if story['summary_digest'] else ""
                dialog = f" '{story['theme'].capitalize()} will guide us,' said {story['characters'][0]} confidently."
                scene['text'] += dialog
                current_summary += f"Dialog Coach added dialogue in scene {i+1} reflecting {story['theme']}."

    elif agent == "Children Linguist":
        for scene in story['scenes']:
            if scene['text']:
                # Simplify for age-appropriate reading level
                scene['text'] = scene['text'].replace('ventured', 'went').replace('revealing', 'showing').replace('confidently', 'bravely')
                if story['reading_level'] in ['K-2', '1-3']:
                    scene['text'] = ' '.join(word if len(word) < 6 else word[:5] for word in scene['text'].split())
                current_summary += f"Children Linguist simplified language in scene for {story['reading_level']} readers."

    elif agent == "Conceptual Children Illustrator":
        for i, scene in enumerate(story['scenes']):
            if not scene['image_prompt']:
                scene['image_prompt'] = f"A vibrant {story['genre']} scene in {story['setting']} featuring {story['characters'][0]} embracing {story['theme'].lower()}"
                current_summary += f"Illustrator created an image prompt for scene {i+1} with {story['characters'][0]}."
            elif turn > 1:
                scene['image_prompt'] += f", with details of {story['details']}"
                current_summary += f"Illustrator refined image prompt for scene {i+1} with {story['details']}."

    elif agent == "Visual Design Editor":
        for i, scene in enumerate(story['scenes']):
            if scene['image_prompt']:
                scene['image_prompt'] += f", colorful, {story['age_appropriate']}-friendly, avoiding {', '.join(story['avoid_content'])}"
                current_summary += f"Visual Design Editor ensured scene {i+1}'s image prompt is age-appropriate."

    elif agent == "Final Preprint Editor":
        story['title'] = story['title'].title()
        for i, scene in enumerate(story['scenes']):
            scene['text'] = scene['text'].capitalize()
            if i == len(story['scenes']) - 1:
                scene['text'] += f" And with {story['theme'].lower()}, {story['characters'][0]}'s {story['genre'].lower()} ended happily!"
            else:
                scene['text'] += f" Ready for more, {story['characters'][0]} smiled."
            current_summary += f"Preprint Editor finalized scene {i+1} text and story ending."

    elif agent == "Continuity Manager":
        for i, scene in enumerate(story['scenes']):
            if i > 0 and scene['text']:
                prev_scene = story['scenes'][i-1]['text']
                if story['theme'].lower() not in scene['text'].lower():
                    scene['text'] += f" All along, {story['theme'].lower()} tied their journey together."
                if story['characters'][0].split(',')[0] not in scene['text']:
                    scene['text'] = f"{story['characters'][0].split(',')[0]} continued as " + scene['text']
                current_summary += f"Continuity Manager ensured scene {i+1} maintains {story['theme']} and {story['characters'][0]} presence."

    story['summary_digest'].append(current_summary)
    return story

def multi_agent_pipeline(story: Dict) -> Dict:
    """Runs the multi-agent pipeline for story synthesis with increased turns."""
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