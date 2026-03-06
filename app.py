st.set_page_config(page_title="AcademiSync Ultra", layout="wide")

st.title("🎓 全自动学术研究系统")
# 侧边栏：API Key 与参数
with st.sidebar:
    st.header("配置")
    default_key = os.getenv("ZHIPUAI_API_KEY", "")
    api_key = st.text_input("智谱 API Key", value=default_key, type="password")
    num_papers = st.slider("每个关键词检索篇数", 3, 20, 5)
    uploaded_files = st.file_uploader(
        "可选：上传本地中文文献（txt/md）以增强内容",
        type=["txt", "md"],
        accept_multiple_files=True,
    )
    show_debug = st.checkbox("显示调试信息", value=False)
  research_title = st.text_input(
    "请输入综述标题（AI将自动理解并搜寻文献）：",
    placeholder="例如：中药干预糖尿病肾病的效果及分子机制研究进展",
)
if st.button("🚀 启动全链路写作", type="primary"):
    if not research_title:
        st.error("请输入标题")
        st.stop()

    if api_key:
        os.environ["ZHIPUAI_API_KEY"] = api_key
          with st.status("🛠️ 正在执行学术工作流...", expanded=True) as status:
        # 1. 语义解析
        st.write("🧠 正在深度解析课题语义...")
        analysis = generator.analyze_research_title(research_title)
        en_keywords = analysis.get("en_keywords", [])

        if not en_keywords:
            en_keywords = [research_title]

        # 2. 自动化多路搜索
        st.write("📡 正在全网检索相关文献（双引擎驱动）...")
        all_papers = []
        for kw in en_keywords:
            st.write(f"🔍 正在检索核心概念: {kw}...")
            try:
                results = researcher.fetch_papers(kw, limit=num_papers)
            except Exception as e:
                st.warning(f"检索关键词 {kw} 时出现错误：{e}")
                results = []
            all_papers.extend(results or [])

        # 可选：合并本地上传的中文文献
        if uploaded_files:
            st.write("📂 正在合并本地上传的中文文献...")
            # ... 追加到 all_papers ...

        # 文献去重
        unique_map = {}
        for p in all_papers:
            title = (p.get("title") or "").strip()
            if not title:
                continue
            if title not in unique_map:
                unique_map[title] = p
        unique_papers = list(unique_map.values())

        if not unique_papers:
            status.update(
                label="❌ 所有数据库均未找到结果，请更换关键词。", state="error"
            )
            st.stop()

        st.success(f"✅ 找到 {len(unique_papers)} 篇高度相关的参考资料！")

        # 3. 规划与写作（支持断点续写）
        st.write("📋 正在生成或更新万字学术大纲...")
        outline = generator.generate_outline(research_title, context_data)

        # 加载/更新 draft_state，按 dimensions 循环
        draft_state = load_draft_state()
        if draft_state.get("title") != research_title:
            draft_state = { "title": research_title, "outline": outline, "dimensions": ..., "chapters": {} }
        dimensions = draft_state.get("dimensions", ...)
        chapters = draft_state.get("chapters", {})

        full_draft = f"# {research_title}\n\n{outline}\n\n"
        for dim in dimensions:
            if dim in chapters:
                st.write(f"⏩ 已存在章节，跳过重新生成：{dim}")
                chapter_text = chapters[dim]
            else:
                st.write(f"✍️ 正在撰写深度章节：{dim}...")
                chapter_text = generator.generate_chapter(...)
                chapters[dim] = chapter_text
                save_draft_state(draft_state)
            full_draft += f"## {dim}\n\n{chapter_text}\n\n"

        # 保存 temp_draft.md
        # 4. 审稿润色
        st.write("✨ 正在进行 AI 专家级润色...")
        polished_text = generator.polish_review(full_draft)
        final_text = polished_text + "\n\n---\n" + ref_list

        status.update(label="✅ 生成成功！", state="complete")
          # 结果展示
    st.markdown(final_text)

    # 引用对齐检查
    citation_report = check_citations(final_text, ref_count=len(unique_papers))

    # 下载 Word
    doc = Document()
    for line in final_text.split("\n"):
        doc.add_paragraph(line)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    st.download_button(
        "📥 下载完整综述 (Word)",
        data=bio.getvalue(),
        file_name="Review.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    if show_debug:
        with st.expander("调试信息（标题分析、原始文献与引用校验）", expanded=False):
            st.write("标题分析结果：", analysis)
            st.write("文献条目数：", len(unique_papers))
            st.write("引用校验报告：", citation_report)
