from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 选择模型
# model_name = "Helsinki-NLP/opus-mt-en-chk"
model_name = "/home/github/opus-mt-en-chk"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate(text, tokenizer, model):
    # 将输入文本编码为模型输入格式
    inputs = tokenizer.encode(text, return_tensors="pt", truncation=True)
    # 使用模型生成翻译
    outputs = model.generate(inputs, max_length=40, num_beams=4, early_stopping=True)
    # 解码生成的张量为文本
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

if __name__ == '__main__':
    english_text = "Hello, how are you?"
    translated_text = translate(english_text, tokenizer, model)
    print("Translated text:", translated_text)


