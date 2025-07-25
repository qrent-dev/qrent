import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# 导入问卷模块
from questionnaire import (
    init_questionnaire_state, 
    show_questionnaire,
    format_questionnaire_data,
    reset_questionnaire_data
)

# 导入报告模块
from report import show_report_interface

# 添加Agent目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.join(current_dir, '..', 'Agent')
agent_dir = os.path.abspath(agent_dir)

if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)

# 导入Agent模块
try:
    sys.path.append(agent_dir)
    import agent
    try:
        from inquiry_agent import create_inquiry_agent
    except ImportError:
        # 如果无法导入inquiry_agent，创建一个空的替代
        def create_inquiry_agent():
            return None
    
    try:
        from report_agent import create_report_agent
    except ImportError:
        # 如果无法导入report_agent，创建一个空的替代
        def create_report_agent():
            return None
    
    get_agent = agent.get_agent
except ImportError as e:
    st.error(f"无法导入Agent模块: {e}")
    st.error(f"Agent目录路径: {agent_dir}")
    st.error(f"目录是否存在: {os.path.exists(agent_dir)}")
    if os.path.exists(agent_dir):
        st.error(f"目录内容: {os.listdir(agent_dir)}")
    st.stop()

# 页面配置
st.set_page_config(
    page_title="Qrent 租房助手", 
    layout="wide",
    page_icon="🏠"
)

# 强制重新创建agent对象以确保使用最新版本
try:
    st.session_state.agent = get_agent()
except Exception as e:
    st.error(f"初始化Agent失败: {e}")
    st.stop()

if 'inquiry_agent' not in st.session_state:
    try:
        st.session_state.inquiry_agent = create_inquiry_agent()
        if st.session_state.inquiry_agent is None:
            st.warning("智能追问Agent暂不可用，将使用基础模式")
    except Exception as e:
        st.warning(f"初始化信息追问Agent失败: {e}")
        st.session_state.inquiry_agent = None

if 'report_agent' not in st.session_state:
    try:
        st.session_state.report_agent = create_report_agent()
        if st.session_state.report_agent is None:
            st.warning("报告生成Agent暂不可用")
    except Exception as e:
        st.warning(f"初始化报告生成Agent失败: {e}")
        st.session_state.report_agent = None

if 'history' not in st.session_state:
    st.session_state.history = []



# 初始化工作流程状态
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = 'questionnaire'  # questionnaire -> assessment -> consultation -> report

if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False

if 'consultation_complete' not in st.session_state:
    st.session_state.consultation_complete = False

# 初始化问卷相关的session state
init_questionnaire_state()


def show_workflow_interface():
    """显示智能工作流程界面"""
    st.title("🚀 智能租房流程")
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
    
    # 显示当前流程进度
    st.markdown("### 📋 流程进度")
    
    # 创建进度条
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    
    with progress_col1:
        if st.session_state.workflow_stage == 'questionnaire':
            st.info("📝 **当前步骤**\n问卷填写")
        elif st.session_state.workflow_stage in ['assessment', 'consultation', 'report']:
            st.success("✅ **已完成**\n问卷填写")
        else:
            st.warning("⏳ **待完成**\n问卷填写")
    
    with progress_col2:
        if st.session_state.workflow_stage == 'assessment':
            st.info("🔍 **当前步骤**\n需求评估")
        elif st.session_state.workflow_stage in ['consultation', 'report']:
            st.success("✅ **已完成**\n需求评估")
        else:
            st.warning("⏳ **待完成**\n需求评估")
    
    with progress_col3:
        if st.session_state.workflow_stage == 'consultation':
            st.info("💬 **当前步骤**\n房源咨询")
        elif st.session_state.workflow_stage == 'report':
            st.success("✅ **已完成**\n房源咨询")
        else:
            st.warning("⏳ **待完成**\n房源咨询")
    
    with progress_col4:
        if st.session_state.workflow_stage == 'report':
            st.info("📊 **当前步骤**\n报告生成")
        else:
            st.warning("⏳ **待完成**\n报告生成")
    
    st.markdown("---")
    
    # 根据当前阶段显示不同的界面
    if st.session_state.workflow_stage == 'questionnaire':
        show_questionnaire_stage()
    elif st.session_state.workflow_stage == 'assessment':
        show_assessment_stage()
    elif st.session_state.workflow_stage == 'consultation':
        show_consultation_stage()
    elif st.session_state.workflow_stage == 'report':
        show_report_stage()


def show_questionnaire_stage():
    """显示问卷填写阶段"""
    st.markdown("### 📝 第一步：完善您的租房需求")
    st.markdown("请先完整填写问卷，我们将基于您的信息进行专业评估。")
    
    # 调用问卷组件，使用workflow前缀避免key冲突
    show_questionnaire(key_prefix="workflow_")
    
    # 检查问卷是否完成
    if st.session_state.questionnaire_data:
        # 检查关键信息是否完整
        required_fields = ['budget_min', 'budget_max', 'room_type']
        filled_fields = [field for field in required_fields if st.session_state.questionnaire_data.get(field)]
        
        if len(filled_fields) >= 2:  # 至少填写了2个关键字段
            st.success("✅ 问卷信息已收集完成！")
            
            if st.button("🔍 开始需求评估", type="primary", key="workflow_start_assessment"):
                st.session_state.workflow_stage = 'assessment'
                # 重置评估状态
                if st.session_state.inquiry_agent:
                    st.session_state.inquiry_agent.reset_conversation()
                    st.session_state.inquiry_agent.update_context(
                        questionnaire_data=st.session_state.questionnaire_data
                    )
                st.rerun()
        else:
            st.warning("⚠️ 请至少填写预算范围和房型偏好后再进行下一步。")


def show_assessment_stage():
    """显示需求评估阶段"""
    st.markdown("### 🔍 第二步：专业需求评估")
    st.markdown("我们的专业评估师将分析您的需求合理性，并提供改进建议。")
    
    if not st.session_state.inquiry_agent:
        st.error("❌ 评估服务暂不可用，请刷新页面重试。")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("需求评估")
        
        # 显示问卷摘要
        with st.expander("📋 您的问卷信息", expanded=False):
            if st.session_state.questionnaire_data:
                for key, value in st.session_state.questionnaire_data.items():
                    if value:
                        st.text(f"{key}: {value}")
        
        # 首次评估或显示评估历史
        if not st.session_state.inquiry_agent.conversation_history:
            st.markdown("#### 🤖 初步评估")
            if st.button("开始评估", type="primary"):
                with st.spinner("正在评估您的需求..."):
                    try:
                        response = st.session_state.inquiry_agent.assess_questionnaire_requirements()
                        st.rerun()
                    except Exception as e:
                        st.error(f"评估失败: {e}")
        else:
            # 显示评估历史
            st.markdown("#### 📝 评估对话")
            for i, (role, content) in enumerate(st.session_state.inquiry_agent.conversation_history):
                if role == "user":
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>👤 您的回复:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                elif role == "assistant":
                    st.markdown(f"""
                    <div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>🔍 专业评估:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
            
            # 显示更新后的需求信息
            if st.session_state.inquiry_agent.conversation_history:
                st.markdown("#### 📊 更新后的需求信息")
                updated_requirements = st.session_state.inquiry_agent.get_updated_requirements()
                
                # 只显示有值的字段
                display_requirements = {k: v for k, v in updated_requirements.items() if v is not None}
                
                if display_requirements:
                    with st.expander("📋 当前收集到的需求信息", expanded=True):
                        for key, value in display_requirements.items():
                            st.text(f"• {key}: {value}")
                else:
                    st.info("💡 暂未收集到更新的需求信息")
            
            # 检查评估是否完成
            if st.session_state.inquiry_agent.is_assessment_complete():
                st.success("✅ 需求评估已完成！您的需求已通过专业评估。")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🏠 开始房源咨询", type="primary"):
                        st.session_state.workflow_stage = 'consultation'
                        st.session_state.assessment_complete = True
                        st.rerun()
                
                with col_btn2:
                    if st.button("🔄 重新评估"):
                        st.session_state.inquiry_agent.reset_conversation()
                        st.session_state.inquiry_agent.update_context(
                            questionnaire_data=st.session_state.questionnaire_data
                        )
                        st.rerun()
            else:
                # 继续对话
                st.markdown("#### 💬 继续对话")
                user_response = st.text_area(
                    "请回复评估师的问题或提供更多信息：",
                    height=100,
                    placeholder="请根据上方的评估意见进行回复..."
                )
                
                if st.button("提交回复", type="primary"):
                    if user_response.strip():
                        with st.spinner("正在分析您的回复..."):
                            try:
                                st.session_state.inquiry_agent.provide_follow_up_analysis(user_response)
                                st.rerun()
                            except Exception as e:
                                st.error(f"分析失败: {e}")
                    else:
                        st.warning("请输入您的回复内容。")
    
    with col2:
        st.header("评估指南")
        
        with st.expander("💡 评估标准", expanded=True):
            st.markdown("""
            **预算合理性:**
            - 房租占总生活费的45%-65%
            - 生活费至少1200澳元/月
            - 考虑Bills和家具成本
            
            **房型匹配度:**
            - 预算与房型的匹配
            - 合租意愿的合理性
            - 区域选择的可行性
            """)
        
        with st.expander("🎯 评估目标", expanded=True):
            st.markdown("""
            **我们将帮您确认:**
            - 预算设置是否合理
            - 房型选择是否现实
            - 是否有遗漏的关键信息
            - 期望是否需要调整
            """)
        
        # 显示评估进度
        if st.session_state.inquiry_agent.conversation_history:
            summary = st.session_state.inquiry_agent.get_conversation_summary()
            st.markdown(f"""
            **📊 评估进度:**
            - 对话轮数: {summary['total_exchanges']}
            - 状态: {'已完成' if summary['assessment_complete'] else '进行中'}
            """)


def show_consultation_stage():
    """显示房源咨询阶段"""
    st.markdown("### 💬 第三步：专业房源咨询")
    st.markdown("基于您已验证的需求，我们将为您推荐合适的房源和区域。")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("房源咨询")
        
        # 显示需求摘要
        with st.expander("✅ 已验证的需求", expanded=False):
            # 显示inquiry_agent收集和验证的最终需求
            if st.session_state.inquiry_agent:
                updated_requirements = st.session_state.inquiry_agent.get_updated_requirements()
                validation_status = st.session_state.inquiry_agent.get_validation_status()
                
                st.markdown("**✅ 经过专业评估验证的需求信息:**")
                
                # 显示完整性和预算验证状态
                if validation_status['is_valid']:
                    st.success(f"🎯 {validation_status['validation_message']}")
                else:
                    st.warning(f"⚠️ {validation_status['validation_message']}")
                
                st.markdown("---")
                
                # 显示具体的需求数据
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💰 预算信息:**")
                    if updated_requirements.get('budget_min') and updated_requirements.get('budget_max'):
                        st.text(f"• 租金预算: ${updated_requirements['budget_min']}-${updated_requirements['budget_max']}/周")
                    if updated_requirements.get('total_budget'):
                        st.text(f"• 总生活预算: ${updated_requirements['total_budget']}/周")
                    if updated_requirements.get('includes_bills'):
                        st.text(f"• Bills费用: {updated_requirements['includes_bills']}")
                    if updated_requirements.get('includes_furniture'):
                        st.text(f"• 家具费用: {updated_requirements['includes_furniture']}")
                
                with col2:
                    st.markdown("**🏠 房型和其他要求:**")
                    if updated_requirements.get('room_type'):
                        st.text(f"• 房型: {updated_requirements['room_type']}")
                    if updated_requirements.get('consider_sharing'):
                        st.text(f"• 合租意愿: {updated_requirements['consider_sharing']}")
                    if updated_requirements.get('commute_time'):
                        st.text(f"• 通勤时间: {updated_requirements['commute_time']}")
                    if updated_requirements.get('move_in_date'):
                        st.text(f"• 入住日期: {updated_requirements['move_in_date']}")
                    if updated_requirements.get('lease_duration'):
                        st.text(f"• 租期: {updated_requirements['lease_duration']}")
                
                # 显示JSON格式的完整数据
                with st.expander("🔧 查看完整需求数据 (JSON格式)", expanded=False):
                    st.json(updated_requirements)
                    
            elif st.session_state.questionnaire_data:
                st.markdown("**⚠️ 基本需求 (未经专业评估):**")
                for key, value in st.session_state.questionnaire_data.items():
                    if value:
                        st.text(f"• {key}: {value}")
                st.info("💡 建议先完成需求评估步骤以获得更准确的需求数据")
            else:
                st.warning("📝 请先完成问卷填写和需求评估")
        
        # 房源咨询对话
        query = st.text_area(
            "请描述您的具体需求：",
            height=100,
            placeholder="例如：我想在UNSW附近找符合我预算的两室公寓，请推荐具体的区域和房源..."
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 获取房源推荐", type="primary"):
                if query.strip():
                    with st.spinner("正在搜索匹配的房源..."):
                        try:
                            # 更新Agent上下文信息
                            inquiry_updated_requirements = None
                            if st.session_state.inquiry_agent:
                                inquiry_updated_requirements = st.session_state.inquiry_agent.get_updated_requirements()
                            
                            st.session_state.agent.update_context(
                                questionnaire_data=st.session_state.questionnaire_data,
                                inquiry_agent_history=st.session_state.inquiry_agent.conversation_history if st.session_state.inquiry_agent else None,
                                inquiry_updated_requirements=inquiry_updated_requirements
                            )
                            
                            # 使用主Agent进行房源搜索
                            result = st.session_state.agent.process_query(query, top_k=5)
                            
                            # 显示搜索结果
                            st.markdown("### 🏠 房源推荐结果")
                            
                            # 显示函数调用结果
                            if result.get('function_results'):
                                st.markdown("#### 📊 数据库查询结果")
                                for func_result in result['function_results']:
                                    if 'error' in func_result:
                                        st.error(f"❌ {func_result['name']}: {func_result['error']}")
                                    else:
                                        st.success(f"✅ {func_result['name']}: 查询成功")
                            
                            # 显示AI推荐
                            if result['answer']:
                                st.markdown("#### 🤖 专业推荐")
                                st.markdown(f"""<div style="background: #fff3e0; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>🔍 专业评估:</strong><br>
                        {result['answer']}
                    </div>
                                """, unsafe_allow_html=True)
                            
                            # 满意度确认
                            st.markdown("---")
                            st.markdown("#### 💭 您对推荐结果满意吗？")
                            
                            satisfaction_col1, satisfaction_col2 = st.columns(2)
                            with satisfaction_col1:
                                if st.button("😊 满意，生成报告", type="primary"):
                                    st.session_state.workflow_stage = 'report'
                                    st.session_state.consultation_complete = True
                                    st.rerun()
                            
                            with satisfaction_col2:
                                if st.button("🔄 需要更多信息"):
                                    st.info("请继续提问，我们将提供更详细的信息。")
                            
                        except Exception as e:
                            st.error(f"搜索失败: {e}")
                else:
                    st.warning("请输入您的具体需求。")
        
        with col_btn2:
            if st.button("📊 直接生成报告"):
                st.session_state.workflow_stage = 'report'
                st.session_state.consultation_complete = True
                st.rerun()
        
        # 显示对话历史
        if st.session_state.history:
            st.markdown("### 📝 咨询历史")
            
            for i, (role, content) in enumerate(st.session_state.history[-4:]):  # 显示最近2轮对话
                if role == "user":
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>👤 您的咨询:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
                elif role == "assistant":
                    st.markdown(f"""
                    <div style="background: #f3e5f5; padding: 15px; border-radius: 10px; margin: 10px 0;">
                        <strong>🏠 房源顾问:</strong><br>
                        {content}
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.header("咨询指南")
        
        with st.expander("💡 推荐咨询内容", expanded=True):
            st.markdown("""
            **具体询问:**
            - 推荐符合预算的具体区域
            - 各区域的房源价格对比
            - 交通便利程度分析
            - 生活设施和安全性评估
            
            **深入了解:**
            - 租赁流程和注意事项
            - 看房和申请技巧
            - 合同条款解读
            """)
        
        with st.expander("🎯 优质服务", expanded=True):
            st.markdown("""
            **我们提供:**
            - 基于数据库的精准房源搜索
            - 专业的区域分析报告
            - 个性化的预算建议
            - 实时的市场信息
            """)


def show_report_stage():
    """显示报告生成阶段"""
    st.markdown("### 📊 第四步：生成专业报告")
    st.markdown("基于您的完整需求分析和咨询结果，我们将生成个性化的租房报告。")
    
    # 调用报告生成界面
    show_report_interface(key_prefix="workflow_")
    
    # 添加流程完成提示
    st.markdown("---")
    st.success("🎉 恭喜！您已完成完整的智能租房流程。")
    
    if st.button("🔄 重新开始流程"):
        # 重置所有状态
        st.session_state.workflow_stage = 'questionnaire'
        st.session_state.assessment_complete = False
        st.session_state.consultation_complete = False
        
        # 重置各个Agent
        if st.session_state.inquiry_agent:
            st.session_state.inquiry_agent.reset_conversation()
        if st.session_state.agent:
            st.session_state.agent.clear_history()
        if st.session_state.report_agent:
            st.session_state.report_agent.reset_data()
        
        # 清空历史
        st.session_state.history = []
        
        st.rerun()


def show_chat_interface():
    """显示对话界面"""
    st.title("💬 Qrent 智能对话助手")
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

    # 侧边栏设置
    with st.sidebar:
        st.header("设置")
        
        # 检索参数设置
        top_k = st.slider(
            "检索文档条数 (k)", 
            min_value=1, 
            max_value=10, 
            value=5,
            help="设置从知识库中检索的相关文档数量"
        )
        
        st.markdown("---")
        
        # 历史记录管理
        st.header("对话管理")
        
        if st.button("清空对话历史", type="secondary"):
            st.session_state.agent.clear_history()
            st.session_state.history = []
            st.success("对话历史已清空！")
            st.rerun()
        
        # 生成报告按钮
        if st.button("📊 生成租房报告", type="primary"):
            st.success("🎉 请点击页面顶部的 '📊 租房报告' 标签页生成专业报告")
        
        # 显示当前对话轮数
        if st.session_state.history:
            st.info(f"当前对话轮数: {len(st.session_state.history)//2}")
        
        st.markdown("---")
        
        # 帮助信息
        st.header("💡 使用提示")
        st.markdown("""
        **如何使用：**
        1. 在下方输入框中描述您的租房需求
        2. 点击"提交查询"按钮
        3. 系统会基于知识库为您推荐合适的房源
        
        **示例问题：**
        - 我想在悉尼找一个两室一厅的房子，预算500澳元每周
        - 推荐一些靠近UNSW的公寓，预算800澳元
        - 分析kensington区域的房源价格统计情况
        - 帮我找预算600-900澳元的两室房源
        - 对比randwick和kingsford两个区域的租房市场
        """)

    # 主要内容区域
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("对话区域")
        
        # 查询输入
        query = st.text_area(
            "请输入您的租房需求：",
            height=100,
            placeholder="例如：我想在悉尼找一个两室一厅的房子，预算500澳元每周，靠近UNSW..."
        )
        
        # 提交按钮
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            submit_button = st.button("提交查询", type="primary")
        
        with col_btn2:
            if st.button("重新生成"):
                if st.session_state.history:
                    # 获取最后一个用户问题
                    last_query = None
                    for i in range(len(st.session_state.history) - 1, -1, -1):
                        if st.session_state.history[i][0] == "user":
                            last_query = st.session_state.history[i][1]
                            break
                    
                    if last_query:
                        # 移除最后一轮对话
                        if len(st.session_state.history) >= 2:
                            st.session_state.history = st.session_state.history[:-2]
                            st.session_state.agent.history = st.session_state.agent.history[:-2]
                        
                        # 重新处理查询
                        query = last_query
                        submit_button = True

        # 处理查询
        if submit_button and query.strip():
            with st.spinner("正在分析您的需求，请稍候..."):
                try:
                    # 获取inquiry_agent的最后一轮输出作为上下文
                    inquiry_context = None
                    if st.session_state.inquiry_agent and st.session_state.inquiry_agent.conversation_history:
                        inquiry_context = st.session_state.inquiry_agent.conversation_history
                    
                    # 获取更新后的需求数据
                    inquiry_updated_requirements = None
                    if st.session_state.inquiry_agent:
                        inquiry_updated_requirements = st.session_state.inquiry_agent.get_updated_requirements()
                    
                    # 更新Agent上下文信息
                    st.session_state.agent.update_context(
                        questionnaire_data=st.session_state.questionnaire_data,
                        inquiry_agent_history=inquiry_context,
                        inquiry_updated_requirements=inquiry_updated_requirements
                    )
                    
                    result = st.session_state.agent.process_query(query, top_k)
                    
                    # 更新session state中的历史
                    st.session_state.history = result['history']
                    
                    # 显示结果
                    st.success("查询处理完成！")
                    
                    # 显示函数调用结果（如果有）
                    if result.get('function_results'):
                        st.markdown("### 📊 数据库查询结果：")
                        for func_result in result['function_results']:
                            if 'error' in func_result:
                                st.error(f"❌ {func_result['name']}: {func_result['error']}")
                            else:
                                st.success(f"✅ {func_result['name']}: 查询成功")
                                if 'result' in func_result:
                                    func_res = func_result['result']
                                    if 'analysis_results' in func_res:
                                        st.info(f"📈 分析了 {len(func_res['analysis_results'])} 个区域")
                                    elif 'properties' in func_res:
                                        st.info(f"🏠 找到 {func_res.get('count', 0)} 套房源")
                    
                    # 显示AI回答
                    if result['answer']:
                        st.markdown("### 🤖 AI助手回答：")
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                            padding: 25px;
                            border-radius: 12px;
                            margin: 15px 0;
                            border: 2px solid #e3f2fd;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            width: 100%;
                            max-width: none;
                        ">
                            <div style="
                                background: white;
                                padding: 25px;
                                border-radius: 8px;
                                border-left: 5px solid #ff6b6b;
                                line-height: 1.7;
                                font-size: 16px;
                                width: 100%;
                                box-sizing: border-box;
                                word-wrap: break-word;
                                overflow-wrap: break-word;
                            ">
                                {result['answer']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error("🚨 处理查询时遇到问题")
                    with st.expander("查看错误详情", expanded=False):
                        st.code(f"错误类型: {type(e).__name__}")
                        st.code(f"错误信息: {str(e)}")
                    
                    st.markdown("### 💡 建议解决方案：")
                    st.info("""
                    1. 请尝试简化您的问题
                    2. 检查预算和房型信息是否准确
                    3. 稍后再次尝试
                    4. 如果问题持续，请联系技术支持
                    """)

    with col2:
        st.header("检索信息")
        
        # 显示最近查询的统计信息
        if st.session_state.history:
            st.info(f"💬 总对话轮数: {len(st.session_state.history)//2}")
            
            # 显示最近的查询
            if len(st.session_state.history) >= 2:
                latest_query = st.session_state.history[-2][1]
                with st.expander("📝 最近查询", expanded=True):
                    st.text(latest_query[:100] + "..." if len(latest_query) > 100 else latest_query)
            
            # 显示上下文信息
            context_items = []
            if st.session_state.questionnaire_data:
                context_items.append("✅ 问卷信息已加载")
            if st.session_state.inquiry_agent and st.session_state.inquiry_agent.conversation_history:
                context_items.append("✅ 需求评估结果已加载")
            
            if context_items:
                with st.expander("🔗 当前上下文", expanded=True):
                    for item in context_items:
                        st.success(item)
                    
                    # 显示详细的问卷信息
                    if st.session_state.questionnaire_data:
                        st.markdown("**问卷详情：**")
                        for key, value in st.session_state.questionnaire_data.items():
                            if value:
                                st.text(f"• {key}: {value}")
                    
                    # 显示inquiry_agent的最后评估结果
                    if st.session_state.inquiry_agent and st.session_state.inquiry_agent.conversation_history:
                        st.markdown("**最新评估结果：**")
                        # 获取最后一轮assistant的回复
                        last_assessment = None
                        for role, content in reversed(st.session_state.inquiry_agent.conversation_history):
                            if role == "assistant":
                                last_assessment = content
                                break
                        
                        if last_assessment:
                            # 显示摘要（前200字符）
                            assessment_summary = last_assessment[:200] + "..." if len(last_assessment) > 200 else last_assessment
                            st.info(f"💡 {assessment_summary}")
                            
                            # 显示评估状态
                            if st.session_state.inquiry_agent.is_assessment_complete():
                                st.success("🎯 需求评估已完成，可以进行房源搜索")
                            else:
                                st.warning("⚠️ 需求评估未完成，建议先完成评估")
                    
                    # 显示更新后的需求信息
                    if st.session_state.inquiry_agent:
                        updated_requirements = st.session_state.inquiry_agent.get_updated_requirements()
                        display_requirements = {k: v for k, v in updated_requirements.items() if v is not None}
                        
                        if display_requirements:
                            st.markdown("**📊 收集到的需求信息：**")
                            with st.expander("查看详细需求", expanded=False):
                                for key, value in display_requirements.items():
                                    st.text(f"• {key}: {value}")
            else:
                st.info("💡 建议先填写问卷或完成需求评估，以获得更精准的推荐")
            
            # 显示帮助信息
            with st.expander("💡 使用提示", expanded=False):
                st.markdown("""
                **查询技巧：**
                - 包含具体地区（如悉尼、墨尔本）
                - 明确预算范围
                - 说明房型需求（几室几厅）
                - 提及特殊要求（靠近学校、交通等）
                
                **示例：**
                > 我是UNSW学生，想找500-600澳元的两室公寓，最好在Kensington或Randwick
                """)
        else:
            st.info("还没有查询记录，开始您的第一次租房咨询吧！")

    # 对话历史显示
    if st.session_state.history:
        st.markdown("---")
        st.header("对话历史")
        
        # 创建对话容器
        chat_container = st.container()
        
        with chat_container:
            for i, (role, content) in enumerate(st.session_state.history):
                if role == "user":
                    # 用户消息
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        padding: 20px;
                        border-radius: 12px;
                        margin: 15px 0;
                        border-left: 5px solid #2196f3;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: none;
                        box-sizing: border-box;
                    ">
                        <div style="
                            font-weight: bold;
                            color: #1976d2;
                            margin-bottom: 10px;
                            font-size: 16px;
                        ">👤 用户:</div>
                        <div style="
                            line-height: 1.6;
                            font-size: 15px;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                        ">
                            {content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # 助手消息
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                        padding: 20px;
                        border-radius: 12px;
                        margin: 15px 0;
                        border-left: 5px solid #9c27b0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: none;
                        box-sizing: border-box;
                    ">
                        <div style="
                            font-weight: bold;
                            color: #7b1fa2;
                            margin-bottom: 10px;
                            font-size: 16px;
                        ">🤖 Qrent助手:</div>
                        <div style="
                            line-height: 1.6;
                            font-size: 15px;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                        ">
                            {content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# 主程序
def main():
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 智能流程", "📋 需求问卷", "💬 对话助手", "📊 租房报告"])
    
    with tab1:
        show_workflow_interface()
    
    with tab2:
        show_questionnaire()
    
    with tab3:
        show_chat_interface()
    
    with tab4:
        show_report_interface(key_prefix="tab_")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.8em;">
        Powered by Qrent AI Agent | 基于知识库的智能租房推荐系统
    </div>
    """, 
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()
