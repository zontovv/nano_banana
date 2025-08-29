"""
Prompt templates for GoWombat doodle generation.
"""

from typing import Optional


def create_doodle_prompt(occasion: str, style_hint: Optional[str] = None) -> str:
    """
    Create a detailed prompt for generating a GoWombat doodle.
    
    Args:
        occasion: The event or occasion for the doodle (in any language)
        style_hint: Optional style guidance
        
    Returns:
        str: Complete prompt for image generation
    """
    
    base_prompt = f"""Create a creative doodle design for the company "GoWombat" celebrating: {occasion}

IMPORTANT REQUIREMENTS:
1. The word "GoWombat" must be clearly visible and stylized to match the occasion
2. Incorporate a cute wombat character or wombat-themed elements into the letters
3. Make it in the style of Google Doodles - playful, creative, and thematic
4. The design should be colorful, festive, and eye-catching
5. Include visual elements related to: {occasion}
6. Keep the overall composition balanced and readable
7. The background should be clean (white or light colored)
8. Make it look professional yet fun and engaging

STYLE GUIDELINES:
- Similar to Google Doodles: creative letter transformations
- Incorporate the occasion's symbols into the lettering
- Use vibrant, harmonious colors
- Add small decorative elements around the main text
- Make the wombat character interact with the letters creatively
"""

    if style_hint:
        base_prompt += f"\n\nADDITIONAL STYLE DIRECTION: {style_hint}"
    
    base_prompt += "\n\nGenerate a high-quality, detailed illustration suitable for a company's special occasion celebration."
    
    return base_prompt