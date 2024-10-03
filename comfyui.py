import json
import uuid
import urllib.request
import websocket
from PIL import Image
import io
import logging
from typing import Dict, Any, Optional
from requests_toolbelt import MultipartEncoder

from color_utils import ColorDetector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comfyui.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ComfyUI')

class ComfyUIHandler:
    def __init__(self, server_address: str = "127.0.0.1:8188", workflow_path: str = "workflow.json"):
        self.server_address = server_address
        self.workflow_path = workflow_path
        self.client_id = str(uuid.uuid4())
        self.color_detector = ColorDetector()
        
    def load_workflow(self) -> Dict[str, Any]:
        """Load the workflow JSON file."""
        try:
            with open(self.workflow_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading workflow: {e}")
            raise Exception(f"Error loading workflow: {e}")

    def modify_workflow(self, uploaded_image_path: str, product_data: Dict[str, Any], background_color: str) -> Dict[str, Any]:
        """
        Modify the workflow with new image path and prompts based on product data.
        
        Args:
            uploaded_image_path: The path of the uploaded image in ComfyUI
            product_data: Dictionary containing product information from the model output
                Expected keys: 'entity_name', 'product_title'
        """
        try:
            workflow = self.load_workflow()
            
            # Extract product information
            product_name = product_data.get('entity_name', '')
            product_title = product_data.get('product_title', '')
            
            if not product_name or not product_title:
                logger.warning("Missing product information in model output")
                product_name = "generic product"
                product_title = "generic title"

            # Construct the enhanced prompt
            enhanced_prompt = f"{product_name} with {background_color} background, professional product photography, studio lighting"
            
            # Update specific nodes
            try:
                # Update image input node (node 15)
                workflow['15']['inputs']['image'] = uploaded_image_path
                logger.info(f"Updated image path to: {uploaded_image_path}")

                # Update GroundingDino prompt (node 41)
                workflow['41']['inputs']['prompt'] = product_name
                logger.info(f"Updated GroundingDino prompt to: {product_name}")

                # Update CLIP Text Encode prompt (node 54)
                workflow['54']['inputs']['text'] = enhanced_prompt
                logger.info(f"Updated CLIP Text Encode prompt to: {enhanced_prompt}")

            except KeyError as e:
                logger.error(f"Failed to update workflow node: {e}")
                raise Exception(f"Workflow structure mismatch: {e}")
                
            return workflow
        except Exception as e:
            logger.error(f"Error in modify_workflow: {e}")
            raise

    def upload_image(self, image: Image.Image, image_name: str) -> str:
        """
        Upload an image to ComfyUI and return the server-side path.
        """
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            multipart_data = MultipartEncoder(
                fields={
                    'image': (image_name, img_byte_arr, 'image/png'),
                    'type': 'input',
                    'overwrite': 'true'
                }
            )
            
            headers = {'Content-Type': multipart_data.content_type}
            request = urllib.request.Request(
                f"http://{self.server_address}/upload/image",
                data=multipart_data,
                headers=headers
            )
            
            with urllib.request.urlopen(request) as response:
                response_data = json.loads(response.read())
                image_path = response_data.get('name', '')
                if not image_path:
                    raise Exception("No image path received from server")
                logger.info(f"Successfully uploaded image: {image_path}")
                return image_path
                
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            raise Exception(f"Failed to upload image: {e}")

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Queue a prompt and return the prompt ID."""
        try:
            p = {"prompt": workflow, "client_id": self.client_id}
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(p).encode('utf-8')
            
            req = urllib.request.Request(
                f"http://{self.server_address}/prompt",
                data=data,
                headers=headers
            )
            response = urllib.request.urlopen(req)
            prompt_id = json.loads(response.read())['prompt_id']
            logger.info(f"Successfully queued prompt with ID: {prompt_id}")
            return prompt_id
        except Exception as e:
            logger.error(f"Failed to queue prompt: {e}")
            raise

    def wait_for_completion(self, prompt_id: str) -> None:
        """Wait for the workflow to complete using WebSocket."""
        ws = websocket.WebSocket()
        try:
            ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
            logger.info(f"WebSocket connected, waiting for prompt {prompt_id}")
            
            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executing':
                        if 'node' in message['data']:
                            logger.debug(f"Processing node: {message['data']['node']}")
                        if not message['data']['node'] and message['data']['prompt_id'] == prompt_id:
                            logger.info(f"Workflow completed for prompt {prompt_id}")
                            break
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            raise
        finally:
            ws.close()

    def get_result(self, prompt_id: str) -> Image.Image:
        """Get the resulting image."""
        try:
            with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
                history = json.loads(response.read())

            outputs = history[prompt_id]['outputs']
            last_node = "70"
            image_data = outputs[last_node]['images'][0]
            
            image_url = f"http://{self.server_address}/view?" + urllib.parse.urlencode({
                'filename': image_data['filename'],
                'type': image_data['type'],
                'subfolder': image_data['subfolder']
            })
            
            with urllib.request.urlopen(image_url) as response:
                logger.info(f"Successfully retrieved result image for prompt {prompt_id}")
                return Image.open(io.BytesIO(response.read()))
        except Exception as e:
            logger.error(f"Failed to get result: {e}")
            raise

    def generate_enhanced_image(self, input_image: Image.Image, product_data: Dict[str, Any]) -> Optional[Image.Image]:
        """
        Main method to generate enhanced image using ComfyUI.
        
        Args:
            input_image: The input PIL Image
            product_data: Dictionary containing product information from the model output
                Expected keys: 'entity_name', 'product_title'
        """
        try:
            # Generate a unique name for the image
            image_name = f"input_{uuid.uuid4()}.png"
            
            # Upload the image and get the server-side path
            uploaded_image_path = self.upload_image(input_image, image_name)
            
            background_color = self.color_detector.get_color_name(input_image)
            logger.info(f"Detected background color: {background_color}")
            
            # Modify workflow with new image path and prompts
            modified_workflow = self.modify_workflow(uploaded_image_path, product_data, background_color)
            
            # Queue the prompt and get prompt ID
            prompt_id = self.queue_prompt(modified_workflow)
            
            # Wait for completion
            self.wait_for_completion(prompt_id)
            
            # Get and return the result
            return self.get_result(prompt_id)
            
        except Exception as e:
            logger.error(f"Error in generate_enhanced_image: {e}")
            return None