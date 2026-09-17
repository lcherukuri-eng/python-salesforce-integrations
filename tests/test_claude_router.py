from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_claude_service
from app.security import verify_request

client = TestClient(app)

async def fake_claude(question):
    return "This is a mock response"

def test_ask_ai():

    app.dependency_overrides[
        verify_request
    ] = lambda: True

    app.dependency_overrides[
        get_claude_service
    ] = lambda: fake_claude

    response = client.get(
        "/claude/ask",
        params={"question": "What is AI?"}
    )

    assert response.status_code == 200

    assert response.json() == {
        "question": "What is AI?",
        "answer": "This is a mock response"
    }

    app.dependency_overrides.clear()