from http.client import HTTPException
import google.generativeai as genai
import logging
from typing import List, Dict, Any, Tuple

from .core.config import settings
from .models import ChatState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    # Set up the model configuration (optional, adjust as needed)
    generation_config = {
        "temperature": 0.7,  # Adjust creativity vs factualness
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,  # Adjust based on expected report length
    }
    safety_settings = [  # Adjust safety settings carefully
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",  # Or another suitable model
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    logger.info("Gemini AI configured successfully.")
except Exception as e:
    logger.error(f"Failed to configure Gemini AI: {e}")
    gemini_model = None

# Constants for assessment flow
MAX_PERSONAL_QUESTIONS = 1  # Only one general personal question
MAX_ASSESSMENT_QUESTIONS = 5  # Limit to 5 yes/no assessment questions

# Add doctor recommendations
DOCTORS_LIST = {
    "anxiety": [
        {
            "name": "Dr. Sharma",
            "specialty": "Anxiety & Panic Disorders",
            "contact": "+91 9876543210",
        },
        {
            "name": "Dr. Patel",
            "specialty": "Clinical Psychology",
            "contact": "+91 8765432109",
        },
    ],
    "depression": [
        {
            "name": "Dr. Kumar",
            "specialty": "Depression & Mood Disorders",
            "contact": "+91 7654321098",
        },
        {"name": "Dr. Singh", "specialty": "Psychiatry", "contact": "+91 6543210987"},
    ],
    "stress": [
        {
            "name": "Dr. Reddy",
            "specialty": "Stress Management",
            "contact": "+91 5432109876",
        },
        {
            "name": "Dr. Joshi",
            "specialty": "Behavioral Therapy",
            "contact": "+91 4321098765",
        },
    ],
}

# Add question themes for AI generation
ASSESSMENT_THEMES = {
    "depression": [
        "mood and sadness",
        "loss of interest or pleasure",
        "sleep patterns",
        "self-worth and guilt",
        "thoughts of self-harm",
    ],
    "anxiety": [
        "worry and nervousness",
        "avoidance behaviors",
        "panic and physical symptoms",
        "sleep and restlessness",
        "impact on daily life",
    ],
    "stress": [
        "feeling overwhelmed",
        "physical symptoms",
        "concentration and memory",
        "irritability and mood",
        "relaxation and coping",
        "coping mechanisms",
    ],
}


def get_question_prompt(theme: str) -> str:
    return f"""
    You are an AI mental health assistant.
    Your task is to generate a single yes/no question about {theme} that helps assess mental health.
    The question should be direct, sensitive, and use everyday language that a normal person can understand.
    The question should not be insensitive or offensive.
    The question should be related to the theme.
    The question should be short and concise.
    Format: Only return the question text, nothing else.
    Example: "Do you often feel overwhelmed by daily tasks?"
    """


async def get_assessment_prompt(condition: str, question_num: int) -> str:
    condition_key = condition.lower()
    theme = ASSESSMENT_THEMES[condition_key][question_num]

    try:
        chat = gemini_model.start_chat(history=[])
        response = await chat.send_message_async(get_question_prompt(theme))
        question = response.text.strip().strip('"').strip()

        # Ensure question ends with ?
        if not question.endswith("?"):
            question += "?"

        return f"Question {question_num + 1}/5:\n{question}\n(Answer Yes or No)"
    except Exception as e:
        logger.error(f"Failed to generate question: {e}")
        # Fallback questions if AI generation fails
        fallback_questions = {
            "depression": [
                "Do you often feel sad or down?",
                "Have you lost interest in things you used to enjoy?",
                "Are you having trouble with sleep?",
                "Do you feel worthless or guilty?",
                "Have you had thoughts of harming yourself?",
            ],
            "anxiety": [
                "Do you frequently feel nervous or anxious?",
                "Do you avoid situations due to anxiety?",
                "Do you have panic attacks?",
                "Do you have trouble sleeping due to worry?",
                "Does anxiety interfere with your daily life?",
            ],
            "stress": [
                "Do you feel overwhelmed daily?",
                "Do you have frequent headaches/tension?",
                "Do you have trouble concentrating?",
                "Do you feel irritable often?",
                "Do you find it hard to relax?",
            ],
        }
        return f"Question {question_num + 1}/5:\n{fallback_questions[condition_key][question_num]}\n(Answer Yes or No)"


# --- Prompt Engineering ---


def get_initial_prompt() -> str:
    return (
        "Welcome to MindGuide AI!\n\n"
        "Choose a test to begin:\n"
        "1. Depression Test\n"
        "2. Anxiety Test\n"
        "3. Stress Test\n\n"
        "Type 1, 2, or 3 to start."
    )


def get_personal_info_prompt(condition: str) -> str:
    return f"Let's begin the {condition} assessment. I'll ask you 5 questions. Please answer with Yes or No only.\n\nFirst question:"


def get_report_prompt(condition: str, history: List[Dict[str, Any]]) -> str:
    yes_count = sum(
        1
        for msg in history
        if msg["role"] == "user" and msg["parts"][0].strip().lower() == "yes"
    )
    score = int((yes_count / MAX_ASSESSMENT_QUESTIONS) * 10)

    severity = "low" if score <= 3 else "moderate" if score <= 6 else "severe"

    report = f"""
Assessment Complete

Score: {score}/10
Severity: {severity.upper()}

"""

    if severity == "severe":
        doctors = DOCTORS_LIST[condition.lower()]
        report += "\nRecommended Doctors:\n"
        for doc in doctors:
            report += f"- {doc['name']} ({doc['specialty']}): {doc['contact']}\n"

    # Provide general recommendations based on the condition
    report += get_recommendations(condition.lower(), severity)

    # Add a disclaimer at the end of the report
    report += (
        "\n\nDisclaimer: This assessment is for informational purposes only and "
        "does not constitute medical advice. Please consult with a qualified "
        "healthcare professional for diagnosis and treatment."
    )

    return report


def get_recommendations(condition: str, severity: str) -> str:
    """Provides general recommendations based on the condition and severity."""
    recommendations = "\n\nRecommendations:\n"

    if condition == "depression":
        recommendations += (
            "- Consider talking to a therapist or counselor.\n"
            "- Engage in activities you used to enjoy, even if you don't feel like it.\n"
            "- Maintain a regular sleep schedule and healthy diet.\n"
        )
    elif condition == "anxiety":
        recommendations += (
            "- Practice relaxation techniques such as deep breathing or meditation.\n"
            "- Limit caffeine and alcohol intake.\n"
            "- Engage in regular physical activity.\n"
        )
    elif condition == "stress":
        recommendations += (
            "- Identify and manage stressors in your life.\n"
            "- Practice mindfulness and relaxation techniques.\n"
            "- Ensure you get enough sleep and exercise.\n"
        )

    if severity in ["moderate", "severe"]:
        recommendations += (
            "- It is highly recommended to seek professional help from a mental "
            "health expert.\n"
        )

    return recommendations


# --- Main Chat Function ---


async def handle_chat_message(
    user_id: str, user_message: str, current_state: ChatState
) -> Tuple[str, ChatState]:
    """Handles chat messages with direct responses."""
    current_state.history.append({"role": "user", "parts": [user_message]})

    try:
        if current_state.stage == "start":
            # Handle initial test selection
            selection = user_message.strip()
            conditions = {"1": "Depression", "2": "Anxiety", "3": "Stress"}

            if selection not in conditions:
                return "Please type 1, 2, or 3 to select a test.", current_state

            current_state.condition = conditions[selection]
            current_state.stage = "assessment"
            current_state.question_count = 0

            response = await get_assessment_prompt(current_state.condition, 0)
            current_state.history.append({"role": "model", "parts": [response]})
            return response, current_state

        elif current_state.stage == "assessment":
            answer = user_message.lower()
            if answer not in ("yes", "no"):
                return "Please answer with Yes or No only.", current_state

            current_state.question_count += 1

            if current_state.question_count < MAX_ASSESSMENT_QUESTIONS:
                response = await get_assessment_prompt(
                    current_state.condition, current_state.question_count
                )
                current_state.history.append({"role": "model", "parts": [response]})
                return response, current_state
            else:
                report = get_report_prompt(
                    current_state.condition, current_state.history
                )
                current_state.stage = "done"
                current_state.history.append({"role": "model", "parts": [report]})
                return report, current_state

        elif current_state.stage == "done":
            return (
                "Assessment complete. Click 'Take New Test' to start another assessment.",
                current_state,
            )

    except Exception as e:
        logger.error(f"Error in chat message handling: {e}")
        return "An error occurred. Please try again.", current_state


async def start_new_chat(user_id: str) -> Tuple[str, ChatState]:
    """Starts a new chat with direct initial message."""
    logger.info(f"Starting new chat for user {user_id}")
    new_state = ChatState(stage="start", history=[])

    initial_message = (
        "Welcome to MindGuide AI!\n\n"
        "Choose a test to begin:\n"
        "1. Depression Test\n"
        "2. Anxiety Test\n"
        "3. Stress Test\n\n"
        "Type 1, 2, or 3 to start."
    )

    new_state.history.append({"role": "model", "parts": [initial_message]})
    new_state.stage = "start"

    return initial_message, new_state
