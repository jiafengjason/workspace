from openai import OpenAI

client = OpenAI(
    api_key="sk-4b5f2a482b424108b8e62efec9a68fa0",
    base_url="https://api.deepseek.com/v1"
)

try:
    completion = client.chat.completions.create(
        model="deepseek-chat",  # 免费模型
        messages=[{"role": "user", "content": "hello"}]
    )
    print("✅ DeepSeek 连通成功！")
    print(completion.choices[0].message.content)
except Exception as e:
    print("❌ 失败")
    print(e)
