import openai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai

genai_api_key = "AIzaSyAQpCmTfDd1hjWMrUqt0GuEcPYzWQJhdgs"

if not genai_api_key:
    raise Exception("Gemini API Key not found. Make sure it's set in the .env file.")

# Configure the Gemini API
genai.configure(api_key=genai_api_key)

# Function to get transcript from YouTube video
def get_transcript(youtube_url): 
    video_id = youtube_url.split("v=")[-1]
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try fetching the manual transcript
    try:
        transcript = transcript_list.find_manually_created_transcript() 
        language_code = transcript.language_code  # Save the detected language
    except:
        # If no manual transcript is found, try fetching an auto-generated transcript
        try:
            generated_transcripts = [trans for trans in transcript_list if trans.is_generated]
            transcript = generated_transcripts[0]
            language_code = transcript.language_code  # Save the detected language 
        except: 
            # If no transcript is found, raise an exception 
            raise Exception("No suitable transcript found.")
    
    full_transcript = " ".join([part['text'] for part in transcript.fetch()])
    return full_transcript, language_code  # Return both the transcript and detected language

# Function to summarize the transcript using Gemini API
def summarize_with_gemini(transcript, language_code, model_name='gemini-1.5-flash'):
    # Split the document if it's too long
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_text(transcript)
    text_to_summarize = " ".join(texts[:4])  # Adjust this as needed
    
    # Prepare the prompt for summarization
    response = genai.GenerativeModel(model_name).generate_content(f"Summarize the following text in English. Text: {text_to_summarize}")
    
    return response.text

# Main function for Streamlit app
def main():
    st.title('YouTube Video Summarizer')
    link = st.text_input('Enter the link of the YouTube video you want to summarize:')
    
    if st.button('Start'):
        if link:
            try:
                progress = st.progress(0)
                status_text = st.empty()
                status_text.text('Loading the transcript...')
                progress.progress(25)
                
                # Getting both the transcript and language code
                transcript, language_code = get_transcript(link)
                
                status_text.text('Creating summary...')
                progress.progress(75)
                
                summary = summarize_with_gemini(transcript, language_code)
                
                status_text.text('Summary:')
                st.markdown(summary)
                progress.progress(100)
            except Exception as e:
                st.write(str(e))
        else:
            st.write('Please enter a valid YouTube link.')

if __name__ == "__main__":
    main()
