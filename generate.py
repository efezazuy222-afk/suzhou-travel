import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-e411674adab84202adea93c8e918b475",
    base_url="https://api.deepseek.com"
)

def generate_tour(topic):
    prompt = f"""你是澜青旅行社的苏州旅游内容编辑。请为旅游主题"{topic}"生成一个完整的旅游套餐 .mdx 文件。

严格按以下格式输出，所有文字用中文，slug 用英文小写连字符：

---
title: "套餐中文标题"
category: "Cultural Tour"
description: "一句话中文描述"
cover: "/img/tour1.jpg"

gallery:
  - "/img/tour1.jpg"
  - "/img/tour2.jpg"
  - "/img/tour3.jpg"
  - "/img/tour4.jpg"

duration: "全天"
location: "苏州，江苏，中国"
price: 398

pricing:
  - label: "标准套餐"
    price: 398
    multiplier: 1
  - label: "深度体验"
    price: 598
    multiplier: 1.6
  - label: "VIP私享"
    price: 998
    multiplier: 2.4

rating: 4.8
reviews: 200

facilities:
  - 专业中文导游
  - 门票全包
  - 苏州特色午餐
  - 空调车接送
  - 无线讲解器
---

## 行程安排

（用中文写详细行程，分上午、中午、下午）

## 行程亮点

（列出5-6个亮点）

（正文不少于500字）
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是澜青旅行社的专业苏州旅游内容编辑，所有输出必须用中文。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        stream=False
    )
    
    return response.choices[0].message.content


def save_tour(filename, content):
    filepath = f"src/content/tours/{filename}.mdx"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {filepath}")


if __name__ == "__main__":
    topic = input("Enter tour topic in Chinese (e.g., 苏州评弹体验): ")
    print(f"Generating: {topic}...")
    content = generate_tour(topic)
    
    slug = input("Enter slug (e.g., suzhou-pingtan): ")
    save_tour(slug, content)
    print("Done! Restart npm run dev to view.")