import os
import random
import requests
import subprocess
from datetime import datetime
from openai import OpenAI

# ==================== API 配置 ====================
DEEPSEEK_KEY = "sk-e411674adab84202adea93c8e918b475"
UNSPLASH_KEY = "zbHgRBgMWl4Vgm6td0HMA8o8guj5PK-eSIWVu9YGT_s"

client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

# ==================== 本地图片库 ====================
LOCAL_IMAGES = [
    "sz1.jpg", "sz2.jpg", "sz3.jpg", "sz4.jpg", "sz5.jpg",
    "sz6.jpg", "sz7.jpg", "sz8.jpg", "sz9.jpg", "sz10.jpg",
    "sz11.jpg", "sz12.jpg", "sz13.jpg", "sz14.jpg", "sz15.jpg",
    "water1.jpg", "street1.jpg",
    "tour1.jpg", "tour2.jpg", "tour3.jpg", "tour4.jpg",
    "tour5.jpg", "tour6.jpg", "tour7.jpg", "tour8.jpg"
]

# ==================== 核心函数 ====================

def download_unsplash_image(query, filename):
    """从 Unsplash 下载一张苏州相关图片"""
    url = f"https://api.unsplash.com/photos/random?query=suzhou+{query}&orientation=landscape&client_id={UNSPLASH_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        img_url = data["urls"]["regular"]
        img_data = requests.get(img_url, timeout=30).content
        filepath = f"public/img/{filename}"
        with open(filepath, "wb") as f:
            f.write(img_data)
        print(f"  📷 Unsplash 下载: {filename}")
        return filename
    except Exception as e:
        print(f"  ⚠️ Unsplash 下载失败，使用本地图片: {e}")
        return None

def get_random_images(count=4):
    """从本地图片库随机选图"""
    available = [img for img in LOCAL_IMAGES if os.path.exists(f"public/img/{img}")]
    if len(available) < count:
        available = LOCAL_IMAGES[:count]
    random.shuffle(available)
    return available[:count]

def generate_tour(topic, images):
    """调用 DeepSeek 生成中文旅游文章"""
    prompt = f"""你是澜青旅行社的苏州旅游内容编辑。请为主题"{topic}"生成一个完整的旅游套餐 .mdx 文件。

严格按以下格式输出，所有文字用中文，正文不少于500字，包含 ## 行程安排 和 ## 行程亮点。

---
title: "关于{topic}的套餐标题"
category: "Cultural Tour"
description: "关于{topic}的一句话描述"
cover: "/img/{images[0]}"

gallery:
  - "/img/{images[0]}"
  - "/img/{images[1]}"
  - "/img/{images[2]}"
  - "/img/{images[3]}"

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

（正文内容）
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是澜青旅行社专业苏州旅游编辑，只输出中文。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        stream=False
    )
    return response.choices[0].message.content

def save_tour(slug, content):
    filepath = f"src/content/tours/{slug}.mdx"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ 已保存: {filepath}")

def git_push(topic):
    """自动推送到 GitHub"""
    print("  🚀 正在推送...")
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", f"自动生成: {topic}"], capture_output=True)
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✅ 推送成功！Cloudflare 自动部署中...")
    else:
        print(f"  ⚠️ 推送失败: {result.stderr}")

# ==================== 主程序 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("  澜青旅行社 - 全自动内容发布系统")
    print("=" * 50)
    
    topic = input("\n📝 输入主题（如：金鸡湖夜景）: ").strip()
    if not topic:
        topic = "苏州旅游"
    
    slug = input("🔗 输入英文 slug（如：jinji-lake）: ").strip()
    if not slug:
        slug = f"suzhou-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"\n🤖 DeepSeek 正在生成「{topic}」...")
    
    # 1. 下载一张新图
    new_img = download_unsplash_image(topic, f"sz-{slug}.jpg")
    
    # 2. 选 4 张图
    images = get_random_images(4)
    if new_img:
        images[0] = new_img
    
    # 3. 生成文章
    content = generate_tour(topic, images)
    save_tour(slug, content)
    
    # 4. 自动推送
    git_push(topic)
    
    print(f"\n🎉 全部完成！2 分钟后访问 travel-suzhou.com/tours/{slug} 查看。")