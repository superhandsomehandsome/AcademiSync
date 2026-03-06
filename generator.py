import json
from zhipuai import ZhipuAI
import streamlit as st

def get_client():
    """从 Streamlit Secrets 安全获取 API Key"""
    if "ZHIPUAI_API_KEY" not in st.secrets:
        st.error("未在 Secrets 中找到 ZHIPUAI_API_KEY，请检查设置。")
        st.stop()
    api_key = st.secrets["ZHIPUAI_API_KEY"]
    return ZhipuAI(api_key=api_key)

def analyze_research_title(title):
    """分析标题并提取英文关键词和研究维度"""
    client = get_client()
    prompt = f"分析标题《{title}》，输出3个核心英文学术关键词和4个研究维度。以JSON格式返回，格式为: {{\"en_keywords\": [], \"dimensions\": []}}"
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def generate_outline(title, paper_data):
    """根据文献资料生成论文大纲"""
    client = get_client()
    prompt = f"针对课题《{title}》，参考以下文献资料：\n{paper_data}\n请生成一份详细的综述大纲。"
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_chapter(title, outline, chapter, paper_data):
    """撰写具体的章节内容"""
    client = get_client()
    prompt = f"撰写《{title}》的章节：{chapter}。参考大纲：\n{outline}\n参考资料：\n{paper_data}\n要求：学术风格，不少于1000字。"
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
