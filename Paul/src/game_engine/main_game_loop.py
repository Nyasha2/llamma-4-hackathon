import json
import os
from src.llm_interface.llama_api import call_llama_api

def load_game_state():
    """Load the current game state from JSON file."""
    try:
        with open('knowledge_base/game_state.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Game state file not found. Creating default state.")
        return create_default_game_state()
    except json.JSONDecodeError:
        print("Error reading game state file. Creating default state.")
        return create_default_game_state()

def load_world_knowledge():
    """Load the world knowledge from JSON file."""
    try:
        with open('knowledge_base/world_knowledge_graph.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("World knowledge file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error reading world knowledge file.")
        return {}

def create_default_game_state():
    """Create a default game state if none exists."""
    default_state = {
        "player_character": {
            "name": "Player",
            "location": "Unknown",
            "inventory": []
        },
        "conversation_history": [],
        "world_events_unlocked": []
    }
    
    # Save the default state
    os.makedirs('knowledge_base', exist_ok=True)
    with open('knowledge_base/game_state.json', 'w', encoding='utf-8') as f:
        json.dump(default_state, f, indent=2, ensure_ascii=False)
    
    return default_state

def save_game_state(game_state):
    """Save the current game state to JSON file."""
    try:
        with open('knowledge_base/game_state.json', 'w', encoding='utf-8') as f:
            json.dump(game_state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving game state: {e}")

def start_game():
    """Initialize the game and return the opening message."""
    game_state = load_game_state()
    
    if not game_state.get('conversation_history'):
        # This is a new game, return the story selection message
        return "어떠한 스토리를 넣고 싶습니까?\n\n1. Harry Potter and the Sorcerer's Stone - 마법의 세계로 들어가 해리 포터가 되어보세요.\n2. The Shadow of the Serpent's Eye - 고대 유물을 둘러싼 판타지 모험의 세계.\n\n원하는 스토리를 선택해주세요."
    
    # Return the last message from conversation history
    return game_state['conversation_history'][-1]

def process_player_input(player_input: str, story_id: str = "shadow_serpent"):
    """
    Process player input and return appropriate response based on the selected story.
    
    Args:
        player_input: The player's input text
        story_id: The ID of the selected story ("harry_potter" or "shadow_serpent")
    
    Returns:
        The response from the game
    """
    game_state = load_game_state()
    world_knowledge = load_world_knowledge()
    
    # Check if this is the first interaction and we need to start a story
    if not game_state.get('conversation_history') or len(game_state['conversation_history']) == 0:
        # This is the first interaction, start the selected story
        if story_id == "harry_potter":
            return start_harry_potter_story(game_state, world_knowledge)
        elif story_id == "shadow_serpent":
            return start_shadow_serpent_story(game_state, world_knowledge)
        else:
            return "스토리를 선택해주세요:\n\n1. Harry Potter and the Sorcerer's Stone\n2. The Shadow of the Serpent's Eye"
    
    # If we already have conversation history, continue the story
    # Add player action to conversation history
    game_state['conversation_history'].append(f"Player: {player_input}")
    
    # Prepare context for AI based on the selected story
    if story_id == "harry_potter":
        # Create Harry Potter context
        book_content = load_book_content('harrypotter.txt')
        context = {
            "world_knowledge": {
                "book_title": "Harry Potter and the Sorcerer's Stone",
                "universe_summary": "A magical world where wizards and witches live alongside Muggles (non-magical people). Based on the actual Harry Potter book series.",
                "book_content": book_content[:2000],
                "characters": [
                    {
                        "name": "Harry Potter",
                        "role": "Protagonist",
                        "description": "A young wizard who survived an attack by the dark wizard Voldemort as a baby. He has a lightning bolt scar on his forehead.",
                        "personality": "Brave, loyal, curious, with a strong sense of justice. He's humble despite his fame.",
                        "knowledge": "Recently discovered he is a wizard and is learning about the magical world. He knows very little about his parents or his past.",
                        "current_goal": "Learn about his magical heritage and attend Hogwarts School of Witchcraft and Wizardry",
                        "background": "Lives with his cruel Muggle relatives, the Dursleys, who have kept his magical heritage secret from him."
                    },
                    {
                        "name": "Rubeus Hagrid",
                        "role": "Gamekeeper at Hogwarts",
                        "description": "A half-giant who is the gamekeeper at Hogwarts and was the first to tell Harry about his magical heritage. He's very large and has a wild beard.",
                        "personality": "Friendly, loyal, enthusiastic, but sometimes careless. He loves magical creatures and is very protective of Harry.",
                        "knowledge": "Knows about magical creatures and was friends with Harry's parents. He was expelled from Hogwarts but Dumbledore let him stay as gamekeeper.",
                        "current_goal": "Help Harry adjust to the magical world and protect him",
                        "background": "Was framed for opening the Chamber of Secrets and expelled from Hogwarts, but Dumbledore believed in his innocence."
                    }
                ]
            },
            "game_state": game_state
        }
    else:
        # Use shadow serpent context
        context = {
            "world_knowledge": world_knowledge,
            "game_state": game_state
        }
    
    # Get AI response
    ai_response = call_llama_api(player_input, context)
    
    # Add AI response to conversation history
    game_state['conversation_history'].append(f"Narrator: {ai_response}")
    
    # Save updated game state
    save_game_state(game_state)
    
    return ai_response

def load_book_content(book_file: str) -> str:
    """
    Load content from a book file.
    
    Args:
        book_file: The name of the book file to load
        
    Returns:
        The content of the book file
    """
    try:
        book_path = os.path.join('book_data', book_file)
        with open(book_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Book file {book_file} not found.")
        return ""
    except Exception as e:
        print(f"Error reading book file {book_file}: {e}")
        return ""

def start_harry_potter_story(game_state, world_knowledge):
    """Initialize Harry Potter story scenario using the actual book content."""
    # Load the actual Harry Potter book content
    book_content = load_book_content('harrypotter.txt')
    
    # Create Harry Potter specific context with actual book content
    harry_potter_context = {
        "world_knowledge": {
            "book_title": "Harry Potter and the Sorcerer's Stone",
            "universe_summary": "A magical world where wizards and witches live alongside Muggles (non-magical people). Based on the actual Harry Potter book series.",
            "book_content": book_content[:2000],  # Include first 2000 characters for context
            "characters": [
                {
                    "name": "Harry Potter",
                    "role": "Protagonist",
                    "description": "A young wizard who survived an attack by the dark wizard Voldemort as a baby. He has a lightning bolt scar on his forehead.",
                    "personality": "Brave, loyal, curious, with a strong sense of justice. He's humble despite his fame.",
                    "knowledge": "Recently discovered he is a wizard and is learning about the magical world. He knows very little about his parents or his past.",
                    "current_goal": "Learn about his magical heritage and attend Hogwarts School of Witchcraft and Wizardry",
                    "background": "Lives with his cruel Muggle relatives, the Dursleys, who have kept his magical heritage secret from him."
                },
                {
                    "name": "Albus Dumbledore",
                    "role": "Wise Wizard",
                    "description": "The headmaster of Hogwarts School of Witchcraft and Wizardry, one of the greatest wizards of all time. He has a long silver beard and half-moon spectacles.",
                    "personality": "Wise, kind, mysterious, with a twinkle in his eye. He speaks in riddles and has a fondness for lemon drops.",
                    "knowledge": "Knows about Harry's past and the prophecy, expert in magic and the history of the wizarding world. He was the one who left Harry with the Dursleys.",
                    "current_goal": "Protect Harry and guide him in his magical education",
                    "background": "Defeated the dark wizard Grindelwald and is considered the only wizard Voldemort ever feared."
                },
                {
                    "name": "Rubeus Hagrid",
                    "role": "Gamekeeper at Hogwarts",
                    "description": "A half-giant who is the gamekeeper at Hogwarts and was the first to tell Harry about his magical heritage. He's very large and has a wild beard.",
                    "personality": "Friendly, loyal, enthusiastic, but sometimes careless. He loves magical creatures and is very protective of Harry.",
                    "knowledge": "Knows about magical creatures and was friends with Harry's parents. He was expelled from Hogwarts but Dumbledore let him stay as gamekeeper.",
                    "current_goal": "Help Harry adjust to the magical world and protect him",
                    "background": "Was framed for opening the Chamber of Secrets and expelled from Hogwarts, but Dumbledore believed in his innocence."
                },
                {
                    "name": "Vernon Dursley",
                    "role": "Harry's Uncle",
                    "description": "Harry's Muggle uncle who is large and beefy with hardly any neck. He works at a drill company called Grunnings.",
                    "personality": "Proud, narrow-minded, and obsessed with being normal. He despises anything magical or unusual.",
                    "knowledge": "Knows about magic but refuses to acknowledge it. He's terrified of being associated with the wizarding world.",
                    "current_goal": "Keep Harry away from magic and maintain his 'normal' lifestyle",
                    "background": "Married to Petunia, Harry's aunt. He's the father of Dudley and lives at Number 4, Privet Drive."
                },
                {
                    "name": "Petunia Dursley",
                    "role": "Harry's Aunt",
                    "description": "Harry's Muggle aunt who is thin and blonde with a long neck. She's Lily Potter's sister.",
                    "personality": "Jealous of her sister's magical abilities, spiteful, and obsessed with appearing normal.",
                    "knowledge": "Knows about magic from her sister Lily but has rejected it. She's ashamed of her magical heritage.",
                    "current_goal": "Keep Harry away from magic and pretend her sister never existed",
                    "background": "Lily Potter's older sister who was jealous that Lily got to go to Hogwarts while she didn't."
                }
            ],
            "locations": [
                {
                    "name": "Number 4, Privet Drive",
                    "description": "Harry's home with his Muggle relatives, the Dursleys. A perfectly normal house in a perfectly normal neighborhood.",
                    "characters_present": ["Harry Potter", "Vernon Dursley", "Petunia Dursley", "Dudley Dursley"],
                    "current_situation": "Harry has just received his Hogwarts letter and the Dursleys are trying to prevent him from learning about magic."
                },
                {
                    "name": "Hogwarts School of Witchcraft and Wizardry",
                    "description": "A magical castle where young wizards and witches learn magic. It's located in Scotland and is protected by powerful magic.",
                    "characters_present": ["Albus Dumbledore", "Rubeus Hagrid", "Students", "Teachers"],
                    "current_situation": "The school is preparing for the new term and Harry has been accepted as a first-year student."
                },
                {
                    "name": "Diagon Alley",
                    "description": "A magical shopping street in London where wizards buy their supplies. It's hidden from Muggles behind the Leaky Cauldron pub.",
                    "characters_present": ["Shopkeepers", "Wizards", "Rubeus Hagrid"],
                    "current_situation": "This is where Harry will need to go to buy his school supplies for Hogwarts."
                },
                {
                    "name": "The Leaky Cauldron",
                    "description": "A famous wizarding pub in London that serves as the entrance to Diagon Alley. It's invisible to Muggles.",
                    "characters_present": ["Tom the barman", "Wizards", "Travelers"],
                    "current_situation": "This is where Harry will first enter the magical world, guided by Hagrid."
                }
            ],
            "key_events": [
                "The night Voldemort tried to kill Harry but failed, leaving him with his lightning bolt scar",
                "Harry being left on the Dursleys' doorstep by Dumbledore with a letter explaining his situation",
                "Harry growing up with the Dursleys, unaware of his magical heritage",
                "Harry receiving his Hogwarts acceptance letter",
                "The Dursleys trying to prevent Harry from learning about magic"
            ]
        },
        "game_state": {
            "player_character": {
                "name": "Harry Potter",
                "role": "Young Wizard",
                "location": "Number 4, Privet Drive",
                "background": "Recently discovered you are a wizard and have been invited to attend Hogwarts School of Witchcraft and Wizardry. You live with your cruel Muggle relatives who have kept your magical heritage secret.",
                "inventory": ["Hogwarts acceptance letter", "List of school supplies"],
                "current_goal": "Learn about the magical world and prepare for Hogwarts",
                "knowledge": "You know very little about magic or your parents. You've been told they died in a car crash, but you're starting to suspect that's not true."
            }
        }
    }
    
    # Add the story selection to conversation history
    game_state['conversation_history'] = [
        "Narrator: You are Harry Potter, a young boy who has just discovered he is a wizard. You're sitting in your room at Number 4, Privet Drive, reading your Hogwarts acceptance letter for the hundredth time. The Dursleys have been trying to prevent you from learning about magic, but the letters keep coming. Suddenly, you hear a loud knock at the door..."
    ]
    
    save_game_state(game_state)
    
    # Use the Harry Potter context for the AI response
    response = call_llama_api("I'm Harry Potter and I just got my Hogwarts letter. The Dursleys have been trying to hide it from me, but I want to learn about magic and my parents. What should I do?", harry_potter_context)
    
    return f"Narrator: {response}"

def start_shadow_serpent_story(game_state, world_knowledge):
    """Initialize Shadow of the Serpent's Eye story scenario."""
    # Use the existing world knowledge for the shadow serpent story
    context = {
        "world_knowledge": world_knowledge,
        "game_state": game_state
    }
    
    # Reset conversation history for the shadow serpent story
    game_state['conversation_history'] = [
        "Narrator: You find yourself in the dimly lit common room of the Prancing Pony Inn. The air is thick with the smell of ale and wood smoke. In the corner, a scarred figure with a weathered face watches you intently. This is Captain Thorne, a retired royal guard who knows more about your situation than he lets on. He beckons you over with a subtle gesture. What do you do?"
    ]
    
    save_game_state(game_state)
    
    # Use the shadow serpent context for the AI response
    response = call_llama_api("I approach the mysterious figure in the corner.", context)
    
    return f"Narrator: {response}"

def process_player_action(action):
    """Legacy function for backward compatibility."""
    game_state = load_game_state()
    world_knowledge = load_world_knowledge()
    
    # Add player action to conversation history
    game_state['conversation_history'].append(f"Player: {action}")
    
    # Prepare context for AI
    context = {
        "world_knowledge": world_knowledge,
        "game_state": game_state
    }
    
    # Get AI response
    ai_response = call_llama_api(action, context)
    
    # Add AI response to conversation history
    game_state['conversation_history'].append(f"Narrator: {ai_response}")
    
    # Save updated game state
    save_game_state(game_state)
    
    return ai_response 