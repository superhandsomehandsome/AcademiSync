import streamlit as st
import researcher
import generator
from docx import Document
from io import BytesIO

# 1. 页面配置
st.set_page_config(page_title="AcademiSync", layout="wide")
st.title("🎓 AcademiSync: 全自动学术综述生成")

# 2. 用户输入
research_title = st.text_input("请输入综述标题：", placeholder="例如：中药干预肺纤维化的机制研究")

# 3. 运行逻辑
if st.button("🚀 开始研究"):
    if not research_title:
        st.error("请输入标题后再继续")
        st.stop()
        
    with st.status("🛠️ 正在执行学术工作流...", expanded=True) as status:
        st.write("🧠 正在深度解析课题语义...")
        analysis = generator.analyze_research_title(research_title)
        
        st.write("📡 正在全网检索相关文献...")
        all_papers = []
        for kw in analysis.get('en_keywords', []):
            results = researcher.fetch_papers(kw, limit=5)
            all_papers.extend(results)
        
        # 简单去重
        unique_papers = {p['title']: p for p in all_papers}.values()
        context_data = ""
        for i, p in enumerate(unique_papers, 1):
            context_data += f"[{i}] {p['title']}\n"

        st.write("📋 正在生成万字学术大纲...")
        outline = generator.generate_outline(research_title, context_data)
        
        full_draft = f"# {research_title}\n\n{outline}\n\n"
        
        # 撰写章节
        for dim in analysis.get('dimensions', ['引言', '核心技术', '挑战与展望']):
            st.write(f"✍️ 正在撰写章节：{dim}...")
            chapter_text = generator.generate_chapter(research_title, outline, dim, context_data)
            full_draft += f"## {dim}\n\n{chapter_text}\n\n"

        status.update(label="✅ 生成成功！", state="complete")

    # 4. 结果展示
    st.markdown(full_draft)
    
    # 5. 下载 Word
    doc = Document()
    for line in full_draft.split('\n'):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 下载 Word 文档", bio.getvalue(), file_name="Review.docx")
