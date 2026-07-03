# Rule-Based AI Chatbot

class Rubai:
    def __init__(self, KB):
        self.kb = KB

    def clean_input(self, user_input):
        return user_input.strip().lower()

    def respond(self, user_input):
        user_input = self.clean_input(user_input)
        reply = self.kb.get(user_input, "I'm sorry, I don't understand. Can you please help grow my knowledge by providing more information?")
        return reply
    
if __name__ == "__main__":
    
    KB = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! What can I do for you?",
        "how are you": "I'm running! How about you?",
        "what is your name": "I am a Rubai, a rule-based AI chatbot. What's your name?",
        "bye": "Goodbye! Have a great day!",
        "thank you": "You're welcome! If you have any other questions, feel free to ask.",
        "please help": "Of course! I'm here to help. What do you need assistance with?"
    }
    
    chatbot = Rubai(KB)
    print("Welcome to Rubai! Type 'bye' to exit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "bye":
            print("Rubai: Goodbye! Have a great day!")
            break
        response = chatbot.respond(user_input)
        print(f"Rubai: {response}")