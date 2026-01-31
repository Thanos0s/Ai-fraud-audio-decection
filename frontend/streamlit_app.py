"""
Enhanced Streamlit Frontend - Cloud Optimized Version
"""
import streamlit as st
import requests
import base64
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import io

# Page configuration
st.set_page_config(
    page_title="AI Voice Detection",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Configuration
DEFAULT_API_URL = "http://localhost:8000/api/voice-detection"
DEFAULT_API_KEY = "sk_test_voice_detection_2026"

# Title and description
st.title("🎤 AI-Generated Voice Detection")
st.markdown("""
Detect whether a voice sample is AI-generated or spoken by a real human.
Supports **Tamil, English, Hindi, Malayalam, and Telugu**.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API Endpoint",
        value=DEFAULT_API_URL,
        help="Backend API URL"
    )
    
    api_key = st.text_input(
        "API Key",
        value=DEFAULT_API_KEY,
        type="password",
        help="Authentication key"
    )
    
    st.divider()
    
    st.header("ℹ️ About")
    st.markdown("""
    This tool uses advanced AI to detect synthetic voices across multiple languages.
    
    **Supported Languages:**
    - 🇮🇳 Tamil
    - 🇬🇧 English
    - 🇮🇳 Hindi
    - 🇮🇳 Malayalam
    - 🇮🇳 Telugu
    """)

# Helper Functions
def analyze_audio(audio_data, language, api_url, api_key):
    """Helper function to analyze audio"""
    try:
        # Convert to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Prepare request
        payload = {
            "language": language,
            "audioFormat": "mp3",
            "audioBase64": audio_base64
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        # Make API request
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 401:
            return None, "Invalid API key"
        elif response.status_code == 400:
            return None, f"Bad request: {response.json().get('message', 'Unknown error')}"
        else:
            return None, f"API error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Request timed out. Backend might be starting up, please try again."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Please check API URL."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def display_results(result):
    """Display analysis results in a nice format"""
    classification = result.get('classification', 'UNKNOWN')
    confidence = result.get('confidenceScore', 0.0)
    explanation = result.get('explanation', 'No explanation provided')
    
    # Color coding
    if classification == 'AI_GENERATED':
        color = 'red'
        icon = '🤖'
    else:
        color = 'green'
        icon = '👤'
    
    # Display banner
    st.markdown(f"""
    <div style='padding: 20px; border-radius: 10px; background-color: {color}20; border-left: 5px solid {color};'>
        <h2 style='color: {color}; margin: 0;'>{icon} {classification.replace('_', ' ')}</h2>
        <p style='font-size: 24px; margin: 10px 0;'><strong>Confidence: {confidence*100:.1f}%</strong></p>
        <p style='margin: 0;'>{explanation}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Confidence gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = confidence * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Confidence Score"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Full results
    with st.expander("📄 View Full Results"):
        st.json(result)

# Main content - Simplified for cloud deployment
tab1, tab2, tab3 = st.tabs([
    "🎵 Upload Audio", 
    "📊 Batch Analysis", 
    "📖 API Documentation"
])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Voice Sample")
        
        # Language selection
        language = st.selectbox(
            "Select Language",
            ["English", "Tamil", "Hindi", "Malayalam", "Telugu"],
            help="Language of the audio sample",
            key="upload_lang"
        )
        
        # File upload
        audio_file = st.file_uploader(
            "Upload MP3 Audio File",
            type=['mp3'],
            help="Maximum 30 seconds"
        )
        
        if audio_file is not None:
            # Display audio player
            st.audio(audio_file, format='audio/mp3')
            
            # Analysis button
            if st.button("🔍 Analyze Voice", type="primary", key="analyze_upload"):
                with st.spinner("Analyzing audio... This may take a few seconds..."):
                    audio_bytes = audio_file.read()
                    result, error = analyze_audio(audio_bytes, language, api_url, api_key)
                    
                    if result:
                        display_results(result)
                        
                        # Download results
                        st.download_button(
                            label="📥 Download Results (JSON)",
                            data=json.dumps(result, indent=2),
                            file_name=f"voice_analysis_{language}.json",
                            mime="application/json"
                        )
                    else:
                        st.error(f"❌ {error}")


    with col2:
        st.subheader("📋 How It Works")
        st.markdown("""
        ### 🛡️ Protection Features
        
        **1. Synthetic Voice Prevention**
        Detects if the caller is using AI/Deepfake technology.
        
        **2. Multi-Language Support**
        Works across 5 Indian and international languages.
        
        **3. Fast Analysis**
        Results in seconds with detailed confidence scores.
        """)
    
        st.divider()
        
        st.subheader("📋 Quick Guide")
        st.markdown("""
        **Steps:**
        1. ✅ Select language
        2. 📤 Upload MP3 file
        3. 🔍 Click "Analyze Voice"
        4. 📊 View results
        
        **Requirements:**
        - 📁 MP3 format only
        - ⏱️ Max 30 seconds
        - 🎵 Clear audio quality
        
        **Tip:** For best results, use clear audio without background noise.
        """)
        
        st.divider()
        
        st.subheader("🎯 Example Use Cases")
        st.markdown("""
        - Verify voice authenticity
        - Detect deepfake audio
        - Content moderation
        - Research purposes
        """)

with tab2:
    st.subheader("📊 Batch Analysis")
    st.info("Upload multiple audio files for batch processing")
    
    uploaded_files = st.file_uploader(
        "Upload Multiple MP3 Files",
        type=['mp3'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        batch_language = st.selectbox(
            "Select Language for All Files",
            ["English", "Tamil", "Hindi", "Malayalam", "Telugu"],
            key="batch_lang"
        )
        
        if st.button("🚀 Process Batch", key="batch_btn"):
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}... ({idx+1}/{len(uploaded_files)})")
                
                audio_bytes = file.read()
                result, error = analyze_audio(audio_bytes, batch_language, api_url, api_key)
                
                if result:
                    results.append({
                        "File": file.name,
                        "Classification": result['classification'],
                        "Confidence": f"{result['confidenceScore']*100:.1f}%",
                        "Explanation": result['explanation']
                    })
                else:
                    results.append({
                        "File": file.name,
                        "Classification": "ERROR",
                        "Confidence": "N/A",
                        "Explanation": error or "Processing failed"
                    })
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ Batch processing complete!")
            
            # Display results table
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            if len(df) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    ai_count = len(df[df['Classification'] == 'AI_GENERATED'])
                    st.metric("AI Generated", ai_count)
                with col2:
                    human_count = len(df[df['Classification'] == 'HUMAN'])
                    st.metric("Human Voice", human_count)
                with col3:
                    error_count = len(df[df['Classification'] == 'ERROR'])
                    st.metric("Errors", error_count)
            
            # Download batch results
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Batch Results (CSV)",
                csv,
                "batch_results.csv",
                "text/csv"
            )

with tab3:
    st.subheader("📖 API Documentation")
    
    st.markdown("""
    ### Endpoint
    ```
    POST /api/voice-detection
    ```
    
    ### Authentication
    Add your API key in the request header:
    ```
    x-api-key: YOUR_API_KEY
    ```
    
    ### Request Body
    ```json
    {
        "language": "Tamil",
        "audioFormat": "mp3",
        "audioBase64": "BASE64_ENCODED_AUDIO..."
    }
    ```
    
    **Parameters:**
    - `language`: One of `Tamil`, `English`, `Hindi`, `Malayalam`, `Telugu`
    - `audioFormat`: Always `mp3`
    - `audioBase64`: Base64-encoded MP3 file (max 30 seconds)
    
    ### Response (Success)
    ```json
    {
        "status": "success",
        "language": "Tamil",
        "classification": "AI_GENERATED",
        "confidenceScore": 0.91,
        "explanation": "Unnatural pitch consistency detected"
    }
    ```
    
    ### Example with Python
    ```python
    import requests
    import base64
    
    # Read audio file
    with open('audio.mp3', 'rb') as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    
    # Make request
    response = requests.post(
        'http://localhost:8000/api/voice-detection',
        headers={'x-api-key': 'YOUR_API_KEY'},
        json={
            'language': 'English',
            'audioFormat': 'mp3',
            'audioBase64': audio_base64
        }
    )
    
    print(response.json())
    ```
    
    ### Error Response
    ```json
    {
        "status": "error",
        "message": "Invalid API key or malformed request"
    }
    ```
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🎤 AI Voice Detection System | Powered by Advanced Machine Learning</p>
</div>
""", unsafe_allow_html=True)
