from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, json, asyncio

from app.orchestrator import Orchestrator
from app.image_analyzer import analyze_image

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orch = Orchestrator()

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            raw = await ws.receive_text()

            try:
                data = json.loads(raw)
            except:
                await ws.send_text(json.dumps({"type": "error", "msg": "Invalid JSON"}))
                continue

            if data.get("type") != "msg":
                await ws.send_text(json.dumps({"type": "error", "msg": "Unknown type"}))
                continue

            user_id = data.get("user_id", "user")
            message = data.get("message", "")
            persona = data.get("persona", "default")
            chat_id = data.get("chat_id")

            await ws.send_text(json.dumps({"type": "typing"}))

            try:
                reply = await orch.handle_message(
                    user_id=user_id,
                    message=message,
                    persona=persona,
                    chat_id=chat_id
                )

                await ws.send_text(json.dumps({
                    "type": "msg",
                    "text": reply
                }))

            except Exception as e:
                await ws.send_text(json.dumps({
                    "type": "error",
                    "msg": str(e)
                }))

    except WebSocketDisconnect:
        print("Client disconnected")
        return








