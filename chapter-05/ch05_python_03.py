import json
import uuid
import requests
from websocket import create_connection
from PIL import Image
import io

class ComfyUIClient:
    """Client for programmatic ComfyUI workflow execution."""
    
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
    
    def queue_workflow(self, workflow: dict) -> str:
        """Queue a workflow and return the prompt ID."""
        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        response = requests.post(
            f"http://{self.server_address}/prompt",
            json=payload
        )
        return response.json()["prompt_id"]
    
    def get_image(self, prompt_id: str, node_id: str) -> Image.Image:
        """Retrieve output image from a completed workflow."""
        # Wait for completion
        ws = create_connection(
            f"ws://{self.server_address}/ws?clientId={self.client_id}"
        )
        
        while True:
            message = ws.recv()
            data = json.loads(message)
            
            if data["type"] == "executed":
                if data["data"]["node"] == node_id:
                    # Get the image
                    image_data = data["data"]["output"]["images"][0]
                    response = requests.get(
                        f"http://{self.server_address}/view",
                        params={
                            "filename": image_data["filename"],
                            "subfolder": image_data["subfolder"],
                            "type": image_data["type"]
                        }
                    )
                    return Image.open(io.BytesIO(response.content))
    
    def run_product_pipeline(
        self,
        product_image_path: str,
        scene_prompt: str
    ) -> Image.Image:
        """
        Run the complete product photography pipeline.
        
        Args:
            product_image_path: Path to input product image
            scene_prompt: Description of desired scene
        
        Returns:
            Generated product photo
        """
        # Load workflow template
        with open("workflows/product_photography.json", "r") as f:
            workflow = json.load(f)
        
        # Override the input image and prompt
        for node_id, node in workflow.items():
            if node["class_type"] == "LoadImage":
                node["inputs"]["image"] = product_image_path
            elif node["class_type"] == "CLIPTextEncode":
                if "prompt" in node["inputs"]:
                    node["inputs"]["text"] = scene_prompt
        
        # Queue and get result
        prompt_id = self.queue_workflow(workflow)
        return self.get_image(prompt_id, "save_image_node_id")

# Usage
client = ComfyUIClient()
result = client.run_product_pipeline(
    product_image_path="input_sneakers.png",
    scene_prompt="Sneakers on a basketball court at sunset, "
                 "dramatic golden hour lighting, "
                 "professional sports photography style"
)
result.save("final_product_photo.png")
