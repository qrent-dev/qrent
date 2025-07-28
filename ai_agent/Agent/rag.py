import os
import pandas as pd
from huggingface_hub import snapshot_download
from langchain.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# 嵌入模型配置（示例使用 Qwen-Embedding）
EMBEDDING_REPO = "qwen/Qwen3-Embedding-0.6B"
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

# 下载并初始化嵌入模型
print(f"Downloading embedding model {EMBEDDING_REPO}...")
model_path = snapshot_download(repo_id=EMBEDDING_REPO)
print(f"Embedding model downloaded to: {model_path}")
embed_model = HuggingFaceEmbeddings(
    model_name=model_path,
    model_kwargs={"device": EMBEDDING_DEVICE}
)


def load_documents(sources: list[str]) -> list[Document]:
    """
    加载指定路径下的文档，支持目录 (.txt/.md/.pdf/.csv/.xlsx) 和单文件。
    返回 Document 列表。
    """
    docs: list[Document] = []
    for src in sources:
        print(f"Processing source: {src}")
        
        # 检查文件是否存在
        if not os.path.exists(src):
            print(f"Warning: File/directory not found: {src}")
            continue
            
        if os.path.isdir(src):
            for root, _, files in os.walk(src):
                for fn in files:
                    path = os.path.join(root, fn)
                    ext = os.path.splitext(fn)[1].lower()
                    try:
                        if ext in ['.txt', '.md']:
                            loaded_docs = TextLoader(path).load()
                            docs.extend(loaded_docs)
                            print(f"Loaded {len(loaded_docs)} documents from {path}")
                        elif ext == '.pdf':
                            loaded_docs = PyPDFLoader(path).load()
                            docs.extend(loaded_docs)
                            print(f"Loaded {len(loaded_docs)} documents from {path}")
                        elif ext == '.csv':
                            loaded_docs = CSVLoader(path).load()
                            docs.extend(loaded_docs)
                            print(f"Loaded {len(loaded_docs)} documents from {path}")
                        elif ext in ['.xlsx', '.xls']:
                            df = pd.read_excel(path)
                            for _, row in df.iterrows():
                                docs.append(Document(
                                    page_content=str(row.to_dict()),
                                    metadata={'source': path}
                                ))
                            print(f"Loaded {len(df)} documents from {path}")
                    except Exception as e:
                        print(f"Error loading {path}: {e}")
                        continue
        elif os.path.isfile(src):
            ext = os.path.splitext(src)[1].lower()
            try:
                if ext in ['.txt', '.md']:
                    loaded_docs = TextLoader(src).load()
                    docs.extend(loaded_docs)
                    print(f"Loaded {len(loaded_docs)} documents from {src}")
                elif ext == '.pdf':
                    loaded_docs = PyPDFLoader(src).load()
                    docs.extend(loaded_docs)
                    print(f"Loaded {len(loaded_docs)} documents from {src}")
                elif ext == '.csv':
                    loaded_docs = CSVLoader(src).load()
                    docs.extend(loaded_docs)
                    print(f"Loaded {len(loaded_docs)} documents from {src}")
                elif ext in ['.xlsx', '.xls']:
                    df = pd.read_excel(src)
                    for _, row in df.iterrows():
                        docs.append(Document(
                            page_content=str(row.to_dict()),
                            metadata={'source': src}
                        ))
                    print(f"Loaded {len(df)} documents from {src}")
            except Exception as e:
                print(f"Error loading {src}: {e}")
                continue
                
    # 过滤掉空内容的文档
    filtered_docs = []
    for doc in docs:
        if doc.page_content and doc.page_content.strip():
            filtered_docs.append(doc)
        else:
            print(f"Skipping empty document from {doc.metadata.get('source', 'unknown')}")
    
    return filtered_docs


def build_vector_store(docs: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> FAISS:
    """
    将文档分块，生成嵌入并构建 FAISS 向量库存储。
    """
    if not docs:
        raise ValueError("No documents provided. Cannot build vector store with empty document list.")
    
    print(f"Building vector store with {len(docs)} documents...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    
    if not chunks:
        raise ValueError("No chunks created from documents. Documents may be empty or too short.")
    
    print(f"Created {len(chunks)} chunks from documents")
    
    # 验证chunks是否有内容
    valid_chunks = []
    for chunk in chunks:
        if chunk.page_content and chunk.page_content.strip():
            valid_chunks.append(chunk)
    
    if not valid_chunks:
        raise ValueError("No valid chunks with content found.")
    
    print(f"Using {len(valid_chunks)} valid chunks for vector store")
    
    faiss_index = FAISS.from_documents(valid_chunks, embed_model)
    return faiss_index


def main():
    # 配置：数据源路径列表和索引存储目录
    data_sources = ['../documents/Qrent攻略.pdf', '../documents/Qrent澳洲租房最全全流程攻略.pdf','../documents/Qrent-rag_plus.pdf']  
    index_path = '../database/faiss_index'

    print("Loading documents...")
    try:
        docs = load_documents(data_sources)
        print(f"Loaded {len(docs)} documents")
        
        if not docs:
            print("Error: No documents were loaded. Please check file paths and file contents.")
            return
        
        print("Building vector store...")
        vector_store = build_vector_store(docs)

        print(f"Saving vector store to '{index_path}'...")
        os.makedirs(index_path, exist_ok=True)
        vector_store.save_local(folder_path=index_path)
        print("Vector store saved successfully.")
        
    except Exception as e:
        print(f"Error in main process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
