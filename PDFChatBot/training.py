import os
import pickle
import time
from langchain_community.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI

os.environ['OPENAI_API_KEY'] = ""

def word_wrap(text, width=80):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9, max_tokens=500)

#file_path = "faiss_store_openai.pkl"
vectorstore_openai = None

loader = DirectoryLoader('pdfs', glob="**/*.*")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    separators=['\n\n', '\n', '.', ','],
    chunk_size=1000
)
split_docs = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
vectorstore_openai = FAISS.from_documents(split_docs, embeddings)
print(vectorstore_openai)
print("vector build")
name = "tempVectorStore"
# Save the FAISS index to a pickle file
#with open(file_path, "wb") as f:
embeddings = OpenAIEmbeddings()
vectorstore_openai.save_local(name)

x = FAISS.load_local(name, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
retriever = x.as_retriever()
