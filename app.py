import streamlit as st
import researcher
import generator
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AcademiSync Pro", layout="wide")
st.title("🎓 AcademiSync: 全自动学术综述生成")

# 侧边栏：功能完全回归
with st.sidebar:
    st.header("⚙️ 写作配置")
    target_words = st.select_slider("目标总字数范围", options=[2000, 5000, 8000], value=5000)
    st.write(f"已设定：{target_words} 字量级")
    
    st.header("📄 参考文献管理")
    uploaded_file = st.file_uploader("上传本地 PDF/Word 文档 (可选)", type=['pdf', 'docx', 'txt'])
    st.info("系统将优先检索在线文献，并结合您上传的资料。")

research_title = st.text_input("请输入综述标题：", placeholder="例如：中药干预肺纤维化的机制研究")

if st.button("🚀 开始生成深度综述"):
    if not research_title:
        st.error("请输入标题后再继续")
        st.stop()
        
    with st.status("🛠️ 正在执行学术工作流...", expanded=True) as status:
        # 第一步：深度解析
        st.write("🧠 正在解析课题并提取学术关键词...")
        analysis = generator.analyze_research_title(research_title)
        
        # 第二步：检索带摘要的文献
        st.write("📡 正在全网检索高质量文献摘要...")
        all_papers = []
        for kw in analysis.get('en_keywords', [])[:3]: # 取前3个关键词检索
            results = researcher.fetch_papers(kw, limit=4)
            all_papers.extend(results)
        
        # 第三步：构建参考文献索引库
        unique_papers = {p['title']: p for p in all_papers}.values()
        context_data = ""
        ref_list_html = "### 📚 参考文献列表\n"
        
        for i, p in enumerate(unique_papers, 1):
            # 将编号 [i] 强行注入上下文，方便 AI 引用
            context_data += f"【文献{i}】标题: {p['title']}。摘要: {(p.get('abstract') or '')[:300]}\n\n"
            ref_list_html += f"[{i}] {p['title']}. ({p.get('year','N/A')}). [来源: {p.get('source','网络')}]\n\n"

        # 第四步：分章撰写（解决字数短的问题）
        st.write("📋 正在规划大纲并分章撰写内容...")
        outline = generator.generate_outline(research_title, context_data)
        
        full_draft = f"# {research_title}\n\n{outline}\n\n"
        
        # 核心：循环生成每一个章节，确保总字数
        for dim in analysis.get('dimensions', ['引言', '核心技术', '挑战与展望']):
            st.write(f"✍️ 正在撰写章节：{dim} (包含文献引用)...")
            chapter_text = generator.generate_chapter(research_title, outline, dim, context_data, target_words)
            full_draft += f"## {dim}\n\n{chapter_text}\n\n"

        # 第五步：合并文献列表
        full_draft += "\n---\n" + ref_list_html
        status.update(label="✅ 生成成功！", state="complete")

    # 展示与下载
    st.markdown(full_draft)
    
    doc = Document()
    for line in full_draft.split('\n'):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 下载 Word 文档", bio.getvalue(), file_name=f"{research_title}.docx")
