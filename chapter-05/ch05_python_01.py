import openai
from typing import Optional
import base64
from pathlib import Path

async def generate_product_image(
    product_name: str,
    product_description: str,
    style: str = "professional product photography",
    background: str = "white seamless",
    size: str = "1792x1024",
    quality: str = "hd",
    output_path: Optional[Path] = None
) -> bytes:
    """
    Generate a product image using DALL-E 3.
    
    Args:
        product_name: Name of the product
        product_description: Detailed description for accurate rendering
        style: Photography style
        background: Background description
        size: Image dimensions (1024x1024, 1792x1024, or 1024x1792)
        quality: 'standard' or 'hd'
        output_path: Optional path to save the image
    
    Returns:
        Image bytes
    """
    prompt = (
        f"Professional e-commerce product photo of {product_name}. "
        f"Description: {product_description}. "
        f"Style: {style}. "
        f"Background: {background}. "
        f"Clean lighting, no shadows, centered composition, high detail."
    )
    
    client = openai.OpenAI()
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
        response_format="b64_json"
    )
    
    image_data = base64.b64decode(response.data[0].b64_json)
    
    if output_path:
        output_path.write_bytes(image_data)
    
    return image_data
