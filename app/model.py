from transformers import MllamaForConditionalGeneration, AutoProcessor
import torch
import gc

from helpers import singleton

@singleton
class VLMModel():
    def __init__(self,  **kwargs):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MllamaForConditionalGeneration.from_pretrained(
            kwargs.get("model_id"),
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        self.processor = AutoProcessor.from_pretrained(kwargs.get("model_id"))

    def generate(self, prompt, image):
        self.model.to("cuda")
        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]}
        ]
        input_text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(image, input_text, return_tensors="pt").to(self.device)

        output = self.model.generate(**inputs, max_new_tokens=700, min_p=0.1)
        decoded_output =  self.processor.decode(output[0])[len(input_text)-1:]
        try:
            self.model.to("cpu")
        except exception as e:
            print(e)
        torch.cuda.empty_cache()
        gc.collect()
        return decoded_output.replace("|end_header_id|>", "").replace("<|eot_id|>", "")
    

"""if __name__ == "__main__":
    from PIL import Image
    image = Image.open("jar.png")
    prompt = "Write a title and a description for this image"
    model = VLMModel(model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct")
    description = model.generate(prompt, image)
    print(description)"""