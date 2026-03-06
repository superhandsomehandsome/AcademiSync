import json
from zhipuai import ZhipuAI
import streamlit as st

def get_client():
    return ZhipuAI(api_key=st.secrets["ZHIPUAI_API_KEY"])

def analyze_research_title(title):
    client = get_client()
    prompt = f"分析标题《{title}》，输出4个英文学术关键词和5个研究维度。以JSON格式返回: {{\"en_keywords\": [], \"dimensions\": []}}"
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def generate_outline(title, context):
    client = get_client()
    prompt = f"针对课题《{title}》，参考以下文献：\n{context}\n生成一份包含二级标题的深度学术综述大纲。"
    response = client.chat.completions.create(model="glm-4-flash", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

def generate_chapter_deep(title, outline, chapter, context, target_words):
    """
    深度生成函数：
    1. 强制分章字数
    2. 强制插入文献编号索引 [i]
    """
    client = get_client()
    # 计算本章应分摊的字数（例如总5000字，5个章节，每章1000字）
    chapter_min = target_words // 5
    
    prompt = f"""
    你是一名严谨的医学教授。请撰写综述《{title}》中的“{chapter}”章节。
    
    【参考大纲】：
    {outline}
    
    【提供的参考文献库】：
    {context}
    
    【写作指令】：
    1. **字数扩充**：本章内容必须极其详尽，字数需超过 {chapter_min} 字。请通过深度探讨分子路径、实验数据对比、病理机制来扩充内容。
    2. **精准引用**：在文中提及相关观点、数据或结论时，**必须**在末尾标注参考文献编号，例如 [1] 或 [2]。
    3. **专业格式**：使用学术语言，适当使用子标题（如 2.1, 2.2）。
    4. **要求**：禁止空谈，必须基于提供的文献摘要进行延伸。
    """
    # 必须使用强模型（glm-4）以支持长文本逻辑
    response = client.chat.completions.create(
        model="glm-4", 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
