from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

resp = client.post('/register', json={'email': 'test-debug@example.com', 'password': 'SuperSecret123'})
print('status', resp.status_code)
print(resp.text)
