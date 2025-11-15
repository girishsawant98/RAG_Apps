import validators, streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from pytube import YouTube
load_dotenv()

# -------------------------
# Extract YouTube Video ID
# -------------------------
def extract_video_id(url: str):
    parsed = urlparse(url)
    video_id = None

    # Standard YouTube link
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    # Short link: youtu.be/asd123
    elif parsed.hostname == "youtu.be":
        video_id = parsed.path.lstrip("/")

    # Embed link: youtube.com/embed/asd123
    elif parsed.path.startswith("/embed/"):
        video_id = parsed.path.split("/")[2]

    return video_id


#----- Streamlit APP ------
st.set_page_config(page_title="Langchain: Summarize Text From YT or Website", page_icon= "🦜")
st.title("🦜Langchain: Summarize Text")
st.subheader("Summarize URL")

### Get the Groq API KEY and URL(YT or Website)
with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", value="", type="password")
    
url = st.text_input("URL", label_visibility="collapsed")

## Get the Gemma model from Groq 
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_api_key)

## Prompt
prompt_template = """
    Provide a summary of the following content in 300 words:
    Content:{text}

"""

prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

if st.button("Summarize"):
    #Validate all the inputs
    if not groq_api_key.strip() or not url.strip():
        st.error("Please provide all the information to proceed")
    elif not validators.url(url):
        st.error("Please enter a valid Url. It can may be a YT video utl or website url") 

    else:
        try:
            with st.spinner("Loading content..."):
                # Load the website from URL or YT video
                if "youtube.com" in url or "youtu.be" in url:
                    loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)
                    docs = loader.load()
                else:
                    #Website content loader
                    loader = UnstructuredURLLoader(
                        urls=[url],
                        ssl_verify=False,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
                    )
                    
                docs = loader.load()

                ##Chain for Summarization
                chain = load_summarize_chain(
                    llm, 
                    chain_type="stuff", 
                    prompt=prompt
                )

                output_summary = chain.run(docs)

                st.success("Summary Generated Successfully.Here is the summary you asked for")
                st.write(output_summary)

        except Exception as e:
            st.error(f"Exception: {e}")







