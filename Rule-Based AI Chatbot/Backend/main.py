from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

menu = """
Welcome to Decode Labs Chatbot 🤖

Please choose an option:

1. What does Decode Labs do?
2. What services does Decode Labs offer?
3. How can I contact Decode Labs?
4. Who can apply for these internships?
5. Are the internships remote and accessible globally?
6. What is the duration and weekly commitment?
7. Will I work on real-world projects?
8. Do I get mentorship and feedback?
9. Is a certificate provided upon completion?
10. Can I get help choosing the right internship track?
11. How do I apply for internship?
12. Do I need to pay any fees for the internship?
"""

responses = {
    "1": "Decode Labs empowers learners worldwide through mentor-led virtual internships, real projects, and industry-ready skill development.",
    "2": "Decode Labs offers virtual internships in various domains, including AI, Data Science, Web Development, and Web Development, providing hands-on experience and mentorship.",
    "3": "You can contact Decode Labs through their official website: https://www.decodelabs.tech/index.html or email hr@decodelabs.tech.",
    "4": "Students, recent graduates, and early-career professionals can apply. Most tracks are beginner-friendly and mentor-guided.",
    "5": "Yes. The programs are designed for global access with remote-friendly delivery. Mentoring sessions and support are coordinated to help learners across different time zones.",
    "6": "Current internship cohorts are structured as 4-week programs with guided weekly milestones. Most learners spend around 8–11 hours per week depending on the selected track.",
    "7": "Yes. Each track includes practical deliverables and at least 3 live project components, helping learners build a useful portfolio for applications and interviews.",
    "8": "Yes. Learners receive mentor checkpoints, project feedback, and guidance on implementation quality, problem-solving, and presentation of outcomes.",
    "9": "Yes. Learners who complete the required milestones and project submissions receive a completion certificate. Verification support is also available through the website.",
    "10": "Yes. You can use the Course Selector and advisor support to pick the best track based on your goals, current skills, and target role.",
    "11": "You can apply for internships through the official website. Navigate to the Internships section and follow the application instructions.",
    "12": "No. There are no fees associated with the internship program. It is completely free of charge."
}


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "message": "Decode Labs chatbot backend is running.",
        "menu": menu
    }


@app.get("/menu")
def get_menu():
    return {
        "menu": menu
    }


@app.post("/chatbot")
def chatbot(request: ChatRequest):
    user_message = request.message.strip()

    # If user asks for menu
    if user_message.lower() in ["menu", "help", "options"]:
        return {
            "reply": menu
        }

    # If user selected a valid menu option
    if user_message in responses:
        return {
            "reply": responses[user_message],
            "menu_hint": "Type 'menu' to see the options again."
        }

    # Invalid input
    return {
        "reply": "Invalid option. Please choose a number between 1 and 12, or type 'menu' to see the options again.",
        "menu": menu
    }