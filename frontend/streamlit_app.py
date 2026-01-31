"""
Enhanced Streamlit Frontend with Live Microphone Recording
"""
import streamlit as st
import requests
import base64
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from streamlit_mic_recorder import mic_recorder
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
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
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
        help="Your secret API key"
    )
    
    st.divider()
    
    st.header("ℹ️ About")
    st.info("""
    This system uses advanced machine learning to analyze audio features and 
    determine if a voice is AI-generated or human.
    
    **Supported Languages:**
    - Tamil (தமிழ்)
    - English
    - Hindi (हिन्दी)
    - Malayalam (മലയാളം)
    - Telugu (తెలుగు)
    """)
    
    st.divider()
    
    st.markdown("""
    **How it works:**
    1. Upload MP3 or record live
    2. Select language
    3. Get instant results
    
    **Accuracy**: 90%+
    **Max Duration**: 30 seconds
    """)

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
            result = response.json()
            return result, None
        elif response.status_code == 401:
            return None, "Invalid API Key. Please check your credentials in the sidebar."
        else:
            error_msg = response.json().get('detail', 'Unknown error')
            return None, f"Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout. The server took too long to respond."
    except requests.exceptions.ConnectionError:
        return None, f"Cannot connect to API at {api_url}. Make sure the backend is running."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def analyze_fraud(audio_data, language, api_url, api_key):
    """Helper function to analyze fraud risk"""
    try:
        # Calls the new /api/call-analysis endpoint
        fraud_url = api_url.replace("/api/voice-detection", "/api/call-analysis")
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        payload = {
            "language": language,
            "audioFormat": "mp3",
            "audioBase64": audio_base64
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
        response = requests.post(
            fraud_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, response.json().get('detail', 'Unknown error')
            
    except Exception as e:
        return None, str(e)

def display_results(result):
    """Display analysis results"""
    st.success("✅ Analysis Complete!")
    
    # Results in columns
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        if result['classification'] == 'AI_GENERATED':
            st.metric(
                "Classification",
                "🤖 AI Generated",
                delta="Synthetic Voice"
            )
        else:
            st.metric(
                "Classification",
                "👤 Human Voice",
                delta="Natural Voice"
            )
    
    with res_col2:
        confidence_pct = result['confidenceScore'] * 100
        st.metric(
            "Confidence Score",
            f"{confidence_pct:.1f}%"
        )
    
    # Confidence gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence_pct,
        title={'text': "Confidence Level", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen" if confidence_pct > 70 else "orange"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 75], 'color': "gray"},
                {'range': [75, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.info(f"**Explanation:** {result['explanation']}")
    
    # Full results
    with st.expander("📄 View Full Results"):
        st.json(result)

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎵 Upload Audio", 
    "🎙️ Live Recording", 
    "🛡️ Call Analyzer",
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


with tab3:
    st.subheader("🛡️ Real-time Call Security Analyzer")
    st.info("Detect spam, fraud, and synthetic voices in real-time")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📞 Call Simulation")
        record_lang_fraud = st.selectbox("Call Language", ["English", "Tamil", "Hindi", "Telugu"], key="fraud_lang")
        
        audio_data_fraud = mic_recorder(
            start_prompt="📞 Start Call",
            stop_prompt="📴 End Call",
            key="fraud_recorder",
            format="wav"
        )
        
        if audio_data_fraud:
            audio_bytes = audio_data_fraud['bytes']
            st.audio(audio_bytes, format='audio/wav')
            if st.button("🛡️ Scan for Threats", type="primary", key="scan_fraud"):
                with st.spinner("Analyzing call patterns..."):
                    result, error = analyze_fraud(audio_bytes, record_lang_fraud, api_url, api_key)
                    
                    if result:
                        # Display Fraud Results
                        risk_score = result['fraud_analysis']['risk_score']
                        risk_level = result['fraud_analysis']['risk_level']
                        
                        # Risk Banner
                        color = "green"
                        if risk_level == "HIGH": color = "orange"
                        if risk_level == "CRITICAL": color = "red"
                        
                        st.markdown(f"""
                        <div style='background-color: {color}; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;'>
                            <h2 style='margin:0'>THREAT LEVEL: {risk_level}</h2>
                            <p style='margin:0; font-size: 1.2em'>Risk Score: {risk_score}/100</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("AI Call Probability", f"{result['fraud_analysis']['metrics']['ai_probability']}%")
                        with c2:
                            st.metric("Urgency Score", f"{result['fraud_analysis']['metrics']['urgency_score']}%")
                            
                        # Alerts
                        st.subheader("⚠️ Detected Threats")
                        alerts = result['fraud_analysis']['alerts']
                        if alerts:
                            for alert in alerts:
                                st.error(alert)
                        else:
                            st.success("✅ No immediate threats detected")
                            
                        # Transcript Display for Debugging
                        with st.expander("📝 Call Transcript", expanded=True):
                            transcript_data = result.get('transcript_data', {})
                            transcript_text = transcript_data.get('transcript', 'No transcript available')
                            keywords = transcript_data.get('keywords_found', [])
                            
                            st.markdown(f"**Recognized Text:**")
                            st.info(transcript_text)
                            
                            if keywords:
                                st.markdown(f"**Keywords Matched:** `{'`, `'.join(keywords)}`")
                            else:
                                st.markdown("**Keywords Matched:** None")
                                
                        with st.expander("🔍 Detailed Analysis"):
                            st.json(result)
                    else:
                        st.error(error)
    
    with col2:
        st.markdown("""
        ### 🛡️ Protection Features
        
        **1. Synthetic Voice Prevention**
        Detects if the caller is using AI/Deepfake technology.
        
        **2. Behavioral Analysis**
        Identifies pressure tactics, urgency, and aggressive speech patterns common in scams.
        
        **3. Keyword Monitoring**
        (Coming Soon) Real-time keyword scanning for 'password', 'OTP', 'bank'.
        """)
    
    with col2:
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
    st.subheader("🎙️ Live Voice Recording")
    st.info("Record your voice directly from your microphone for instant analysis!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Language selection for recording
        record_language = st.selectbox(
            "Select Language",
            ["English", "Tamil", "Hindi", "Malayalam", "Telugu"],
            help="Language of your voice",
            key="record_lang"
        )
        
        st.markdown("### 🎤 Click below to start recording:")
        
        st.markdown("### 🎤 Click below to start recording:")
        
        # Audio recorder widget (streamlit-mic-recorder)
        audio_data = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            key="recorder",
            format="wav"
        )
        
        if audio_data:
            audio_bytes = audio_data['bytes']
            st.audio(audio_bytes, format='audio/wav')
            
            col_a, col_b = st.columns([1, 1])
            
            with col_a:
                if st.button("🔍 Analyze Recording", type="primary", key="analyze_recording"):
                    with st.spinner("Analyzing your voice... This may take a few seconds..."):
                        result, error = analyze_audio(audio_bytes, record_language, api_url, api_key)
                        
                        if result:
                            display_results(result)
                            
                            # Download results
                            st.download_button(
                                label="📥 Download Results (JSON)",
                                data=json.dumps(result, indent=2),
                                file_name=f"live_analysis_{record_language}.json",
                                mime="application/json",
                                key="download_recording"
                            )
                        else:
                            st.error(f"❌ {error}")
            
            with col_b:
                if st.button("🔄 Record Again", key="record_again"):
                    st.rerun()
    
    with col2:
        st.subheader("🎙️ Recording Tips")
        st.markdown("""
        **For best results:**
        - 🔇 Find a quiet environment
        - 🎯 Speak clearly
        - 📏 Keep 5-30 seconds
        - 🎚️ Use good microphone
        
        **What to say:**
        - Read a sentence
        - Introduce yourself
        - Natural conversation
        - Any speech sample
        """)
        
        st.divider()
        
        st.success("""
        **Live Recording Benefits:**
        - ⚡ Instant analysis
        - 🚫 No file upload needed
        - 🎤 Direct from mic
        - 🔒 Privacy-friendly
        """)

with tab3:
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

with tab4:
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
    
    result = response.json()
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidenceScore']}")
    ```
    
    ### Example with cURL
    ```bash
    curl -X POST http://localhost:8000/api/voice-detection \\
      -H "Content-Type: application/json" \\
      -H "x-api-key: YOUR_API_KEY" \\
      -d '{
        "language": "English",
        "audioFormat": "mp3",
        "audioBase64": "BASE64_STRING..."
      }'
    ```
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI Voice Detection System v1.0 | Built with FastAPI & Streamlit</p>
    <p>Supports Tamil, English, Hindi, Malayalam, and Telugu</p>
    <p>✨ NEW: Live microphone recording feature!</p>
</div>
""", unsafe_allow_html=True)
