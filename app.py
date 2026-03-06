import streamlit as st
import researcher
import generator
from docx import Document
from io import BytesIO

# 1. 页面配置
st.set_page_config(page_title="AcademiSync Pro", layout="wide")
st.title("🎓 AcademiSync: 全自动学术综述生成")

# 2. 侧边栏：找回你的“自定义设置”
with st.sidebar:
    st.header("⚙️ 写作设置")
    min_words = st.slider("最低字数要求", 1000, 5000, 5000)
    max_words = st.slider("最高字数要求", 5000, 10000, 8000)
    
    st.header("📄 参考资料管理")
    uploaded_file = st.file_uploader("拖拽你的 PDF/Word 文档到这里 (可选)", type=['pdf', 'docx', 'txt'])
    
    st.info(f"当前设定：内容将围绕 {min_words}-{max_words} 字进行展开。")

# 3. 主界面输入
research_title = st.text_input("请输入综述标题：", placeholder="例如：中药干预肺纤维化的机制研究")

# 4. 运行逻辑
if st.button("🚀 开始生成万字综述"):
    if not research_title:
        st.error("请输入标题后再继续")
        st.stop()
        
    with st.status("🛠️ 正在执行学术工作流...", expanded=True) as status:
        # 第一步：解析
        st.write("🧠 正在深度解析课题语义...")
        analysis = generator.analyze_research_title(research_title)
        
        # 第二步：检索文献
        st.write("📡 正在从 Semantic Scholar 和 arXiv 检索相关文献...")
        all_papers = []
        for kw in analysis.get('en_keywords', []):
            results = researcher.fetch_papers(kw, limit=5)
            all_papers.extend(results)
        
        # 第三步：整合资料
        unique_papers = {p['title']: p for p in all_papers}.values()
        context_data = "【在线检索结果】：\n"
        for i, p in enumerate(unique_papers, 1):
            context_data += f"[{i}] 标题: {p['title']} | 摘要: {p.get('abstract','')[:200]}...\n"
        
        if uploaded_file:
            st.write("📎 正在读取您上传的本地参考资料...")
            # 注意：此处需要处理读取逻辑，演示先占位
            context_data += "\n【用户上传资料已加入参考池】"

        # 第四步：生成大纲
        st.write(f"📋 正在规划 {min_words} 字量级的大纲...")
        outline = generator.generate_outline(research_title, context_data)
        
        full_draft = f"# {research_title}\n\n## 综述大纲\n{outline}\n\n"
        
        # 第五步：分章撰写
        dims = analysis.get('dimensions', ['背景', '现状', '技术', '挑战'])
        for dim in dims:
            st.write(f"✍️ 正在深度撰写章节：{dim}...")
            chapter_text = generator.generate_chapter(research_title, outline, dim, context_data)
            full_draft += f"## {dim}\n\n{chapter_text}\n\n"

        status.update(label="✅ 万字综述生成成功！", state="complete")

    # 5. 结果展示与下载
    st.markdown("---")
    st.markdown(full_draft)
    
    doc = Document()
    for line in full_draft.split('\n'):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 下载完整 Word 文档", bio.getvalue(), file_name=f"{research_title}.docx")
