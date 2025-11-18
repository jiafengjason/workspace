from transformers import AutoProcessor, VisionEncoderDecoderModel
import requests
from PIL import Image
import torch

#model_name = "microsoft/trocr-base-handwritten"
model_name = "/home/github/TR_OCR_LARGE"
processor = AutoProcessor.from_pretrained(model_name, use_fast=True)
model = VisionEncoderDecoderModel.from_pretrained(model_name)

# load image from the IAM dataset
image_path = "/home/workspace/python/code.jpg"
image = Image.open(image_path).convert("RGB")

# training
model.config.decoder_start_token_id = processor.tokenizer.eos_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.vocab_size = model.config.decoder.vocab_size

pixel_values = processor(image, return_tensors="pt").pixel_values
text = "hello world"
labels = processor.tokenizer(text, return_tensors="pt").input_ids
outputs = model(pixel_values=pixel_values, labels=labels)
loss = outputs.loss

# inference (generation)
generated_ids = model.generate(pixel_values)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(generated_text)