import pickle

from dotenv import load_dotenv
import os

from langchain.chains.qa_with_sources import load_qa_with_sources_chain

load_dotenv()
import streamlit as st
import PyPDF2
from pathlib import Path
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
from langchain.llms import OpenAI

st.title('Chatbot from your textbook ✨')
st.subheader("Follow [@jamescodez](https://twitter.com/jamescodez) on twitter for updates")

OPENAI_KEY = os.getenv('OPENAI_KEY')
pageDocs = []

def remove_extra(line):
    line = line.replace('\n', ' ')
    line = line.replace('  ', ' ')
    line = line.replace('\\n', ' ')
    return line

def pdfToTxt():
    pages_text = []
    print("Starting pdf to text transcription")
    with open("file.pdf", 'rb') as pdfFileObject:
        pdfReader = PyPDF2.PdfReader(pdfFileObject)
        print(" No. Of Pages :", len(pdfReader.pages))
        for i, page in enumerate(pdfReader.pages):
            pageObject = pdfReader.pages[i]
            pages_text.append((pageObject.extract_text(), i + 2))
            if i == 544: #pages past 544 trash
                break
    # create documents for each page
    for pageText, pageNum in pages_text:
        pageClean = remove_extra(pageText)
        print("ONE PAGE: ", pageClean)
        doc = Document(page_content=pageClean, metadata={"source": f"Page Number: {pageNum}"})
        pageDocs.append(doc)
    print("done with pdf to txt!")

# upload image to streamlit
uploaded_file = st.file_uploader("Choose a pdf file")

if uploaded_file is not None:
    # To read file as bytes:
    pdfBytes = uploaded_file.getvalue()
    with open('file.pdf', 'wb') as handler:
        handler.write(pdfBytes)
    with st.spinner(text='In progress'):
        pdfToTxt()
        st.success("pdf uploaded!")

    # Split Text to get most relevant data for LLM
    text_splitter = CharacterTextSplitter(separator=" ", chunk_size=1024, chunk_overlap=0)
    out_chunks = []
    for page in pageDocs:
        for smaller_chunk in text_splitter.split_text(page.page_content):
            out_chunks.append(Document(page_content=smaller_chunk, metadata=page.metadata))

    vectorStorePkl = Path("vectorstore.pkl")
    vectorStore = None
    if vectorStorePkl.is_file():
        print("vector index found.. ")
        with open('vectorstore.pkl', 'rb') as f:
            vectorStore = pickle.load(f)
    else:
        print("regenerating search index vector store..")
        # It uses OpenAI API to create embeddings (i.e. a feature vector)
        # https://developers.google.com/machine-learning/crash-course/embeddings/video-lecture
        vectorStore = FAISS.from_documents(out_chunks, OpenAIEmbeddings(openai_api_key=OPENAI_KEY))
        with open("vectorstore.pkl", "wb") as f:
            pickle.dump(vectorStore, f)

    #create load_qa_with_sources_chain
    chain = load_qa_with_sources_chain(OpenAI(temperature=0, openai_api_key=OPENAI_KEY))
    #get user
    userInput = st.text_input(label="Talk with book", placeholder="Enter query")

    #get result
    result = chain(
        {
            "input_documents": vectorStore.similarity_search(userInput, k=4),
            "question": userInput,
        },
        return_only_outputs=True,
    )["output_text"]

    st.subheader(result)