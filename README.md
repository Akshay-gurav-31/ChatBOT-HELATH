# Medicynth Health Assistant - Flask Version

A professional AI-powered health assistant.

## 🚀 Features

- **AI-Powered Health Assistant** - Advanced health-focused system instructions with conversation context
- **Smart Chat Memory** - Remembers conversation history for context-aware responses
- **Multi-Language Script Preservation** - Maintains user's input script (Devanagari, Roman, Arabic, etc.)
- **Enhanced Language Detection** - Distinguishes Hindi vs Marathi in both Devanagari and Roman scripts
- **Image Upload & Analysis** - Upload medical images for AI analysis
- **Speech Recognition** - Voice input support using Web Speech API
- **Theme Switching** - Dark/Light mode toggle with localStorage persistence
- **Responsive Design** - Works on desktop and mobile devices
- **Session Management** - Chat history maintained during session with context rebuilding
- **Markdown Support** - Rich text formatting in AI responses
- **Copy Messages** - Easy copy functionality for AI responses

## 📁 Project Structure

```
TTT/
├── app.py              # Main Flask application
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML template
├── static/
│   ├── style.css      # CSS styles 
│   └── app.js         # Frontend JavaScript
└── README.md          # This file
```

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Open the `.env` file and replace `your_actual_gemini_api_key_here` with your actual API key:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🎯 Usage

1. **Start Chatting**: Type health-related questions in the input field
2. **Upload Images**: Click the attachment button to upload medical images
3. **Voice Input**: Click the microphone button to use speech recognition
4. **Theme Toggle**: Use the theme button in the sidebar to switch between dark/light modes
5. **Clear Chat**: Click the trash icon in the header or "New Chat" in sidebar to reset
6. **Copy Messages**: Hover over AI responses to see the copy button

## 🔒 Security & Privacy

- Session-based chat history (not persisted to database)
- File uploads are processed in memory (not saved to disk)
- Environment variables for secure API key storage
- CSRF protection through Flask sessions

## 🩺 Health Assistant Features

The AI assistant is specifically configured for health-related queries with:

- **Medical Safety Rules**: Proper emergency guidance and disclaimers
- **Evidence-Based Responses**: References to reputable health sources
- **Scope Limitations**: Only answers health/medical/wellness questions
- **Professional Tone**: Calm, empathetic, and professional responses
- **Safety Disclaimers**: Always encourages consulting healthcare professionals

## 🔧 Technical Details

- **Backend**: Flask (Python)
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: CSS with CSS Variables for theming
- **Session Management**: Flask sessions with UUID-based chat IDs
- **File Handling**: Base64 encoding for image uploads

## 🚨 Important Notes

1. **API Key Required**: You must get a Gemini API key to use this application
2. **Health Disclaimer**: This is an AI assistant, not a substitute for professional medical advice
3. **Emergency Situations**: The AI will direct users to emergency services for urgent situations
4. **Privacy**: Chat data is stored in session only, not persisted to database

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🎨 UI/UX Features

- **Modern Purple Theme**: Professional medical aesthetic
- **Smooth Animations**: Hover effects and transitions
- **Loading States**: Visual feedback during AI processing
- **Message Formatting**: Markdown support with proper styling
- **Accessibility**: ARIA labels and keyboard navigation support

**Made with ❤️ Team Medicynth**