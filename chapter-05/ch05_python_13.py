import asyncio
from pathlib import Path
from typing import Optional
import json

class ProductPhotographyPipeline:
    """
    Automated product photography pipeline.
    
    Input: Product image (PNG/JPG)
    Output: E-commerce photo with AI-generated scene
    
    Workflow:
    1. Remove background using rembg
    2. Generate depth map for ControlNet
    3. Run ComfyUI workflow with scene prompt
    4. Apply post-processing (color correction, sharpening)
    5. Save final image
    """
    
    def __init__(
        self,
        comfyui_address: str = "127.0.0.1:8188",
        output_dir: str = "./output"
    ):
        self.comfyui = ComfyUIClient(comfyui_address)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def process_product(
        self,
        input_image: str,
        scene_prompt: str,
        product_name: str = "product",
        output_format: str = "jpg"
    ) -> Path:
        """
        Process a single product image.
        
        Args:
            input_image: Path to input product image
            scene_prompt: Description of desired scene
            product_name: Identifier for output file
            output_format: 'jpg' or 'png'
        
        Returns:
            Path to final image
        """
        print(f"Processing {product_name}...")
        
        # Step 1: Remove background
        print("  Step 1: Removing background...")
        clean_image = await self._remove_background(input_image)
        clean_path = self.output_dir / f"{product_name}_clean.png"
        clean_image.save(clean_path)
        
        # Step 2: Generate depth map
        print("  Step 2: Generating depth map...")
        depth_map = await self._generate_depth_map(clean_image)
        depth_path = self.output_dir / f"{product_name}_depth.png"
        depth_map.save(depth_path)
        
        # Step 3: Run ComfyUI workflow
        print("  Step 3: Running ComfyUI scene generation...")
        final_image = await self._run_comfyui_pipeline(
            product_image=clean_path,
            depth_map=depth_path,
            scene_prompt=scene_prompt
        )
        
        # Step 4: Post-process
        print("  Step 4: Applying post-processing...")
        final_image = self._post_process(final_image)
        
        # Step 5: Save
        output_path = self.output_dir / f"{product_name}_final.{output_format}"
        final_image.save(output_path, quality=95)
        
        print(f"  Done! Saved to {output_path}")
        return output_path
    
    async def _remove_background(self, image_path: str):
        """Remove background using rembg."""
        from rembg import remove
        from PIL import Image
        
        with open(image_path, "rb") as f:
            input_data = f.read()
        
        output_data = remove(input_data)
        return Image.open(io.BytesIO(output_data))
    
    async def _generate_depth_map(self, image):
        """Generate depth map for ControlNet guidance."""
        from transformers import pipeline
        
        depth_estimator = pipeline(
            "depth-estimation",
            model="Intel/dpt-large"
        )
        return depth_estimator(image)["depth"]
    
    async def _run_comfyui_pipeline(
        self,
        product_image: Path,
        depth_map: Path,
        scene_prompt: str
    ):
        """Execute ComfyUI workflow."""
        # Load workflow template
        workflow_path = Path("workflows/product_photography.json")
        with open(workflow_path) as f:
            workflow = json.load(f)
        
        # Configure nodes
        for node_id, node in workflow.items():
            if node["class_type"] == "LoadImage":
                node["inputs"]["image"] = str(product_image)
            elif node["class_type"] == "LoadImage" and "depth" in node_id:
                node["inputs"]["image"] = str(depth_map)
            elif node["class_type"] == "CLIPTextEncode":
                if "positive" in node_id:
                    node["inputs"]["text"] = scene_prompt
        
        # Execute
        prompt_id = self.comfyui.queue_workflow(workflow)
        return self.comfyui.get_image(prompt_id, "save_image_node")
    
    def _post_process(self, image):
        """Apply color correction and sharpening."""
        from PIL import ImageEnhance, ImageFilter
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Slight unsharp mask
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=50))
        
        return image
    
    async def batch_process(
        self,
        products: list,
        scene_prompt_template: str = None
    ):
        """
        Process multiple products in batch.
        
        Args:
            products: List of dicts with 'image' and 'name' keys
            scene_prompt_template: Optional template with {product_name} placeholder
        """
        tasks = []
        for product in products:
            prompt = scene_prompt_template or product.get("prompt", "Professional product photography, white background")
            if scene_prompt_template:
                prompt = prompt.format(product_name=product["name"])
            
            task = self.process_product(
                input_image=product["image"],
                scene_prompt=prompt,
                product_name=product["name"]
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)

# Usage
pipeline = ProductPhotographyPipeline()

# Single product
result = asyncio.run(pipeline.process_product(
    input_image="sneakers_raw.jpg",
    scene_prompt="Sneakers on a minimalist pedestal, "
                 "soft studio lighting, white gradient background, "
                 "professional product photography, 8K quality",
    product_name="air_max_2026"
))

# Batch processing
products = [
    {"image": "shoes_1.jpg", "name": "running_shoe_black"},
    {"image": "shoes_2.jpg", "name": "running_shoe_white"},
    {"image": "bag_1.jpg", "name": "leather_backpack"}
]

results = asyncio.run(pipeline.batch_process(
    products,
    scene_prompt_template="{product_name} on marble surface, "
                         "elegant studio lighting, "
                         "professional e-commerce photography"
))
