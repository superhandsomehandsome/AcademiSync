def get_client():
    # 确保智谱调用不受全局代理影响
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    os.environ.setdefault("NO_PROXY", "open.bigmodel.cn,api.zhipu.ai")

    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        raise ValueError("未在环境变量或 .env 中找到 ZHIPUAI_API_KEY")
    return ZhipuAI(api_key=api_key)
  def analyze_research_title(title):
    client = get_client()
    prompt = f"""
    你是一个学术搜索专家。请分析标题内容：{title}

    任务：
    1. 去掉所有无意义的词（如：研究、讨论、通过、探讨、分析）。
    2. 提取核心学术概念，并翻译成标准的英文术语。
    3. 给出3个独立的英文关键词（用于API检索）。

    例如标题“中药通过肠道菌群治疗肺纤维化”，你应该提取：
    ["Traditional Chinese Medicine", "Gut microbiota", "Pulmonary fibrosis"]

    请严格以 JSON 格式输出：
    {{
        "en_keywords": ["keyword1", "keyword2", "keyword3"],
        "dimensions": ["研究背景", "作用机制", "临床应用", "未来挑战"]
    }}
    """
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
    def generate_outline(title, paper_data):
    """第二步：根据文献规划万字大纲"""
    client = get_client()
    prompt = (
        f"针对课题《{title}》，基于以下文献线索：{paper_data}，规划一份8000字综述的详细大纲（至三级标题）。"
    )
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
    def generate_chapter(title, outline, chapter_title, paper_data):
    """第三步：深度扩写章节，严格要求字数与文献引用"""
    client = get_client()
    prompt = f"""
正在撰写《{title}》。请扩写【{chapter_title}】章节。
参考大纲：{outline}
参考文献：{paper_data}
要求：
1. 严谨学术风，字数1500字左右。
2. 必须在文中通过 [作者, 年份] 或 [编号] 形式引用上述文献。
3. 直接输出正文。
"""
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
