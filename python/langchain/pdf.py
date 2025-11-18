#pip install langchain-community pypdf
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

file_path = "Nginx开发从入门到精通.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print(len(docs))

print(f"{docs[9].page_content[:200]}\n")
print(docs[9].metadata)
print(docs[9].id)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
print(len(all_splits))
print(all_splits[0].page_content)

embeddings = OllamaEmbeddings(model="deepseek-r1:14b")
vector_1 = embeddings.embed_query(all_splits[0].page_content)
vector_2 = embeddings.embed_query(all_splits[1].page_content)

assert len(vector_1) == len(vector_2)
print(f"Generated vectors of length {len(vector_1)}\n")
print(vector_1[:10])

vector_store = InMemoryVectorStore(embeddings)
ids = vector_store.add_documents(documents=all_splits)
results = vector_store.similarity_search(
    "nginx为什么要采用多进程的方式?"
)

print(results[0])

