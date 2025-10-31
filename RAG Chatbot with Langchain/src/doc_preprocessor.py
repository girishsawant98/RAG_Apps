import logging
from langchain_text_splitters import Language
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.parsers.pdf import (
    extract_from_images_with_rapidocr
)
from langchain_core.documents import Document

def process_pdf(source):

    logging.info(f"Loading PDF file from {source}")
    
    # Load the PDF with image text extraction
    loader = PyPDFLoader(source)
    documents = loader.load()

    #Filtering out empty documents
    unscanned_documents = [doc for doc in documents if doc.page_content.strip() != ""]
    
    scanned_pages = len(documents) - len(unscanned_documents)
    if scanned_pages > 0:
        logging.info(f"Omitted {scanned_pages} scanned page(s) from the pdf.")
    
    if not unscanned_documents:
        raise ValueError( 
        "All pages in the PDF appear to be scanned.Please use a PDF with text content"
        )
    
    return split_documents(unscanned_documents)

def process_image(source):
    #Extract text from image using RapidOCR
    logging.info(f"Extracting text from image {source}")
    with open(source, "rb") as img_file:
        image_bytes = img_file.read()

    extracted_text = extract_from_images_with_rapidocr([image_bytes])
    documents = [Document(page_content=extracted_text, metadata={"source": source})]
    return split_documents(documents)


def split_documents(documents):
    logging.info("Splitting documents into smaller chunks")

    LANGUAGE = Language.PYTHON
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        chunk_size=1000,
        chunk_overlap=200,
        language=LANGUAGE
    )

    split_docs = text_splitter.split_documents(documents)
    logging.info(f"Split into {len(split_docs)} chunks")
    return split_docs

def process_document(source):
    if source.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return process_image(source)
    elif source.lower().endswith('.pdf'):
        return process_pdf(source)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or image file. {source}")

    


    

