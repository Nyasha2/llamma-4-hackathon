# prompts.py

def build_world_prompt_from_text(story_text: str) -> str:
    """
    Given raw story text (e.g. from Harry Potter), generate a prompt to ask the LLM to build the world codex.
    """
    prompt = f"""
You are a world-building AI assistant.

Below is a passage from a fictional universe. Please analyze it and extract the following:
1. A high-level world summary (setting, era, magic/tech level)
2. Key themes or tones
3. At least 3 rules or laws of this universe
4. What kind of characters, factions, or conflicts seem to exist?

Use this information to propose an initial Codex to seed a living fictional world.

--- STORY INPUT START ---
{story_text}
--- STORY INPUT END ---
    """.strip()

    return prompt


def build_entity_generation_prompt(world_summary: str) -> str:
    """
    Create a prompt to generate structured entities based on a world summary.
    """
    prompt = f"""
You are an AI entity forge. Based on the fictional world described below, generate:

- 3 Characters (Name, Role, Personality, Motivation)
- 2 Factions (Name, Ideology, Resources)
- 2 Locations (Name, Description, Purpose)

--- WORLD SUMMARY START ---
{world_summary}
--- WORLD SUMMARY END ---
    """.strip()

    return prompt


def build_oracle_prompt(world_context: str, user_question: str) -> str:
    """
    Create a prompt for the Oracle module to answer user questions based on the world.
    """
    prompt = f"""
You are the Oracle of a fictional universe.

Here is the world context:

{world_context}

Now answer the user's question in a way that makes sense within this universe:

Q: {user_question}
A:"""

    return prompt
