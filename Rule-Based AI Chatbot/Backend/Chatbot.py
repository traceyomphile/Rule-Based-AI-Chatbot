from fastapi import FastAPI

app = FastAPI()

@app.get("/chatbot")
async def chatbot():
    return {"message": "Hello! I am your chatbot. How can I assist you today?"}

