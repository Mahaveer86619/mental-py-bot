# MindGuide AI

A mental health assessment and guidance platform built with FastAPI and modern web technologies.

## 🚀 Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/mental-py-bot.git
   cd mental-py-bot
   ```

2. **Set up environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:

   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   APP_PASSWORD=your_email_app_password
   ```

4. **Run the application**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🏗️ Project Structure

```
mental-py-bot/
├── backend/
│   ├── core/
│   │   └── config.py         # Configuration settings
│   ├── auth.py              # Authentication logic
│   ├── gemini_chat.py       # Gemini AI integration
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── smtp_service.py      # Email service
│   ├── storage.py           # Data storage (demo)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Styles
│   │   └── js/
│   │       └── script.js    # Frontend logic
│   └── templates/
│       └── index.html       # Main HTML template
└── .env                     # Environment variables
```

## 🔑 Key Features

- User authentication with JWT
- Mental health assessments for:
  - Depression
  - Anxiety
  - Stress
- Interactive chat interface using Gemini AI
- Emergency contact system
- Progress tracking dashboard
- Responsive design

## 🛠️ Technology Stack

- **Backend**

  - FastAPI
  - Gemini AI
  - Python 3.8+
  - JWT Authentication
  - SMTP for email

- **Frontend**
  - HTML5 + CSS3
  - Vanilla JavaScript
  - Chart.js for analytics

## 👩‍💻 Development Guidelines

### API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get JWT token
- `GET /auth/users/me` - Get current user info
- `POST /chat/start` - Start new chat session
- `POST /chat/message` - Send message to AI
- `POST /chat/emergency_contact` - Send emergency contact email

### Adding New Features

1. Create new route in appropriate backend file
2. Update models if needed
3. Add frontend handler in script.js
4. Style new components in style.css

### Testing

Currently uses manual testing. Future improvements:

- Add pytest for backend
- Add frontend unit tests
- Implement E2E testing

## 🔒 Security Notes

- Store sensitive data in .env file
- Never commit .env or sensitive keys
- Use strong passwords for JWT
- Implement rate limiting for production
- Add CORS rules for production

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email your-email@example.com or open an issue on GitHub.
