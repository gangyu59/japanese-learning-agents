# 在项目中添加mock_api.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/chat/send")
async def mock_chat(request: dict):
    return {
        "success": True,
        "response": f"模拟回复: {request.get('message', '')}",
        "agent_name": request.get('agent_name', 'mock'),
        "learning_points": ["测试学习点"],
        "emotion": "😊"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)