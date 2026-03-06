import streamlit as st
import researcher
import generator
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AcademiSync Pro", layout="wide")
st.title("🎓 AcademiSync: 深度学术综述生成系统")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 写作配置")
    # 提供高字数选项
    target_words = st.select_slider("目标总字数（AI将按此目标分章扩充）", options=[2000, 5000, 8000], value=5000)
    st.write(f"当前设定：约 {target_words} 字深度综述")
    
    st.header("📄 本地参考")
    uploaded_file = st.file_uploader("上传辅助 PDF/Word (可选)", type=['pdf', 'docx'])

research_title = st.text_input("请输入综述标题：", placeholder="例如：中药通过肠道菌群治疗肺纤维化的机制研究")

if st.button("🚀 开始生成深度综述"):
    if not research_title:
        st.error("请输入标题")
        st.stop()
        
    with st.status("🛠️ 正在执行学术工作流...", expanded=True) as status:
        # 1. 语义分析
        st.write("🧠 正在深度解析课题并提取学术关键词...")
        analysis = generator.analyze_research_title(research_title)
        
        # 2. 检索带 URL 的文献
        st.write("📡 正在检索全球数据库并构建参考文献库...")
        all_papers = []
        # 增加搜索广度以覆盖更多引用
        for kw in analysis.get('en_keywords', [])[:4]:
            results = researcher.fetch_papers(kw, limit=5)
            all_papers.extend(results)
        
        # 3. 构建参考文献索引（核心：保留 URL）
        unique_papers = {p['title']: p for p in all_papers}.values()
        context_data = ""
        ref_list_md = "## 参考文献\n\n"
        
        for i, p in enumerate(unique_papers, 1):
            title = p['title']
            url = p.get('url') or f"https://scholar.google.com/scholar?q={title.replace(' ', '+')}"
            abstract = (p.get('abstract') or "暂无摘要")[:400]
            
            # 注入给 AI 的上下文
            context_data += f"【文献{i}】标题: {title}。摘要: {abstract}\n\n"
            # 生成带超链接的列表
            ref_list_md += f"[{i}] [{title}]({url}). {p.get('year','N/A')}. [点击查看原文] \n\n"

        # 4. 生成超长大纲
        st.write("📋 正在规划万字级学术大纲...")
        outline = generator.generate_outline(research_title, context_data)
        
        # 5. 分章节深度撰写 (核心：分步生成解决字数问题)
        full_draft = f"# {research_title}\n\n{outline}\n\n"
        
        dims = analysis.get('dimensions', ['引言', '机制研究', '临床应用', '总结展望'])
        for dim in dims:
            st.write(f"✍️ 正在深度撰写章节：{dim} (强制扩充字数并插入索引)...")
            # 调用深层生成函数
            chapter_text = generator.generate_chapter_deep(research_title, outline, dim, context_data, target_words)
            full_draft += f"## {dim}\n\n{chapter_text}\n\n"

        # 6. 拼接参考文献
        full_draft += "\n---\n" + ref_list_md
        status.update(label="✅ 深度综述生成成功！", state="complete")

    # 7. 渲染与下载
    st.markdown(full_draft, unsafe_allow_html=True)
    
    doc = Document()
    for line in full_draft.split('\n'):
        if line.strip(): doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 下载完整 Word 文档", bio.getvalue(), file_name=f"{research_title}.docx")
