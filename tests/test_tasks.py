def test_create_task(client, auth_headers):
    res = client.post("/tasks", json={
        "title": "Learn Pytest",
        "completed": False
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Learn Pytest"
    assert data["completed"] is False
    assert "id" in data

def test_create_task_whitespace_only_title_fails(client, auth_headers):
    res = client.post("/tasks", json={
        "title": "     ",
        "completed": False
    }, headers=auth_headers)
    assert res.status_code == 422
    assert any("whitespace" in err["message"].lower() for err in res.json()["errors"])

def test_get_tasks_filtering_and_search(client, auth_headers):
    client.post("/tasks", json={"title": "Buy groceries", "completed": False}, headers=auth_headers)
    client.post("/tasks", json={"title": "Buy milk", "completed": True}, headers=auth_headers)
    client.post("/tasks", json={"title": "Read book", "completed": True}, headers=auth_headers)

    # Filter completed=True
    res = client.get("/tasks?completed=true", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    for t in res.json():
        assert t["completed"] is True

    # Search for "Buy"
    res = client.get("/tasks?search=buy", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    for t in res.json():
        assert "buy" in t["title"].lower()

def test_pagination(client, auth_headers):
    # Create 5 tasks
    for i in range(1, 6):
        client.post("/tasks", json={"title": f"Task {i}", "completed": False}, headers=auth_headers)

    # Get first 2 tasks
    res = client.get("/tasks?skip=0&limit=2", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    assert res.json()[0]["title"] == "Task 1"
    assert res.json()[1]["title"] == "Task 2"

    # Get next 2 tasks
    res = client.get("/tasks?skip=2&limit=2", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2
    assert res.json()[0]["title"] == "Task 3"
    assert res.json()[1]["title"] == "Task 4"

def test_update_task_put(client, auth_headers):
    task = client.post("/tasks", json={"title": "Original Title", "completed": False}, headers=auth_headers).json()
    task_id = task["id"]

    res = client.put(f"/tasks/{task_id}", json={
        "title": "Completely Replaced Title",
        "completed": True
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Completely Replaced Title"
    assert res.json()["completed"] is True

def test_update_task_patch(client, auth_headers):
    task = client.post("/tasks", json={"title": "Initial", "completed": False}, headers=auth_headers).json()
    task_id = task["id"]

    # Only update completed
    res = client.patch(f"/tasks/{task_id}", json={"completed": True}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["completed"] is True
    assert res.json()["title"] == "Initial"

def test_patch_empty_body_rejected(client, auth_headers):
    task = client.post("/tasks", json={"title": "Task", "completed": False}, headers=auth_headers).json()
    task_id = task["id"]

    res = client.patch(f"/tasks/{task_id}", json={}, headers=auth_headers)
    assert res.status_code == 400
    assert res.json()["detail"] == "No fields provided to update"

def test_delete_task(client, auth_headers):
    task = client.post("/tasks", json={"title": "To be deleted", "completed": False}, headers=auth_headers).json()
    task_id = task["id"]

    res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200

    # Ensure it's gone
    get_res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 404

def test_user_isolation(client, auth_headers, second_user_headers):
    # User 1 creates task
    task = client.post("/tasks", json={"title": "User 1 Secret", "completed": False}, headers=auth_headers).json()
    task_id = task["id"]

    # User 2 tries to read User 1's task
    get_res = client.get(f"/tasks/{task_id}", headers=second_user_headers)
    assert get_res.status_code == 404

    # User 2 tries to modify User 1's task
    put_res = client.put(f"/tasks/{task_id}", json={"title": "Hacked", "completed": True}, headers=second_user_headers)
    assert put_res.status_code == 404

    # User 2 tries to delete User 1's task
    del_res = client.delete(f"/tasks/{task_id}", headers=second_user_headers)
    assert del_res.status_code == 404

    # User 1 can still access and delete their own task
    assert client.get(f"/tasks/{task_id}", headers=auth_headers).status_code == 200

def test_invalid_task_id_fails_validation(client, auth_headers):
    # Non-positive ID
    res = client.get("/tasks/0", headers=auth_headers)
    assert res.status_code == 422

    res = client.get("/tasks/-1", headers=auth_headers)
    assert res.status_code == 422

    # String instead of int
    res = client.get("/tasks/abc", headers=auth_headers)
    assert res.status_code == 422
