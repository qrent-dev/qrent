# -*- coding: utf-8 -*-
import os
import json
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# 导入function模块
try:
    from function import AVAILABLE_FUNCTIONS
except ImportError:
    AVAILABLE_FUNCTIONS = {}

# Load environment variables
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

API_KEY = os.getenv("API_KEY_POINT")

# Configuration
INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "faiss_index")
EMBEDDING_REPO = "qwen/Qwen3-Embedding-0.6B"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-vl-max-latest"


class QrentAgent:
    def __init__(self):
        self.vector_store = None
        self.embed_model = None
        self.history = []
        self.questionnaire_data = None
        self.inquiry_agent_history = None
        self.inquiry_updated_requirements = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Agent"""
        try:
            # Initialize embedding model
            self.embed_model = HuggingFaceEmbeddings(
                model_name=EMBEDDING_REPO,
                model_kwargs={"device": "cpu"}
            )
            
            # Load vector store
            self.vector_store = self._load_vector_store()
            
            print("QrentAgent initialized successfully")
        except Exception as e:
            print(f"Error initializing QrentAgent: {e}")
            raise
    
    def _load_vector_store(self) -> FAISS:
        """Load vector store"""
        try:
            if not self.embed_model:
                raise ValueError("Embedding model not initialized")
                
            # Check if local index exists
            if not os.path.isdir(INDEX_DIR) or not os.listdir(INDEX_DIR):
                raise ValueError(f"Vector store not found at {INDEX_DIR}. Please build the vector store first.")
            
            # Load existing vector store
            return FAISS.load_local(
                folder_path=INDEX_DIR,
                embeddings=self.embed_model,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
            raise
    
    def update_context(self, questionnaire_data=None, inquiry_agent_history=None, inquiry_updated_requirements=None):
        """Update context information including questionnaire data, inquiry agent history, and updated requirements"""
        if questionnaire_data is not None:
            self.questionnaire_data = questionnaire_data
        if inquiry_agent_history is not None:
            self.inquiry_agent_history = inquiry_agent_history
        if inquiry_updated_requirements is not None:
            self.inquiry_updated_requirements = inquiry_updated_requirements
    
    def retrieve_vector_context(self, query: str, top_k: int = 5):
        """Retrieve relevant context from vector store"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)
        context = "\n---\n".join([d.page_content for d in docs])
        ids = [d.metadata.get("id") for d in docs if d.metadata.get("id")]
        return context, ids
    
    def call_qwen_via_dashscope(self, messages: list, use_functions: bool = True) -> dict:
        """Call Qwen model to generate response with optional function calling"""
        if not API_KEY:
            raise ValueError("API_KEY_POINT not set in environment variables")
        
        client = OpenAI(api_key=API_KEY, base_url=DASHSCOPE_BASE_URL)
        
        # 过滤和转换消息角色，确保API兼容性
        filtered_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # 将非标准角色映射为assistant
            if role == "inquiry_assistant":
                role = "assistant"
            
            # 只保留API支持的角色
            if role in ["system", "assistant", "user", "tool", "function"]:
                filtered_messages.append({"role": role, "content": content})
        
        try:
            # 准备函数定义
            functions = None
            if use_functions and AVAILABLE_FUNCTIONS:
                functions = []
                for func_name, func_config in AVAILABLE_FUNCTIONS.items():
                    functions.append({
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "description": func_config["description"],
                            "parameters": func_config["parameters"]
                        }
                    })
                print(f"Debug: Using {len(functions)} functions: {[f['function']['name'] for f in functions]}")
            else:
                print("Debug: No functions available or function calling disabled")
            
            # 调用API
            if functions:
                completion = client.chat.completions.create(
                    model=QWEN_MODEL,
                    messages=filtered_messages,
                    tools=functions,
                    tool_choice="auto"
                )
            else:
                completion = client.chat.completions.create(
                    model=QWEN_MODEL,
                    messages=filtered_messages
                )
            
            response_message = completion.choices[0].message
            
            # 处理函数调用
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                tool_calls = response_message.tool_calls
                function_results = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    
                    try:
                        # 添加JSON解析的错误处理
                        arguments_str = tool_call.function.arguments
                        print(f"Debug: Parsing function arguments: {arguments_str}")
                        
                        # 尝试清理可能的格式问题
                        arguments_str = arguments_str.strip()
                        
                        # 移除可能的markdown代码块标记
                        if arguments_str.startswith('```json'):
                            arguments_str = arguments_str.replace('```json', '').replace('```', '').strip()
                        elif arguments_str.startswith('```'):
                            arguments_str = arguments_str.replace('```', '').strip()
                        
                        # 查找第一个有效的JSON对象
                        # 如果有额外的数据，只取第一个完整的JSON对象
                        try:
                            # 首先尝试直接解析
                            function_args = json.loads(arguments_str)
                        except json.JSONDecodeError:
                            # 如果失败，尝试查找第一个完整的JSON对象
                            decoder = json.JSONDecoder()
                            try:
                                function_args, idx = decoder.raw_decode(arguments_str)
                                print(f"Debug: Found JSON object ending at position {idx}, total length: {len(arguments_str)}")
                                if idx < len(arguments_str.strip()):
                                    print(f"Debug: Extra data after JSON: '{arguments_str[idx:].strip()}'")
                            except json.JSONDecodeError:
                                # 最后的尝试：查找{}括起来的内容
                                import re
                                json_match = re.search(r'\{.*\}', arguments_str, re.DOTALL)
                                if json_match:
                                    json_part = json_match.group(0)
                                    function_args = json.loads(json_part)
                                    print(f"Debug: Extracted JSON from regex: {json_part}")
                                else:
                                    raise
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error for function {function_name}: {e}")
                        print(f"Raw arguments: {tool_call.function.arguments}")
                        print(f"Error position: line {e.lineno}, column {e.colno}")
                        function_results.append({
                            "name": function_name,
                            "error": f"参数解析错误: {e}"
                        })
                        continue
                    except Exception as e:
                        print(f"Unexpected error parsing function arguments: {e}")
                        function_results.append({
                            "name": function_name,
                            "error": f"参数解析错误: {e}"
                        })
                        continue
                    
                    if function_name in AVAILABLE_FUNCTIONS:
                        func = AVAILABLE_FUNCTIONS[function_name]["function"]
                        try:
                            result = func(**function_args)
                            function_results.append({
                                "name": function_name,
                                "result": result
                            })
                        except Exception as e:
                            function_results.append({
                                "name": function_name,
                                "error": f"函数调用错误: {e}"
                            })
                    else:
                        function_results.append({
                            "name": function_name,
                            "error": f"未知函数: {function_name}"
                        })
                
                return {
                    "type": "function_call",
                    "function_results": function_results,
                    "original_message": response_message.content or ""
                }
            else:
                # 普通文本回复
                return {
                    "type": "text",
                    "content": response_message.content or ""
                }
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error in Qwen API response: {e}")
            print(f"Error position: line {e.lineno}, column {e.colno}")
            print(f"Error character: {e.pos}")
            # 返回一个安全的错误响应而不是抛出异常
            return {
                "type": "text",
                "content": "抱歉，处理您的请求时遇到了格式错误。请稍后重试或简化您的问题。"
            }
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            print(f"Error type: {type(e)}")
            # 返回一个安全的错误响应
            return {
                "type": "text", 
                "content": f"抱歉，处理您的请求时遇到了错误：{str(e)}"
            }
    
    def generate_prompt(self, query: str, vector_context: str) -> str:
        """Generate prompt for AI model"""
        # 检测用户查询语言并设置相应的提示词
        def contains_chinese(text):
            """检测文本是否包含中文字符"""
            for char in text:
                if '\u4e00' <= char <= '\u9fff':
                    return True
            return False
        
        is_chinese = contains_chinese(query)
        
        # 格式化问卷数据和更新后的需求数据
        questionnaire_context = ""
        if self.questionnaire_data:
            questionnaire_context = "# 用户原始问卷信息\n\n" if is_chinese else "# User Original Questionnaire Information\n\n"
            for key, value in self.questionnaire_data.items():
                if value:
                    questionnaire_context += f"- {key}: {value}\n"
            questionnaire_context += "\n"
        
        # 添加更新后的需求数据
        updated_requirements_context = ""
        if self.inquiry_updated_requirements:
            updated_requirements_context = "# 智能分析师更新后的需求信息\n\n" if is_chinese else "# Updated Requirements from Intelligent Analyst\n\n"
            updated_requirements_context += "经过专业需求分析师分析和追问后，用户的最新需求如下：\n\n" if is_chinese else "After professional requirement analysis and follow-up questions, the user's latest requirements are:\n\n"
            
            for key, value in self.inquiry_updated_requirements.items():
                if value is not None:
                    updated_requirements_context += f"- {key}: {value}\n"
            updated_requirements_context += "\n**注意：这些是经过专业评估和用户确认的最新需求信息，请优先使用这些数据进行房源推荐。**\n\n" if is_chinese else "\n**Note: These are the latest requirement information after professional assessment and user confirmation. Please prioritize these data for property recommendations.**\n\n"
        
        # 格式化inquiry_agent历史
        inquiry_context = ""
        if self.inquiry_agent_history:
            inquiry_context = "# 需求分析师评估历史\n\n" if is_chinese else "# Requirement Analyst Assessment History\n\n"
            for i, (role, content) in enumerate(self.inquiry_agent_history[-4:]):  # 只取最近2轮对话
                role_name = "用户" if role == "user" else "需求分析师" if is_chinese else ("User" if role == "user" else "Requirement Analyst")
                inquiry_context += f"**{role_name}:** {content[:300]}{'...' if len(content) > 300 else ''}\n\n"
        
        if is_chinese:
            # 中文提示词
            prompt = f"""
你是一名专业的租房中介助手，根据公司知识库信息为用户提供租房建议。请仔细阅读知识库内容、用户问卷信息、需求分析师的评估结果、对话历史和用户当前问题，然后提供专业的租房建议。

# 知识库上下文

{vector_context}

{questionnaire_context}

{updated_requirements_context}

{inquiry_context}

# 对话历史

{self.history}

# 用户当前问题

{query}

# 要求
- 请用中文回答
- 结合用户问卷信息和需求分析师的评估结果提供建议
- 根据知识库信息提供具体的租房建议
- 包含具体的地区、价格、房型等信息
- 如果信息不足，请询问用户更多细节
- 保持专业、友好的语调
- 充分考虑用户的预算、房型偏好和特殊需求
"""
        else:
            # 英文提示词
            prompt = f"""
You are a professional rental assistant. Based on the knowledge base information, provide rental suggestions for users.

# Knowledge Base Context

{vector_context}

{questionnaire_context}

{updated_requirements_context}

{inquiry_context}

# Conversation History

{self.history}

# Current User Query

{query}

# Requirements
- Please respond in user's language
- Provide recommendations based on user questionnaire and requirement analyst assessment
- Provide specific rental recommendations based on the knowledge base
- Include specific areas, prices, property types, etc.
- If information is insufficient, ask for more details from the user
- Maintain a professional and friendly tone
- Consider user's budget, room type preferences, and special requirements
"""
        
        return prompt
    
    def process_query(self, query: str, top_k: int = 5, use_functions: bool = True) -> dict:
        """Process user query and return result"""
        try:
            # Vector retrieval
            vector_context, ids = self.retrieve_vector_context(query, top_k)
            
            # Build message list
            messages = [
                {"role": "system", "content": "You are a helpful rental assistant with access to real estate database functions."}
            ]
            
            # Add history (filter and convert roles for API compatibility)
            for role, content in self.history:
                # 将非标准角色映射为assistant
                if role == "inquiry_assistant":
                    role = "assistant"
                
                # 只保留API支持的角色
                if role in ["system", "assistant", "user", "tool", "function"]:
                    messages.append({"role": role, "content": content})
            
            # Generate prompt
            prompt = self.generate_prompt(query, vector_context)
            messages.append({"role": "user", "content": prompt})
            
            # Call AI model
            response = self.call_qwen_via_dashscope(messages, use_functions)
            
            # 处理不同类型的响应
            final_answer = ""
            function_results = []
            
            if response["type"] == "function_call":
                # 处理函数调用结果
                function_results = response["function_results"]
                
                # 构建包含函数结果的新消息
                function_summary = "基于数据库查询结果：\n\n"
                for func_result in function_results:
                    if "error" in func_result:
                        function_summary += f"❌ {func_result['name']}: {func_result['error']}\n"
                    else:
                        result = func_result["result"]
                        if result.get("success"):
                            function_summary += f"✅ {func_result['name']} 查询成功\n"
                            if "analysis_results" in result:
                                # 格式化区域分析结果
                                for area, analysis in result["analysis_results"].items():
                                    function_summary += f"\n📍 {area.upper()}区域:\n"
                                    function_summary += f"  总房源: {analysis['total_properties']}套\n"
                                    for room_type, stats in analysis['room_types'].items():
                                        function_summary += f"  {room_type}: {stats['count']}套, 平均租金{stats['avg_price']}AUD/周\n"
                            elif "properties" in result:
                                # 格式化房源搜索结果  
                                function_summary += f"找到 {result['count']} 套房源:\n"
                                for prop in result["properties"][:5]:  # 只显示前5个
                                    function_summary += f"  - {prop['addressLine1']} {prop['addressLine2']}, {prop['bedroomCount']}室{prop['bathroomCount']}卫, {prop['pricePerWeek']}AUD/周\n"
                        else:
                            function_summary += f"❌ {func_result['name']}: {result.get('error', '查询失败')}\n"
                
                # 重新调用AI生成基于函数结果的回答
                final_messages = messages + [
                    {"role": "assistant", "content": function_summary},
                    {"role": "user", "content": "请根据上述数据库查询结果，为用户提供专业的租房建议和推荐。"}
                ]
                
                final_response = self.call_qwen_via_dashscope(final_messages, use_functions=False)
                final_answer = final_response["content"]
                
            else:
                # 普通文本回复
                final_answer = response["content"]
            
            # Update history
            self.history.append(("user", query))
            self.history.append(("assistant", final_answer))
            
            return {
                "query": query,
                "vector_context": vector_context,
                "answer": final_answer,
                "function_results": function_results,
                "history": self.history
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print(f"Error type: {type(e)}")
            
            # 返回一个安全的错误响应，而不是抛出异常
            error_message = "抱歉，处理您的查询时遇到了问题。请尝试简化您的问题或稍后重试。"
            
            # 仍然更新历史记录以保持对话连续性
            self.history.append(("user", query))
            self.history.append(("assistant", error_message))
            
            return {
                "query": query,
                "vector_context": "",
                "answer": error_message,
                "function_results": [],
                "history": self.history,
                "error": str(e)
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
    
    def get_history(self):
        """Get conversation history"""
        return self.history


# Global instance
agent = None

def get_agent():
    """Get QrentAgent instance"""
    global agent
    if agent is None:
        agent = QrentAgent()
    return agent


if __name__ == "__main__":
    # Test code
    try:
        agent = QrentAgent()
        result = agent.process_query("I want to find a two-bedroom apartment in Sydney, budget 500 AUD per week")
        print("Query processed successfully!")
        print(f"Answer: {result['answer']}")
    except Exception as e:
        print(f"Error: {e}") 