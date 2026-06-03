import torch
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
import cv2
import numpy as np

def generate_with_controlnet(
    product_image: str,
    scene_prompt: str,
    controlnet_type: str = "depth"
) -> Image:
    """
    Generate a scene with ControlNet guidance.
    
    Args:
        product_image: Path to product image
        scene_prompt: Description of desired scene
        controlnet_type: 'depth', 'canny', or 'openpose'
    """
    # Load ControlNet model
    controlnet = ControlNetModel.from_pretrained(
        f"diffusers/controlnet-{controlnet_type}-sdxl-1.0",
        torch_dtype=torch.float16
    )
    
    pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        torch_dtype=torch.float16
    ).to("cuda")
    
    # Generate control image
    input_image = load_image(product_image)
    
    if controlnet_type == "depth":
        # Use depth estimation model
        from transformers import pipeline
        depth_estimator = pipeline("depth-estimation", model="Intel/dpt-large")
        control_image = depth_estimator(input_image)["depth"]
        control_image = np.array(control_image)
        control_image = control_image[:, :, None]
        control_image = np.concatenate([control_image] * 3, axis=2)
        control_image = Image.fromarray(control_image)
    
    elif controlnet_type == "canny":
        # Edge detection
        image_np = np.array(input_image)
        edges = cv2.Canny(image_np, 100, 200)
        control_image = Image.fromarray(edges)
    
    # Generate
    image = pipe(
        prompt=scene_prompt,
        negative_prompt="blurry, low quality, distorted",
        image=control_image,
        num_inference_steps=30,
        controlnet_conditioning_scale=0.8
    ).images[0]
    
    return image
