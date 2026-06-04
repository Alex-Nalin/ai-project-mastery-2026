import torch
from diffusers import FluxPipeline
from PIL import Image

def generate_with_flux(
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, ugly",
    num_inference_steps: int = 50,
    guidance_scale: float = 7.5,
    seed: int = 42
) -> Image.Image:
    """
    Generate an image using FLUX model locally.
    """
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16
    )
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    pipe.enable_model_cpu_offload()  # Save VRAM
    
    generator = torch.Generator(device="cuda").manual_seed(seed)
    
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=generator
    ).images[0]
    
    return image

# Usage
image = generate_with_flux(
    prompt="A sleek black wireless charging stand for smartwatch, "
           "minimalist design, brushed aluminum finish, "
           "soft studio lighting, white background, 8K product photography",
    seed=12345
)
image.save("charging_stand_flux.png")
