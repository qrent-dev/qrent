import streamlit as st
from datetime import datetime, timedelta

def init_questionnaire_state():
    """初始化问卷相关的session state"""
    if 'questionnaire_step' not in st.session_state:
        st.session_state.questionnaire_step = 1

    if 'questionnaire_data' not in st.session_state:
        st.session_state.questionnaire_data = {
            'budget_min': None,
            'budget_max': None,
            'includes_bills': None,
            'includes_furniture': None,
            'total_budget': None,
            'room_type': None,
            'consider_sharing': None,
            'commute_time': None,
            'move_in_date': None,
            'lease_duration': None,
            'accept_premium': None,
            'accept_small_room': None
        }

def format_questionnaire_data(data):
    """将问卷数据格式化为文本"""
    formatted_text = f"""
## 租房需求问卷信息

### 预算信息
- 预算范围：${data['budget_min']} - ${data['budget_max']} 澳元/周
- 是否包含Bills（水电网）：{data['includes_bills']}
- 是否包含家具：{data['includes_furniture']}
- 总开销预期：${data['total_budget']} 澳元/周

### 房型偏好
- 目标房型：{data['room_type']}
- 是否考虑合租：{data['consider_sharing']}

### 其他要求
- 通勤时间上限：{data['commute_time']}
- 最早入住日期：{data['move_in_date']}
- 期望租期：{data['lease_duration']}
- 接受高溢价房源：{data['accept_premium']}
- 接受房间较小的房源：{data['accept_small_room']}

请根据以上信息，为我推荐合适的房源并提供详细的租房建议。
"""
    return formatted_text

def show_questionnaire_step(step, key_prefix=""):
    """显示问卷的指定步骤"""
    if step == 1:
        st.markdown("### 第1步，共6步")
        st.progress(1/6)
        st.markdown("## 您的租房预算是多少？")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**最低预算（AUD/周）**")
            st.session_state.questionnaire_data['budget_min'] = st.number_input(
                "最低预算",
                min_value=0,
                max_value=3000,
                value=st.session_state.questionnaire_data['budget_min'] or 300,
                step=50,
                key=f"{key_prefix}budget_min_input"
            )
        
        with col2:
            st.markdown("**最高预算（AUD/周）**")
            st.session_state.questionnaire_data['budget_max'] = st.number_input(
                "最高预算",
                min_value=0,
                max_value=3000,
                value=st.session_state.questionnaire_data['budget_max'] or 800,
                step=50,
                key=f"{key_prefix}budget_max_input"
            )
        
        st.markdown("**预算是否包含Bills（水电网费）？**")
        bills_options = ['包含', '不包含', '不确定']
        bills_default_idx = bills_options.index(st.session_state.questionnaire_data['includes_bills']) if st.session_state.questionnaire_data['includes_bills'] in bills_options else 2
        st.session_state.questionnaire_data['includes_bills'] = st.radio(
            "Bills包含情况",
            options=bills_options,
            index=bills_default_idx,
            horizontal=True,
            key=f"{key_prefix}bills_radio"
        )
        
        st.markdown("**预算是否包含家具？**")
        furniture_options = ['包含', '不包含', '不确定']
        furniture_default_idx = furniture_options.index(st.session_state.questionnaire_data['includes_furniture']) if st.session_state.questionnaire_data['includes_furniture'] in furniture_options else 2
        st.session_state.questionnaire_data['includes_furniture'] = st.radio(
            "家具包含情况",
            options=furniture_options,
            index=furniture_default_idx,
            horizontal=True,
            key=f"{key_prefix}furniture_radio"
        )
        
        st.markdown("**总开销预期（包含生活费，AUD/周）**")
        st.session_state.questionnaire_data['total_budget'] = st.number_input(
            "总开销预期",
            min_value=0,
            max_value=5000,
            value=st.session_state.questionnaire_data['total_budget'] or 1200,
            step=100,
            help="包括房租、生活费、交通费等所有开销",
            key=f"{key_prefix}total_budget_input"
        )
    
    elif step == 2:
        st.markdown("### 第2步，共6步")
        st.progress(2/6)
        st.markdown("## 您的目标房型是什么？")
        
        st.markdown("**房型偏好**")
        room_types = ['Studio', '1 Bedroom', '2 Bedroom', '3+ Bedroom', '合租房间', '不确定']
        room_default_idx = room_types.index(st.session_state.questionnaire_data['room_type']) if st.session_state.questionnaire_data['room_type'] in room_types else 5
        st.session_state.questionnaire_data['room_type'] = st.radio(
            "房型选择",
            options=room_types,
            index=room_default_idx,
            key=f"{key_prefix}room_type_radio"
        )
        
        st.markdown("**如果是Studio或1 Bedroom，是否考虑合租？**")
        sharing_options = ['愿意考虑', '不考虑', '视情况而定']
        sharing_default_idx = sharing_options.index(st.session_state.questionnaire_data['consider_sharing']) if st.session_state.questionnaire_data['consider_sharing'] in sharing_options else 2
        st.session_state.questionnaire_data['consider_sharing'] = st.radio(
            "合租考虑",
            options=sharing_options,
            index=sharing_default_idx,
            horizontal=True,
            key=f"{key_prefix}sharing_radio"
        )
    
    elif step == 3:
        st.markdown("### 第3步，共6步")
        st.progress(3/6)
        st.markdown("## 通勤时间要求")
        
        st.markdown("**您能够接受的通勤时间上限是？**")
        commute_options = ['15分钟以内', '30分钟以内', '45分钟以内', '1小时以内', '1小时以上', '没有要求']
        commute_default_idx = commute_options.index(st.session_state.questionnaire_data['commute_time']) if st.session_state.questionnaire_data['commute_time'] in commute_options else 5
        st.session_state.questionnaire_data['commute_time'] = st.radio(
            "通勤时间",
            options=commute_options,
            index=commute_default_idx,
            key=f"{key_prefix}commute_radio"
        )
    
    elif step == 4:
        st.markdown("### 第4步，共6步")
        st.progress(4/6)
        st.markdown("## 入住时间与租期")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**最早可入住日期**")
            default_move_in_date = st.session_state.questionnaire_data['move_in_date'] if st.session_state.questionnaire_data['move_in_date'] is not None else datetime.now().date() + timedelta(days=30)
            st.session_state.questionnaire_data['move_in_date'] = st.date_input(
                "入住日期",
                value=default_move_in_date,
                min_value=datetime.now().date(),
                key=f"{key_prefix}move_in_date_input"
            )
        
        with col2:
            st.markdown("**期望租期（月）**")
            lease_options = ['不确定', '3个月', '6个月', '9个月', '12个月', '18个月', '24个月', '长期']
            lease_default_idx = lease_options.index(st.session_state.questionnaire_data['lease_duration']) if st.session_state.questionnaire_data['lease_duration'] in lease_options else 0
            st.session_state.questionnaire_data['lease_duration'] = st.selectbox(
                "租期选择",
                options=lease_options,
                index=lease_default_idx,
                key=f"{key_prefix}lease_duration_select"
            )
    
    elif step == 5:
        st.markdown("### 第5步，共6步")
        st.progress(5/6)
        st.markdown("## 接受度评估")
        
        st.markdown("**能否接受高溢价房源？**")
        premium_options = ['可以接受', '不能接受', '视房源质量而定']
        premium_default_idx = premium_options.index(st.session_state.questionnaire_data['accept_premium']) if st.session_state.questionnaire_data['accept_premium'] in premium_options else 2
        st.session_state.questionnaire_data['accept_premium'] = st.radio(
            "高溢价房源",
            options=premium_options,
            index=premium_default_idx,
            horizontal=True,
            key=f"{key_prefix}premium_radio"
        )
        
        st.markdown("**能否接受房间较小的房源？**")
        small_room_options = ['可以接受', '不能接受', '视具体情况而定']
        small_room_default_idx = small_room_options.index(st.session_state.questionnaire_data['accept_small_room']) if st.session_state.questionnaire_data['accept_small_room'] in small_room_options else 2
        st.session_state.questionnaire_data['accept_small_room'] = st.radio(
            "小房间房源",
            options=small_room_options,
            index=small_room_default_idx,
            horizontal=True,
            key=f"{key_prefix}small_room_radio"
        )
    
    elif step == 6:
        st.markdown("### 第6步，共6步")
        st.progress(6/6)
        st.markdown("## 信息确认")
        
        data = st.session_state.questionnaire_data
        
        # 显示预算信息
        st.markdown("### 预算信息")
        budget_min_display = data['budget_min'] if data['budget_min'] is not None else "未设置"
        budget_max_display = data['budget_max'] if data['budget_max'] is not None else "未设置"
        total_budget_display = data['total_budget'] if data['total_budget'] is not None else "未设置"
        st.info(f"""
        **预算范围：** ${budget_min_display} - ${budget_max_display}/周  
        **是否包含Bills：** {data['includes_bills'] or "未选择"}  
        **是否包含家具：** {data['includes_furniture'] or "未选择"}  
        **总开销预期：** ${total_budget_display}/周
        """)
        
        # 显示房型偏好
        st.markdown("### 房型偏好")
        st.info(f"**目标房型：** {data['room_type'] or '未选择'}")
        
        # 显示其他要求
        st.markdown("### 其他要求")
        st.info(f"""
        **通勤时间上限：** {data['commute_time'] or "未选择"}  
        **最早入住日期：** {data['move_in_date'] or "未设置"}  
        **期望租期：** {data['lease_duration'] or "未选择"}  
        **接受高溢价：** {data['accept_premium'] or "未选择"}  
        **接受小房间：** {data['accept_small_room'] or "未选择"}
        """)

def reset_questionnaire_data():
    """重置问卷数据"""
    st.session_state.questionnaire_step = 1
    st.session_state.questionnaire_data = {
        'budget_min': None,
        'budget_max': None,
        'includes_bills': None,
        'includes_furniture': None,
        'total_budget': None,
        'room_type': None,
        'consider_sharing': None,
        'commute_time': None,
        'move_in_date': None,
        'lease_duration': None,
        'accept_premium': None,
        'accept_small_room': None
    }

def show_questionnaire(key_prefix=""):
    """显示问卷界面"""
    st.title("📋 Qrent 租房需求问卷")
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
    
    # 显示当前步骤
    show_questionnaire_step(st.session_state.questionnaire_step, key_prefix)
    
    # 导航按钮
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.session_state.questionnaire_step > 1:
            if st.button("上一步", key=f"{key_prefix}prev_step"):
                st.session_state.questionnaire_step -= 1
                st.rerun()
    
    with col2:
        if st.session_state.questionnaire_step < 6:
            if st.button("下一步", key=f"{key_prefix}next_step"):
                st.session_state.questionnaire_step += 1
                st.rerun()
        else:
            if st.button("开始找房", type="primary", key=f"{key_prefix}start_search"):
                return handle_questionnaire_submission(key_prefix)
    
    return None

def handle_questionnaire_submission(key_prefix=""):
    """处理问卷提交"""
    # 将问卷数据格式化并传递给agent
    formatted_query = format_questionnaire_data(st.session_state.questionnaire_data)
    
    # 显示加载状态
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("正在分析您的需求...")
    progress_bar.progress(20)
    
    try:
        # 调用Agent处理问卷信息
        status_text.text("正在搜索房源数据库...")
        progress_bar.progress(60)
        
        result = st.session_state.agent.process_query(formatted_query, 5)
        
        status_text.text("正在生成个性化推荐...")
        progress_bar.progress(90)
        
        # 更新session state中的历史
        st.session_state.history = result['history']
        
        progress_bar.progress(100)
        status_text.text("分析完成！")
        
        # 清除进度条
        progress_bar.empty()
        status_text.empty()
        
        # 显示成功提示
        st.success("? 问卷分析完成！")
        
        # 创建结果展示区域
        st.markdown("---")
        
        # 标题区域 - 使用与问卷相同的宽度
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            margin: 20px 0;
            text-align: center;
            box-sizing: border-box;
        ">
            <h2 style="color: white; margin: 0; font-size: 24px;">
                ? 基于您的问卷，AI助手为您推荐
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 数据库查询结果区域
        if result.get('function_results'):
            st.markdown("### ? 数据库查询结果")
            
            # 创建查询结果卡片 - 使用一致的宽度
            for i, func_result in enumerate(result['function_results']):
                # 使用简洁的卡片样式
                if 'error' in func_result:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                        padding: 20px;
                        border-radius: 12px;
                        margin: 15px 0;
                        border-left: 5px solid #f44336;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        box-sizing: border-box;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="font-size: 24px; margin-right: 15px;">?</div>
                            <div style="font-weight: bold; color: #c62828; font-size: 18px;">
                                {func_result['name']}
                            </div>
                        </div>
                        <div style="color: #d32f2f; font-size: 14px;">
                            {func_result['error']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                        padding: 20px;
                        border-radius: 12px;
                        margin: 15px 0;
                        border-left: 5px solid #4caf50;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        box-sizing: border-box;
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="font-size: 24px; margin-right: 15px;">?</div>
                            <div style="font-weight: bold; color: #2e7d32; font-size: 18px;">
                                {func_result['name']} - 查询成功
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'result' in func_result:
                        func_res = func_result['result']
                        
                        # 详细结果展示
                        if 'analysis_results' in func_res:
                            st.info(f"? 已分析 **{len(func_res['analysis_results'])}** 个区域的房源情况")
                            
                            # 显示区域分析摘要
                            if len(func_res['analysis_results']) > 0:
                                with st.expander("查看区域分析详情", expanded=False):
                                    for area_result in func_res['analysis_results'][:3]:  # 只显示前3个
                                        st.markdown(f"**{area_result.get('area', 'N/A')}**: 平均价格 ${area_result.get('avg_price', 'N/A')}/周")
                        
                        elif 'properties' in func_res:
                            property_count = func_res.get('count', 0)
                            st.info(f"? 找到 **{property_count}** 套符合条件的房源")
                            
                            # 显示房源摘要
                            if property_count > 0:
                                with st.expander("查看房源概览", expanded=False):
                                    properties = func_res.get('properties', [])
                                    for prop in properties[:3]:  # 只显示前3个
                                        st.markdown(f"? **{prop.get('suburb', 'N/A')}** - ${prop.get('price', 'N/A')}/周 - {prop.get('property_type', 'N/A')}")
                
                st.markdown("---")
        
        # 引导用户到对话助手页面
        st.markdown("### ? 个性化推荐结果")
        
        # 引导信息卡片 - 使用与问卷相同的宽度
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            padding: 30px;
            border-radius: 12px;
            margin: 20px 0;
            border: 2px solid #4caf50;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            box-sizing: border-box;
        ">
            <div style="
                background: white;
                padding: 25px;
                border-radius: 8px;
                border-left: 5px solid #4caf50;
                line-height: 1.8;
                font-size: 18px;
                box-sizing: border-box;
            ">
                <div style="font-size: 24px; margin-bottom: 15px;">??</div>
                <div style="font-weight: bold; color: #2e7d32; margin-bottom: 10px;">
                    问卷分析已完成！
                </div>
                <div style="color: #4caf50; font-size: 16px;">
                    请在 <strong>? 对话助手</strong> 页面查看您的个性化推荐结果
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 操作按钮区域
        st.markdown("---")
        
        # 主要操作按钮 - 突出显示
        col_main = st.columns([1, 3, 1])
        with col_main[1]:
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                if st.button("🎯 查看推荐结果", key=f"{key_prefix}continue_chat", type="primary"):
                    st.balloons()
                    st.success("🎯 请点击页面顶部的 '💬 对话助手' 标签页查看推荐结果")
            
            with button_col2:
                if st.button("📊 生成租房报告", key=f"{key_prefix}generate_report", type="secondary"):
                    st.balloons()
                    st.success("📊 请点击页面顶部的 '📊 租房报告' 标签页生成专业报告")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 其他操作按钮
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 重新填写问卷", key=f"{key_prefix}reset_questionnaire"):
                reset_questionnaire_data()
                st.rerun()
        
        with col2:
            if st.button("🔍 查看数据库结果", key=f"{key_prefix}detailed_analysis"):
                if result.get('function_results'):
                    st.info("✅ 数据库查询结果已在上方展示")
                else:
                    st.warning("⚠️ 暂无数据库查询结果")
        
        # 用户反馈区域
        st.markdown("---")
        st.markdown("### ? 反馈与建议")
        
        feedback_col1, feedback_col2 = st.columns([2, 1])
        
        with feedback_col1:
            user_feedback = st.text_area(
                "对推荐结果有什么想法？",
                placeholder="例如：希望看到更多某个区域的房源，或对价格范围有调整...",
                height=80,
                key=f"{key_prefix}user_feedback"
            )
        
        with feedback_col2:
            st.markdown("**推荐满意度**")
            satisfaction = st.radio(
                "您对推荐结果满意吗？",
                ["😊 很满意", "👍 还不错", "😐 一般", "😕 不太满意"],
                index=0,
                key=f"{key_prefix}satisfaction_radio"
            )
            
            if st.button("提交反馈", key=f"{key_prefix}submit_feedback"):
                st.success("感谢您的反馈！我们会持续改进推荐系统。")
        
        return result
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ 处理问卷时出错: {e}")
        st.error("请稍后重试，或切换到对话助手模式手动查询。")
        
        # 错误情况下的备用选项
        if st.button("🔄 重试", key=f"{key_prefix}retry_search"):
            st.rerun()
        
        return None 