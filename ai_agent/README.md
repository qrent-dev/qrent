# Qrent AI Agent

����֪ʶ��������ⷿ�Ƽ�ϵͳ�������ԭʼ�� `agent/Agent.py` �ļ���

## ��Ŀ�ṹ

```
ai_agent/
������ Agent/
��   ������ agent.py          # ����Agent�߼���
��   ������ rag.py           # RAG�����洢����
������ ui/
��   ������ streamlit.py     # Streamlit�û�����
������ database/
��   ������ faiss_index/     # FAISS�����洢
������ documents/
��   ������ Qrent����.pdf
��   ������ Qrent�����ⷿ��ȫȫ���̹���.pdf
������ run_streamlit.py     # Streamlit�����ű�
������ test_agent.py        # Agent���ܲ��Խű�
������ README.md           # ���ļ�
```

## ��������

### ���Ĺ���

- **�����ʴ�**: ����֪ʶ��ش��ⷿ�������
- **��������**: ʹ�� FAISS ������������
- **���ݿ⼯��**: �� PostgreSQL ���ݿ��ȡ��Դ��Ϣ
- **���ֶԻ�**: ֧�������ĸ�֪�ĶԻ���ʷ
- **���ȼ�����**: ���ܷ����û��ⷿ���ȼ�

### ����ջ

- **AI ģ��**: Qwen (ͨ�� DashScope API)
- **�����洢**: FAISS
- **Ƕ��ģ��**: Qwen3-Embedding-0.6B
- **���ݿ�**: PostgreSQL
- **UI ���**: Streamlit
- **�ĵ�����**: LangChain

## ��װ������

### 1. ����Ҫ��

```bash
Python 3.8+
pip install -r requirements.txt
```

### 2. ������������

���� `.env` �ļ����������±�����

```env
# ���ݿ�����
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name

# API����
API_KEY_POINT=your_dashscope_api_key
```

### 3. �����洢����

�״�ʹ��ǰ��Ҫ���������洢��

```bash
cd Agent
python rag.py
```

�⽫��

- ���� PDF �ĵ�
- �����ĵ�Ƕ��
- ���� FAISS ������ `database/faiss_index/`

## ʹ�÷���

### 1. ���� Agent ����

```bash
python test_agent.py
```

### 2. ���� Streamlit Ӧ��

```bash
python run_streamlit.py
```

����ֱ�����У�

```bash
streamlit run ui/streamlit.py
```

### 3. ��̽ӿ�ʹ��

```python
from Agent.agent import QrentAgent

# ����Agentʵ��
agent = QrentAgent()

# �����ѯ
result = agent.process_query("������һ������һ���ķ��ӣ�Ԥ��500��Ԫÿ��")

# ��ȡ���
print(result['answer'])
print(result['db_data'])
print(result['vector_context'])
```

## API �ӿ�

### QrentAgent ��

#### ��Ҫ����

- `process_query(query: str, top_k: int = 5) -> dict`

  - �����û���ѯ
  - ���ذ����𰸡����������ĺ����ݿ����ݵ��ֵ�

- `clear_history()`

  - ��նԻ���ʷ

- `get_history() -> list`
  - ��ȡ�Ի���ʷ

#### ���ظ�ʽ

```python
{
    "query": "�û���ѯ",
    "vector_context": "�����������������",
    "db_data": [...],  # ��ط�Դ����
    "answer": "AI���ɵĻش�",
    "history": [...]   # �Ի���ʷ
}
```

## �ļ�˵��

### Agent/agent.py

���� Agent �࣬������

- ���ݿ����ӹ���
- �����洢����
- AI ģ�͵���
- ��ѯ�����߼�

### Agent/rag.py

RAG ϵͳ������������

- �ĵ����غʹ���
- �����洢����
- ������͵���

### ui/streamlit.py

Streamlit �û����棬������

- ����ʽ�������
- ������Ϣ��ʾ
- �Ի���ʷ����
- ��������

## �����ų�

### ��������

1. **Agent ��ʼ��ʧ��**

   - ������ݿ���������
   - ȷ�ϻ�������������ȷ
   - ��֤�����洢�ļ�����

2. **�����洢����ʧ��**

   - ���� `python Agent/rag.py` ���¹���
   - ��� PDF �ĵ��Ƿ����
   - ȷ��Ƕ��ģ�����سɹ�

3. **API ����ʧ��**
   - ��֤ `API_KEY_POINT` ������ȷ
   - �����������
   - ȷ�� API ������

### ����ģʽ

�ڴ�������ӵ�����Ϣ��

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## ����˵��

### ����ṹ

- **�����ע��**: UI ��ҵ���߼�����
- **ģ�黯���**: ÿ����������ɲ���
- **������**: ���Ƶ��쳣�������
- **������ʾ**: �ṩ����ע�����ά��

### ��չָ��

1. **����µ��ĵ�����**: �޸� `Agent/rag.py` �е��ĵ������߼�
2. **�Զ��� UI ���**: �� `ui/streamlit.py` ������µĽ���Ԫ��
3. **�����µ� AI ģ��**: �޸� `Agent/agent.py` �е�ģ�͵����߼�

## ���֤

����Ŀ��ѭ MIT ���֤��
