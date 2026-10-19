# components/voice_input.py - Voice input component using Web Speech API

import streamlit as st
import streamlit.components.v1 as components


def voice_input_button(height: int = 200) -> str:
    """
    Renders a microphone button that uses Web Speech API for speech-to-text.
    
    Returns:
        Transcribed text or empty string
    """
    
    # Generate unique key for this component instance
    if "voice_input_key" not in st.session_state:
        st.session_state.voice_input_key = 0
    
    component_html = """
    <style>
        * { box-sizing: border-box; }
        
        .voice-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 16px;
        }
        
        .mic-row {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        
        .mic-btn {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            border: 2px solid #e0e0e0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            cursor: pointer;
            font-size: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .mic-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }
        
        .mic-btn.recording {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s ease-in-out infinite;
            box-shadow: 0 4px 20px rgba(245, 87, 108, 0.5);
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.08); }
        }
        
        .status {
            font-size: 15px;
            color: #666;
        }
        
        .status.recording {
            color: #f5576c;
            font-weight: 500;
        }
        
        .transcript-box {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 16px;
            min-height: 80px;
            font-size: 15px;
            line-height: 1.6;
            color: #333;
        }
        
        .transcript-box.empty {
            color: #999;
            font-style: italic;
        }
        
        .transcript-box.has-text {
            background: #fff;
            border-color: #667eea;
        }
        
        .error-msg {
            color: #dc3545;
            font-size: 14px;
            margin-top: 8px;
        }
        
        .browser-warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            color: #856404;
        }
    </style>
    
    <div class="voice-container">
        <div id="browserCheck"></div>
        
        <div class="mic-row">
            <button class="mic-btn" id="micBtn" onclick="toggleRecording()">
                🎤
            </button>
            <span class="status" id="status">Click microphone to start speaking</span>
        </div>
        
        <div class="transcript-box empty" id="transcript">
            Your speech will appear here...
        </div>
        
        <div id="errorMsg" class="error-msg" style="display: none;"></div>
    </div>
    
    <script>
        let recognition = null;
        let isRecording = false;
        let finalTranscript = '';
        let interimTranscript = '';
        
        // Check browser support
        const browserCheck = document.getElementById('browserCheck');
        
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            browserCheck.innerHTML = `
                <div class="browser-warning">
                    ⚠️ Speech recognition is not supported in this browser. 
                    Please use Chrome, Edge, or Safari for voice input.
                </div>
            `;
            document.getElementById('micBtn').disabled = true;
            document.getElementById('micBtn').style.opacity = '0.5';
            document.getElementById('micBtn').style.cursor = 'not-allowed';
        } else {
            // Initialize speech recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            recognition.maxAlternatives = 1;
            
            recognition.onstart = () => {
                console.log('Speech recognition started');
            };
            
            recognition.onresult = (event) => {
                interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                updateTranscriptDisplay();
            };
            
            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                const errorMsg = document.getElementById('errorMsg');
                
                if (event.error === 'no-speech') {
                    errorMsg.textContent = 'No speech detected. Please try again.';
                } else if (event.error === 'audio-capture') {
                    errorMsg.textContent = 'No microphone found. Please check your microphone.';
                } else if (event.error === 'not-allowed') {
                    errorMsg.textContent = 'Microphone access denied. Please allow microphone access.';
                } else {
                    errorMsg.textContent = 'Error: ' + event.error;
                }
                errorMsg.style.display = 'block';
                
                stopRecording();
            };
            
            recognition.onend = () => {
                if (isRecording) {
                    // Restart if still recording (continuous mode)
                    try {
                        recognition.start();
                    } catch (e) {
                        console.log('Could not restart:', e);
                    }
                }
            };
        }
        
        function updateTranscriptDisplay() {
            const transcriptBox = document.getElementById('transcript');
            const fullText = finalTranscript + interimTranscript;
            
            if (fullText.trim()) {
                transcriptBox.textContent = fullText;
                transcriptBox.className = 'transcript-box has-text';
            } else {
                transcriptBox.textContent = 'Your speech will appear here...';
                transcriptBox.className = 'transcript-box empty';
            }
        }
        
        function toggleRecording() {
            if (!recognition) return;
            
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        }
        
        function startRecording() {
            const btn = document.getElementById('micBtn');
            const status = document.getElementById('status');
            const errorMsg = document.getElementById('errorMsg');
            
            // Reset
            finalTranscript = '';
            interimTranscript = '';
            errorMsg.style.display = 'none';
            updateTranscriptDisplay();
            
            try {
                recognition.start();
                isRecording = true;
                
                btn.classList.add('recording');
                btn.textContent = '⏹️';
                status.textContent = 'Listening... Click to stop';
                status.classList.add('recording');
            } catch (e) {
                console.error('Could not start recognition:', e);
            }
        }
        
        function stopRecording() {
            const btn = document.getElementById('micBtn');
            const status = document.getElementById('status');
            
            isRecording = false;
            
            try {
                recognition.stop();
            } catch (e) {
                console.log('Stop error:', e);
            }
            
            btn.classList.remove('recording');
            btn.textContent = '🎤';
            status.textContent = 'Click microphone to speak again';
            status.classList.remove('recording');
            
            // Send transcript to Streamlit
            const transcript = finalTranscript.trim();
            if (transcript) {
                // Use Streamlit's component communication
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }, '*');
            }
        }
    </script>
    """
    
    result = components.html(component_html, height=height)
    
    return result or ""


def voice_input_simple() -> str:
    """
    Simpler voice input using just a text area (fallback)
    """
    st.info("🎤 **Voice Input**: Speak your situation naturally. For example:")
    st.caption(
        '_"I\'m a single mom with two kids ages 3 and 7. '
        'I work part-time making about $24,000 a year in Texas. '
        'I need help with food, childcare, and health insurance."_'
    )
    
    transcript = st.text_area(
        "Type or paste your speech transcript here:",
        height=100,
        placeholder="Enter your situation description..."
    )
    
    return transcript
