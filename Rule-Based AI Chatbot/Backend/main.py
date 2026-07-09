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

# Stores user session state temporarily.
# In production, use Redis/database instead of this dictionary.
# Shape:
# sessions[session_id] = {
#     "node": "main" | submenu_key | "answer",
#     "back_to": None | "main" | submenu_key,
# }
sessions = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Single source of truth for the whole conversation tree.
#
# A node can point to another node with "next", or return a final "answer".
# Important behaviour:
# - Submenus show options.
# - Final answers do NOT show the submenu options again.
# - Back from a final answer returns to the submenu it came from.
# - Back from a submenu returns to the main menu.
# - If a main menu option points to a submenu with only one question, the app
#   skips that useless submenu and returns the answer directly.
# ---------------------------------------------------------------------------
MENU = {
    "main": {
        "title": "Decode Labs Chatbot",
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
ANSWER_STATE = "answer"


def make_session(session_id: Optional[str] = None) -> str:
    """Create a new session or reset an existing session to the main menu."""
    session_id = session_id or str(uuid4())
    sessions[session_id] = {"node": "main", "back_to": None}
    return session_id


def ensure_session(session_id: Optional[str]) -> str:
    """Return a valid session id, creating a new session when needed."""
    if not session_id or session_id not in sessions:
        return make_session(session_id)
    return session_id


def node_payload(session_id: str, node_key: str, message: str = "", is_error: bool = False):
    """Build the structured JSON payload the frontend renders for a menu node."""
    node = MENU[node_key]
    sessions[session_id] = {"node": node_key, "back_to": None if node_key == "main" else "main"}

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


def answer_payload(
    session_id: str,
    title: str,
    message: str,
    back_to: str,
    is_error: bool = False,
):
    """Build the payload for a final answer.

    Final answers intentionally return an empty options list. That stops the
    submenu from being repeated under the answer. The session stores where the
    Back button must return.
    """
    sessions[session_id] = {"node": ANSWER_STATE, "back_to": back_to}

    return {
        "session_id": session_id,
        "node": ANSWER_STATE,
        "title": title,
        "intro": "",
        "message": message,
        "is_error": is_error,
        "can_go_back": True,
        "options": [],
    }


def direct_single_option_if_needed(session_id: str, main_option: dict):
    """Skip a submenu when it only contains one possible question."""
    target_node_key = main_option["next"]
    target_node = MENU[target_node_key]

    if len(target_node["options"]) != 1:
        return node_payload(session_id, target_node_key)

    only_option = next(iter(target_node["options"].values()))
    return answer_payload(
        session_id=session_id,
        title=main_option["label"],
        message=only_option["answer"],
        back_to="main",
    )


@app.get("/")
def home():
    return {"message": "Decode Labs chatbot backend is running."}


@app.get("/menu")
def get_menu():
    """Structured main menu, handy for the frontend's initial load."""
    session_id = make_session()
    return node_payload(session_id, "main")


@app.post("/chatbot")
def chatbot(request: ChatRequest):
    user_message = request.message.strip().lower()
    session_id = ensure_session(request.session_id)
    state = sessions[session_id]

    # Return to main menu anytime.
    if user_message in RESET_WORDS:
        make_session(session_id)
        return node_payload(session_id, "main")

    # Back behaves according to the current depth:
    # - answer -> previous submenu, or main if the answer was opened directly
    # - submenu -> main
    # - main -> main
    if user_message in BACK_WORDS:
        back_to = state.get("back_to") or "main"
        return node_payload(session_id, back_to)

    current_node_key = state.get("node", "main")

    # If the user types while viewing a final answer, do not guess.
    # The only sensible action from this screen is Back or Menu.
    if current_node_key == ANSWER_STATE:
        return answer_payload(
            session_id=session_id,
            title="Use the back button",
            message="Please go back first, then choose another option.",
            back_to=state.get("back_to") or "main",
            is_error=True,
        )

    node = MENU[current_node_key]
    option = node["options"].get(user_message)

    if option is None:
        return node_payload(
            session_id=session_id,
            node_key=current_node_key,
            message="Invalid option. Please choose one of the options below.",
            is_error=True,
        )

    if "next" in option:
        if current_node_key == "main":
            return direct_single_option_if_needed(session_id, option)
        return node_payload(session_id, option["next"])

    # Final answer from inside a submenu.
    # The options list is intentionally empty here.
    return answer_payload(
        session_id=session_id,
        title=option["label"],
        message=option["answer"],
        back_to=current_node_key,
    )
