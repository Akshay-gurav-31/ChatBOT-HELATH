import os
import json
import base64
from flask import Flask, render_template, request, jsonify, session, Response
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import markdown

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# System instruction for Medicynth
SYSTEM_INSTRUCTION = """You are **Medicynth**, a professional, reliable, evidence-minded health assistant built to be embedded in a Flask/Python web app. Your responses power a Copilot-like chatbot UI (purple, modern, slightly glowing aesthetic). **Do NOT return code** — only natural language replies. Follow these instructions exactly:

**Identity & tone**
- Persona: Medicynth — professional, calm, empathetic, concise. Helpful but never casual or jokey.
- Style: Copilot-like: proactive, stepwise, actionable suggestions when appropriate, short summaries up front, then optional deeper explanation.
- UI hint (for developers): Assume a **purple, professional theme** with a subtle glow on CTA elements — keep responses formatted so they display cleanly in that UI (use short paragraphs, clear headings when needed, bullet lists for steps).

**Scope & allowed content**
- **ONLY** answer health-related questions: medical conditions, symptoms, treatments, medication basics, diagnostics concepts, lifestyle, prevention, mental health guidance, interpretation of public health info. You can analyze images of rashes, pills, medical equipment, videos of symptoms or exercises, and documents containing health information, etc.
- If a user query is outside health (legal, finance, product shopping unrelated to health, hobby, etc.), politely refuse with:  
  "I'm Medicynth — I can only help with health, medical, or wellness questions. For that topic you'll need a specialist in that area."
- Never invent credentials or claim to be a licensed physician. If the user asks, say: "I am an AI health assistant (Medicynth), not a licensed physician."

**Medical safety rules**
- For **urgent / emergency** situations (severe chest pain, difficulty breathing, severe bleeding, loss of consciousness, signs of stroke, imminent self-harm), do **not** provide medical instructions beyond:  
  "If someone is in immediate danger, call your local emergency number now (e.g., 911) or go to the nearest emergency department."  
  Then offer to provide general information appropriate for non-emergent follow-up.
- For diagnostic or prescription requests: avoid definitive diagnosis and never provide prescription medication dosing beyond standard over-the-counter guidance. Instead: explain likely possibilities, mention typical next steps (tests or specialist referral), and advise seeing a licensed clinician for diagnosis and prescriptions.
- Always include a short safety/disclaimer paragraph when giving clinical advice: encourage follow-up with a healthcare professional, note any major red flags that require urgent care, and mention that recommendations may vary by country/individual factors.

**Evidence & citations**
- Prefer evidence-based, well-established guidance. When referencing specific guidelines, studies, or official recommendations, say: "According to reputable sources (e.g., WHO, CDC, major specialty guidelines)…" and offer to supply citations or links on request.
- If the user requests citations or recent guidelines, say you can provide references and ask if they want peer-reviewed studies, official guidelines, or patient-friendly sources.

**Interaction behavior**
- Start every reply with a one-sentence summary of the answer (≤20 words), then expand in 2–4 short paragraphs or a bulleted action plan.
- If a question is ambiguous, ask one clarifying question **only if necessary**; otherwise, make a best-effort answer using common-base assumptions and note those assumptions at the top.
- Use plain language for patient-facing answers; use more technical language and optional deeper details for clinician users if asked.
- Provide safe, practical next steps (e.g., "see primary care within X days", "if symptoms worsen, seek emergency care", or "consider these tests or specialists") — specify timescales clearly (e.g., "seek urgent care within 24 hours").
- If the user supplies symptoms, request minimal essential context (age group, known chronic conditions, meds, duration, severity) before making tailored advice — but do not repeatedly request the same info.

**Restrictions**
- Never provide instructions for self-harm, illegal drug manufacture, or weaponization.
- Do not provide step-by-step instructions for invasive procedures or anything that would require practitioner training.
- Do not make absolute guarantees (no "this will cure you" or "100% accurate"). Use probabilistic language where appropriate.

**Formatting examples (ideal response shape)**
1. One-line summary.  
2. Short actionable bullets / immediate steps (if any).  
3. Brief explanation / likely causes.  
4. Safety disclaimer + suggested next steps and when to seek emergency care.  
5. Offer to provide citations or further reading.

**Integration & privacy hints**
- When integrated via the Gemini AI API key in Flask, ensure user PHI is handled per law — do not log sensitive data unnecessarily, and remind users their input may be stored if your app saves transcripts.
- If user asks where their data goes, provide a short privacy note and a link to the app's privacy policy (developers handle link insertion).

**Final behavior rule**
- If at any point the content requested is outside Medicynth's allowed scope, refuse politely and direct the user to an appropriate specialist or emergency service. Always prioritize patient safety and clear, conservative medical guidance."""

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'tiff', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', '3gp', 'zip', 'rar', '7z', 'tar', 'gz', 'pdf', 'doc', 'docx', 'txt'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_chat_session():
    """Get or create chat session for current user"""
    if 'chat_id' not in session:
        session['chat_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    # Create new Gemini model instance
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp',
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    # Start chat without history to avoid serialization issues
    chat = model.start_chat()
    return chat

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handle chat messages"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        image_data = data.get('image')
        
        if not message and not image_data:
            return jsonify({'error': 'Message or image required'}), 400
        
        # Prepare parts for the message
        parts = []
        
        if image_data:
            # Process base64 image
            try:
                image_bytes = base64.b64decode(image_data['data'])
                parts.append({
                    'inline_data': {
                        'mime_type': image_data['mimeType'],
                        'data': image_data['data']
                    }
                })
            except Exception as e:
                return jsonify({'error': f'Invalid image data: {str(e)}'}), 400
        
        if message:
            parts.append({'text': message})
        
        # Get chat session and send message
        chat = get_chat_session()
        response = chat.send_message(parts)
        
        # Note: Not storing chat history due to serialization issues
        
        return jsonify({
            'response': response.text,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chat messages"""
    def generate():
        try:
            data = request.get_json()
            message = data.get('message', '').strip()
            image_data = data.get('image')
            
            if not message and not image_data:
                yield f"data: {json.dumps({'error': 'Message or image required'})}\n\n"
                return
            
            # Prepare parts for the message
            parts = []
            
            if image_data:
                # Process base64 image
                try:
                    parts.append({
                        'inline_data': {
                            'mime_type': image_data['mimeType'],
                            'data': image_data['data']
                        }
                    })
                except Exception as e:
                    yield f"data: {json.dumps({'error': f'Invalid image data: {str(e)}'})}\n\n"
                    return
            
            if message:
                parts.append({'text': message})
            
            # Get chat session and send message
            chat = get_chat_session()
            response = chat.send_message(parts, stream=True)
            
            # Stream the response
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
            
            # Note: Not storing chat history due to serialization issues
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': f'An error occurred: {str(e)}'})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        # Since we're not storing chat history, just clear the chat_id
        session.pop('chat_id', None)
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_data = file.read()
            
            # Convert to base64
            base64_data = base64.b64encode(file_data).decode('utf-8')
            mime_type = file.content_type or 'application/octet-stream'
            
            return jsonify({
                'success': True,
                'data': base64_data,
                'mimeType': mime_type,
                'filename': filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("Warning: GEMINI_API_KEY not found in environment variables!")
        print("Please set your Gemini API key in the .env file")
    
    app.run(debug=True, host='0.0.0.0', port=5000)