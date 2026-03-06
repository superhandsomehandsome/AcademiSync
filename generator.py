import json
from zhipuai import ZhipuAI
import streamlit as st

def get_client():
    return ZhipuAI(api_key=st.secrets["ZHIPUAI_API_KEY"])

def analyze_research_title(title):
    client = get_client()
    prompt = f"分析标题《{title}》，输出3个核心英文关键词和4个研究维度。JSON格式: {{\"en_keywords\": [], \"dimensions\": []}}"
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def generate_outline(title, context):
    client = get_client()
    prompt = f"针对《{title}》，参考以下文献库：\n{context}\n请生成一份学术综述大纲。"
    response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

def generate_chapter(title, outline, chapter, context, target_words):
    client = get_client()
    # 核心指令：强制字数和索引
    prompt = f"""
    你是一名资深教授。请撰写《{title}》的章节：{chapter}。
    要求：
    1. 字数：本章不少于 {target_words // 4} 字。
    2. 引用：**必须**在正文观点后标注参考文献编号，如 [1] 或 [2]。
    3. 深度：基于以下文献摘要进行分析，禁止空谈：
    {context}
    """
    response = client.chat.completions.create(model="glm-4", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content
