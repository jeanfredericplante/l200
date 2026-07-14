def test_get_state_endpoint(client):
    """Test fetching the student state via API."""
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "default_student"
    assert data["overall_progress_percent"] == 0.0

def test_update_module_endpoint(client):
    """Test manual completion updates via API."""
    # Complete module
    response = client.post("/api/state/update_module", json={"module_id": "s1_m1", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["modules"]["s1_m1"]["completed"] is True
    assert data["overall_progress_percent"] == 12.3

    # Reset module
    response = client.post("/api/state/update_module", json={"module_id": "s1_m1", "completed": False})
    assert response.status_code == 200
    data = response.json()
    assert data["modules"]["s1_m1"]["completed"] is False
    assert data["overall_progress_percent"] == 0.0

def test_update_module_endpoint_invalid_id(client):
    """Test update module endpoint returns 400 for bad module id."""
    response = client.post("/api/state/update_module", json={"module_id": "invalid_id", "completed": True})
    assert response.status_code == 400
    assert "Invalid module ID." in response.json()["detail"]

def test_quiz_submit_endpoint(client):
    """Test submitting quiz answers via API."""
    # s1_m1 correct answer is "B"
    response = client.post("/api/quiz/submit", json={"module_id": "s1_m1", "answer": "B"})
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is True
    assert data["correct_answer"] == "B"
    assert data["state"]["modules"]["s1_m1"]["completed"] is True
    assert data["state"]["overall_progress_percent"] == 12.3

    # Submit wrong answer "A"
    response = client.post("/api/quiz/submit", json={"module_id": "s1_m1", "answer": "A"})
    assert response.status_code == 200
    data = response.json()
    assert data["correct"] is False
    assert data["correct_answer"] == "B"

def test_quiz_submit_endpoint_invalid_id(client):
    """Test quiz submit endpoint returns 400 for bad module id."""
    response = client.post("/api/quiz/submit", json={"module_id": "invalid_id", "answer": "B"})
    assert response.status_code == 400
    assert "Invalid module ID." in response.json()["detail"]

def test_chat_endpoint_empty_prompt(client):
    """Test chat endpoint returns 400 for empty or whitespace prompts."""
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400
    assert "Prompt is empty." in response.json()["detail"]

def test_chat_endpoint_local_routing(client):
    """Test chat endpoint triggers rule-based / intelligent offline routing."""
    response = client.post("/api/chat", json={"message": "Tell me about s1_m1"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Teaching Agent" in data["response"]
    assert "s1_m1" in data["response"].lower() or "antigravity" in data["response"].lower()
