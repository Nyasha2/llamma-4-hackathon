import os
import re
import json
from typing import Optional, Dict, List
from llama_api_client import LlamaAPIClient

class ChimeraWorldEngine:
    def __init__(self):
        self.api_key = os.getenv('Llama_API_KEY')
        
        if not self.api_key:
            raise ValueError("Llama_API_KEY environment variable is not set")
        
        self.client = LlamaAPIClient(api_key=self.api_key)
        
        # Initialize the Living Codex
        self.world_codex = {
            "title": "Harry Potter and the Sorcerer's Stone",
            "world_type": "Fantasy/Magic",
            "entities": {
                "characters": {},
                "locations": {},
                "factions": {},
                "events": {},
                "items": {},
                "relationships": []
            },
            "world_rules": {
                "magic_system": "Wizarding magic with spells, potions, and magical creatures",
                "social_structure": "Wizarding world hidden from Muggles, Hogwarts as magical school",
                "technology": "Magical artifacts and traditional wizarding methods"
            },
            "current_state": {
                "timeline": "Year 1 at Hogwarts",
                "active_locations": ["Hogwarts School of Witchcraft and Wizardry", "Diagon Alley", "Privet Drive"],
                "major_events": ["Voldemort's defeat", "Harry discovers he's a wizard", "First year at Hogwarts"]
            }
        }
        
        # Load Harry Potter content
        self.load_harry_potter_content()
    
    def load_harry_potter_content(self):
        """Load Harry Potter book content for world context"""
        try:
            with open('book_data/harrypotter.txt', 'r', encoding='utf-8') as f:
                self.harry_potter_content = f.read()[:3000]  # First 3000 chars for context
        except FileNotFoundError:
            self.harry_potter_content = "Harry Potter and the Sorcerer's Stone content not found."
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        if re.search(r'[가-힣]', text):
            return 'Korean'
        elif re.search(r'[あ-んア-ン一-龯]', text):
            return 'Japanese'
        elif re.search(r'[\u4e00-\u9fff]', text):
            return 'Chinese'
        elif re.search(r'[\u0600-\u06ff]', text):
            return 'Arabic'
        elif re.search(r'[\u0400-\u04ff]', text):
            return 'Russian'
        elif any(word in text.lower() for word in ['hola', 'gracias', 'por favor', 'si', 'no', 'que', 'como', 'donde']):
            return 'Spanish'
        elif any(word in text.lower() for word in ['bonjour', 'merci', 'oui', 'non', 'comment', 'ou', 'quoi']):
            return 'French'
        elif any(word in text.lower() for word in ['hallo', 'danke', 'ja', 'nein', 'wie', 'wo', 'was']):
            return 'German'
        else:
            return 'English'
    
    def get_chimera_system_prompt(self, language: str) -> str:
        """Get Project Chimera system prompt based on detected language"""
        base_prompt = f"""You are Project Chimera: Genesis Engine - an AI-powered narrative worldbuilding engine that creates and evolves entire fictional universes.

You are currently operating within the Harry Potter universe, with access to the original book content and a structured world codex.

CORE CAPABILITIES:
🧠 World Anvil: You can analyze and expand the Harry Potter world with new rules, themes, and settings
🧩 Entity Forge: Generate structured characters, factions, places, and timelines
📚 Living Codex: Maintain persistent world state and relationships
🌊 Ripple Engine: Simulate how events affect the world and characters
🔮 Oracle Interface: Answer "what if" questions and explore alternate scenarios
🎭 Scenario Synthesizer: Create new plotlines based on existing world structure

CURRENT WORLD STATE:
- Timeline: {self.world_codex['current_state']['timeline']}
- Active Locations: {', '.join(self.world_codex['current_state']['active_locations'])}
- Major Events: {', '.join(self.world_codex['current_state']['major_events'])}

RESPONSE STYLE:
- Be creative and imaginative while staying true to Harry Potter lore
- Reference the original book content when relevant
- Suggest new world elements, character interactions, or plot developments
- Consider ripple effects of any changes or scenarios
- Maintain the magical atmosphere and tone of the Harry Potter universe

Respond in {language} and maintain the enchanting, magical tone of the Harry Potter world."""
        
        return base_prompt
    
    def analyze_user_query(self, user_message: str) -> Dict:
        """Analyze user query to determine intent and context"""
        analysis_prompt = f"""
Analyze this user query about the Harry Potter world and categorize it:

Query: "{user_message}"

Categories:
1. CHARACTER_QUERY - Questions about characters, their motivations, relationships
2. WORLD_EXPLORATION - Questions about locations, magic, wizarding world
3. WHAT_IF_SCENARIO - Hypothetical scenarios or alternate timelines
4. STORY_GENERATION - Requests for new stories, plots, or scenarios
5. LORE_QUESTION - Questions about magical rules, history, or background
6. INTERACTIVE_STORY - User wants to participate in or influence the story
7. GENERAL_CHAT - General conversation or questions

Respond with only the category number (1-7).
"""
        
        try:
            completion = self.client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            category = completion.completion_message.content.text.strip()
            return {"category": category, "query": user_message}
        except:
            return {"category": "7", "query": user_message}
    
    def generate_world_response(self, user_message: str, query_analysis: Dict) -> str:
        """Generate contextual response based on query analysis and world state"""
        
        # Create context-aware prompt
        context_prompt = f"""
HARRY POTTER WORLD CONTEXT:
{self.harry_potter_content[:1000]}...

CURRENT WORLD STATE:
{json.dumps(self.world_codex['current_state'], indent=2)}

USER QUERY ANALYSIS:
Category: {query_analysis['category']}
Query: {query_analysis['query']}

Generate a creative, engaging response that:
1. Addresses the user's query directly
2. Incorporates Harry Potter lore and atmosphere
3. Suggests new world elements or scenarios when appropriate
4. Maintains the magical, enchanting tone
5. References the living world state and potential ripple effects

User Query: {user_message}

Response:"""
        
        try:
            completion = self.client.chat.completions.create(
                model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[
                    {"role": "system", "content": self.get_chimera_system_prompt(self.detect_language(user_message))},
                    {"role": "user", "content": context_prompt}
                ]
            )
            return completion.completion_message.content.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message: str) -> str:
        """Fallback response when API fails"""
        detected_language = self.detect_language(user_message)
        
        fallback_responses = {
            'Korean': "마법의 세계에서 일시적인 혼란이 발생했습니다. 다시 시도해주세요! 🧙‍♂️✨",
            'Japanese': "魔法世界で一時的な混乱が発生しました。もう一度お試しください！🧙‍♂️✨",
            'Chinese': "魔法世界发生了暂时的混乱。请再试一次！🧙‍♂️✨",
            'Arabic': "حدث اضطراب مؤقت في العالم السحري. يرجى المحاولة مرة أخرى! 🧙‍♂️✨",
            'Russian': "В магическом мире произошла временная путаница. Пожалуйста, попробуйте еще раз! 🧙‍♂️✨",
            'Spanish': "¡Ocurrió una confusión temporal en el mundo mágico. Por favor, inténtalo de nuevo! 🧙‍♂️✨",
            'French': "Une confusion temporaire s'est produite dans le monde magique. Veuillez réessayer ! 🧙‍♂️✨",
            'German': "Im magischen Reich ist eine vorübergehende Verwirrung aufgetreten. Bitte versuchen Sie es erneut! 🧙‍♂️✨",
            'English': "A temporary confusion has occurred in the magical world. Please try again! 🧙‍♂️✨"
        }
        
        return fallback_responses.get(detected_language, fallback_responses['English'])
    
    def get_response(self, user_message: str) -> str:
        """
        Main response method - Project Chimera Genesis Engine
        Creates living, evolving responses based on Harry Potter world
        """
        try:
            # Analyze user query
            query_analysis = self.analyze_user_query(user_message)
            
            # Generate contextual response
            response = self.generate_world_response(user_message, query_analysis)
            
            # Update world state based on interaction
            self.update_world_state(user_message, response)
            
            return response
            
        except Exception as e:
            print(f"Error in Chimera World Engine: {e}")
            return self.get_fallback_response(user_message)
    
    def update_world_state(self, user_message: str, response: str):
        """Update the living world state based on user interaction"""
        # This is a simplified version - in a full implementation,
        # this would track entities, relationships, and world changes
        pass

# Backward compatibility - keep the old class name
class LlamaAPI(ChimeraWorldEngine):
    pass 