# AI-Weather-Assistant-Python
An AI-powered weather forecasting application built using Python, Open-Meteo API, and Claude AI integration with real-time weather updates, 5-day forecasts, and custom weather alerts.
# 🌦️ AI Weather Assistant

AI Weather Assistant is a Python-based weather forecasting application that provides real-time weather updates, 5-day forecasts, and intelligent weather recommendations using APIs and AI integration.

This project was built as a beginner-to-intermediate level AI application to understand real-world API integration, object-oriented programming, and AI-powered features.

---

#  Features

-  Search weather by city name
-  Real-time weather data
-  5-Day weather forecast
-  Temperature, humidity, and wind speed tracking
-  AI-generated weather recommendations using Claude AI
-  Custom heat alert system
-  Personalized user messages
-  Weather emojis and formatted console UI

---

# Technologies Used

- Python
- Requests Library
- Open-Meteo API
- Anthropic Claude API
- Object-Oriented Programming (OOP)
- VS Code
- GitHub

---

#  Project Structure

```bash
AI-Weather-Assistant/
│
├── ai_weather_app.py
├── README.md
└── .env
```

---

# ⚙️ Installation

Install required dependencies:

```bash
pip install requests anthropic python-dotenv
```

---

# Usage

Run the application:

```bash
python ai_weather_app.py
```

Run with city name:

```bash
python ai_weather_app.py --city "Mumbai"
```

Run without AI recommendations:

```bash
python ai_weather_app.py --city "Hyderabad" --no-ai
```

---

#  API Setup

Create a `.env` file and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

---

#  Custom Features Added by Me

- Added temperature-based heat alerts
- Added personalized greeting messages
- Improved console output design
- Enhanced user interaction experience

Example:

```text
🔥 Too hot today! Stay hydrated.
😊 Have a nice day!
```

---

# 📸 Sample Output

```text
🌍 Chīrāla, Andhra Pradesh, India

🌤️ Mainly clear
Temperature : 43.8°C
Humidity    : 31%
Wind        : 12 km/h

🔥 Too hot today! Stay hydrated.
😊 Have a nice day!

5-Day Forecast:
⛈️ Thunderstorm
🌦️ Rain showers
```

---

#  Learning Outcomes

Through this project, I learned:

- API Integration
- Working with JSON data
- Python OOP concepts
- Conditional Logic
- Error Handling
- Debugging
- AI Integration
- GitHub Project Deployment

---

#  Future Improvements

- GUI version using Tkinter
- Flask web application
- Voice-based weather assistant
- Weather notifications
- Hourly forecast support
- Mobile app integration

---

# 👨‍💻 Author

**Deva Tejaswi Jupudi**  
_B.Tech – CSE (AI) Student_

---
