from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # okay for development, restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stores user session state temporarily
# In production, use Redis/database instead of this dictionary
sessions = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Single source of truth for the whole conversation tree.
# Each node has a title, an optional intro line, and a set of options.
# An option either points at another node ("next") or is a leaf with an
# "answer" that is shown while staying on the current node (so the user can
# keep asking other questions in the same submenu, matching the original
# behaviour).
# ---------------------------------------------------------------------------
MENU = {
    "main": {
        "title": "Decode Labs Chatbot 🤖",
        "intro": "Welcome! Please choose an option:",
        "options": {
            "1": {"label": "About Decode Labs", "next": "about"},
            "2": {"label": "Services & Internship Tracks", "next": "services"},
            "3": {"label": "Internship Details", "next": "internship_details"},
            "4": {"label": "Application & Fees", "next": "application"},
            "5": {"label": "Contact Decode Labs", "next": "contact"},
        },
    },
    "about": {
        "title": "About Decode Labs",
        "options": {
            "1": {
                "label": "What does Decode Labs do?",
                "answer": "Decode Labs empowers learners worldwide through mentor-led virtual internships, real projects, and industry-ready skill development.",
            },
            "2": {
                "label": "Who can apply for Decode Labs internships?",
                "answer": "Students, recent graduates, and early-career professionals can apply. Most tracks are beginner-friendly and mentor-guided.",
            },
        },
    },
    "services": {
        "title": "Services & Internship Tracks",
        "options": {
            "1": {
                "label": "What services does Decode Labs offer?",
                "answer": "Decode Labs offers virtual internships in domains such as AI, Data Science, Web Development, and more. The focus is hands-on experience, mentorship, and portfolio-building.",
            },
            "2": {
                "label": "Can I get help choosing the right internship track?",
                "answer": "Yes. You can use the Course Selector and advisor support to choose the best track based on your goals, current skills, and target role.",
            },
        },
    },
    "internship_details": {
        "title": "Internship Details",
        "options": {
            "1": {
                "label": "Are the internships remote and accessible globally?",
                "answer": "Yes. The programs are designed for global access with remote-friendly delivery. Mentoring sessions and support are coordinated to help learners across different time zones.",
            },
            "2": {
                "label": "What is the duration and weekly commitment?",
                "answer": "Current internship cohorts are structured as 4-week programs with guided weekly milestones. Most learners spend around 8–11 hours per week depending on the selected track.",
            },
            "3": {
                "label": "Will I work on real-world projects?",
                "answer": "Yes. Each track includes practical deliverables and at least 3 live project components, helping learners build a portfolio for applications and interviews.",
            },
            "4": {
                "label": "Do I get mentorship and feedback?",
                "answer": "Yes. Learners receive mentor checkpoints, project feedback, and guidance on implementation quality, problem-solving, and presentation of outcomes.",
            },
            "5": {
                "label": "Is a certificate provided upon completion?",
                "answer": "Yes. Learners who complete the required milestones and project submissions receive a completion certificate. Verification support is also available through the website.",
            },
        },
    },
    "application": {
        "title": "Application & Fees",
        "options": {
            "1": {
                "label": "How do I apply for an internship?",
                "answer": "You can apply for internships through the official Decode Labs website. Navigate to the Internships section and follow the application instructions.",
            },
            "2": {
                "label": "Do I need to pay any fees for the internship?",
                "answer": "No. There are no fees associated with the internship program. It is completely free of charge.",
            },
        },
    },
    "contact": {
        "title": "Contact Decode Labs",
        "options": {
            "1": {
                "label": "How can I contact Decode Labs?",
                "answer": "You can contact Decode Labs through the official website: https://www.decodelabs.tech/index.html or by email at hr@decodelabs.tech.",
            },
        },
    },
}

RESET_WORDS = {"menu", "main menu", "start", "restart"}
BACK_WORDS = {"back"}


def node_payload(session_id: str, node_key: str, message: str = "", is_error: bool = False):
    """Build the structured JSON payload the frontend renders."""
    node = MENU[node_key]
    return {
        "session_id": session_id,
        "node": node_key,
        "title": node["title"],
        "intro": node.get("intro", ""),
        "message": message,
        "is_error": is_error,
        "can_go_back": node_key != "main",
        "options": [
            {"key": key, "label": opt["label"]}
            for key, opt in node["options"].items()
        ],
    }


@app.get("/")
def home():
    return {"message": "Decode Labs chatbot backend is running."}


@app.get("/menu")
def get_menu():
    """Structured main menu, handy for the frontend's initial load."""
    session_id = str(uuid4())
    sessions[session_id] = "main"
    return node_payload(session_id, "main")


@app.post("/chatbot")
def chatbot(request: ChatRequest):
    user_message = request.message.strip().lower()
    session_id = request.session_id or str(uuid4())

    if session_id not in sessions:
        sessions[session_id] = "main"

    current_state = sessions[session_id]

    # Return to main menu anytime
    if user_message in RESET_WORDS:
        sessions[session_id] = "main"
        return node_payload(session_id, "main")

    # "back" always goes up to main (tree is only two levels deep)
    if user_message in BACK_WORDS:
        sessions[session_id] = "main"
        return node_payload(session_id, "main")

    node_key = current_state
    node = MENU[node_key]
    option = node["options"].get(user_message)

    if option is None:
        return node_payload(
            session_id,
            node_key,
            message="Invalid option. Please choose one of the options below.",
            is_error=True,
        )

    if "next" in option:
        # Moving into a submenu
        sessions[session_id] = option["next"]
        return node_payload(session_id, option["next"])

    # Leaf answer: stay on the same node so the user can ask another question
    return node_payload(session_id, node_key, message=option["answer"])