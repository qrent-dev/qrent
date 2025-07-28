import streamlit as st


def show_report_interface(key_prefix=""):
    """显示报告生成界面"""
    st.title("🏠 租房报告")
    st.markdown("---")
    
    # 设置页面为全宽模式
    st.markdown("""
    <style>
    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: none;
    }
    .stMarkdown {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.report_agent:
        st.error("报告生成Agent未能正确初始化，请刷新页面重试。")
        return
    
    # 检查数据可用性
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("报告生成")
        
        # 显示数据源状态
        st.markdown("### 数据源状态")
        
        data_status = {
            "问卷数据": bool(st.session_state.questionnaire_data),
            "对话历史": bool(st.session_state.history),
            "智能分析": bool(st.session_state.inquiry_agent and hasattr(st.session_state.inquiry_agent, 'conversation_history')),
        }
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            icon = "🔍" if data_status["问卷数据"] else "❌"
            st.metric("问卷数据", icon, "可用" if data_status["问卷数据"] else "不可用")
        
        with status_col2:
            icon = "🔍" if data_status["对话历史"] else "❌"
            st.metric("对话历史", icon, f"{len(st.session_state.history)//2}轮" if data_status["对话历史"] else "无")
        
        with status_col3:
            inquiry_history = getattr(st.session_state.inquiry_agent, 'conversation_history', []) if st.session_state.inquiry_agent else []
            icon = "🔍" if inquiry_history else "❌"
            st.metric("智能分析", icon, f"{len(inquiry_history)//2}轮" if inquiry_history else "无")
        
        st.markdown("---")
        
        # 数据完整性检查
        data_complete = any(data_status.values())
        
        if not data_complete:
            st.warning(" 暂无足够数据生成报告。请先：")
            st.markdown("""
            - 填写需求问卷，或
            - 在对话助手中提出租房需求，或
            - 使用智能追问模式进行需求分析
            """)
            
            # 提供快速导航
            nav_col1, nav_col2 = st.columns(2)
            with nav_col1:
                if st.button("📝 前往填写问卷", type="primary", key=f"{key_prefix}nav_to_questionnaire"):
                    st.info("👆 请点击页面顶部的 '📋 需求问卷' 标签页")
            
            with nav_col2:
                if st.button("💬 前往对话助手", type="secondary", key=f"{key_prefix}nav_to_chat"):
                    st.info("👆 请点击页面顶部的 '💬 对话助手' 标签页")
        
        else:
            # 更新报告Agent的数据
            if st.session_state.report_agent:
                inquiry_history = getattr(st.session_state.inquiry_agent, 'conversation_history', []) if st.session_state.inquiry_agent else []
                
                st.session_state.report_agent.update_user_data(
                    questionnaire_data=st.session_state.questionnaire_data,
                    main_agent_history=st.session_state.history,
                    inquiry_agent_history=inquiry_history
                )
            
            st.markdown("### 可用报告类型")
            
            # 报告类型选择
            report_type = st.radio(
                "选择报告类型：",
                ["执行摘要", "详细分析报告", "行动计划"],
                help="不同类型的报告提供不同程度的详细信息",
                key=f"{key_prefix}report_type_radio"
            )
            
            # 语言选择
            language = st.selectbox(
                "报告语言：",
                ["自动检测", "中文", "English"],
                help="选择报告生成的语言",
                key=f"{key_prefix}report_language_select"
            )
            
            language_map = {
                "自动检测": None,
                "中文": "chinese", 
                "English": "english"
            }
            
            selected_language = language_map[language]
            
            # 生成报告按钮
            if st.button("📊 生成报告", type="primary", key=f"{key_prefix}generate_report_button"):
                with st.spinner("正在生成报告，请稍候..."):
                    try:
                        if report_type == "执行摘要":
                            report_content = st.session_state.report_agent.generate_executive_summary(selected_language)
                        elif report_type == "详细分析报告":
                            report_content = st.session_state.report_agent.generate_detailed_report(selected_language)
                        elif report_type == "行动计划":
                            priority = st.selectbox(
                                "优先级策略：",
                                ["均衡考虑", "快速入住优先", "预算优先", "房源质量优先"],
                                key=f"{key_prefix}priority_select"
                            )
                            priority_map = {
                                "均衡考虑": "balanced",
                                "快速入住优先": "fast",
                                "预算优先": "budget",
                                "房源质量优先": "quality"
                            }
                            report_content = st.session_state.report_agent.generate_action_plan(
                                priority=priority_map[priority], 
                                language=selected_language
                            )
                        
                        # 显示生成的报告
                        st.success("报告生成完成！")
                        st.markdown("---")
                        
                        # 报告展示区域
                        st.markdown("### 生成的报告")
                        
                        # 使用容器来显示报告
                        report_container = st.container()
                        with report_container:
                            st.markdown(report_content)
                        
                        # 报告操作按钮
                        st.markdown("---")
                        st.markdown("### 报告操作")
                        
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button("📋 复制报告", key=f"{key_prefix}copy_report"):
                                # 这里可以添加复制到剪贴板的功能
                                st.info("💡 您可以选中报告内容进行复制")
                        
                        with action_col2:
                            if st.button("📤 分享报告", key=f"{key_prefix}share_report"):
                                st.info("📧 您可以将报告内容复制并通过邮件或其他方式分享")
                        
                        with action_col3:
                            if st.button("🔄 重新生成", key=f"{key_prefix}regenerate_report"):
                                st.rerun()
                        
                        # 报告元数据
                        with st.expander("报告元数据", expanded=False):
                            metadata = st.session_state.report_agent.get_report_metadata()
                            st.json(metadata)
                        
                    except Exception as e:
                        st.error(f"报告生成失败: {e}")
                        st.error("请稍后重试，或检查数据完整性。")
    
    with col2:
        st.header("报告说明")
        
        # 报告类型说明
        with st.expander("报告类型说明", expanded=True):
            st.markdown("""
            **执行摘要:**
            - 简洁的需求概述
            - 预算分析
            - 核心推荐方案
            - 主要风险提示
            
            **详细分析报告:**
            - 完整的用户画像
            - 深入的需求分析
            - 市场调研结果
            - 详细房源推荐
            - 区域对比分析
            - 费用详细估算
            - 完整行动计划
            
            **行动计划:**
            - 具体执行步骤
            - 时间规划
            - 优先级排序
            - 风险控制
            - 备选方案
            """)
        
        # 数据完整性说明
        with st.expander("提高报告质量", expanded=True):
            st.markdown("""
            **为了获得更好的报告质量，建议：**
            
            1. **完整填写问卷** - 提供基础需求信息
            2. **多轮对话交流** - 与AI助手深入讨论需求
            3. **使用智能追问** - 让AI帮您分析需求合理性
            4. **提供具体信息** - 详细描述预算、地区、房型等
            
            **报告质量评分因素：**
            - 数据完整性 (70%)
            - 区域分析结果 (10%)
            - 对话交流深度 (10%) 
            - 需求分析详细度 (10%)
            """)
        
        # 使用建议
        with st.expander("使用建议", expanded=False):
            st.markdown("""
            **最佳使用流程：**
            
            1. 先在问卷页填写基本需求
            2. 在对话助手中详细讨论
            3. 开启智能追问模式优化需求
            4. 最后生成综合报告
            
            **注意事项：**
            - 报告基于已有数据生成
            - 建议在需求明确后再生成
            - 可多次生成不同类型报告
            - 报告内容仅供参考
            """) 