import pytest
from app import app, db, User, Todo
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(username='admin', password=generate_password_hash('adminpass'), role='admin')
        db.session.add(admin)
        db.session.commit()

    yield client

def register(client, username, password):
    return client.post('/register', data={'username': username, 'password': password})

def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password})

def logout(client):
    return client.get('/logout')

def test_register_login_logout(client):
    rv = register(client, 'user1', 'pass1')
    assert rv.status_code == 200
    rv = login(client, 'user1', 'pass1')
    assert b'Login successful' in rv.data
    rv = logout(client)
    assert b'Logged out' in rv.data

def test_profile_update(client):
    register(client, 'user2', 'pass2')
    login(client, 'user2', 'pass2')

    rv = client.post('/profile', data={'username': 'admin'})
    assert rv.status_code == 400

    rv = client.post('/profile', data={'username': 'user2new', 'password': 'newpass'})
    assert b'Profile updated' in rv.data

def test_admin_access(client):
    login(client, 'admin', 'adminpass')
    rv = client.get('/admin/users')
    assert rv.status_code == 200
    users = rv.get_json()
    assert any(u['username'] == 'admin' for u in users)

    logout(client)
    register(client, 'user3', 'pass3')
    login(client, 'user3', 'pass3')
    rv = client.get('/admin/users')
    assert rv.status_code == 403

def test_todo_crud(client):
    register(client, 'user4', 'pass4')
    login(client, 'user4', 'pass4')

    rv = client.post('/todos', data={'title': 'Buy milk'})
    assert b'Todo created' in rv.data
    todo = rv.get_json()['todo']
    todo_id = todo['id']

    rv = client.get('/todos')
    todos = rv.get_json()
    assert any(t['title'] == 'Buy milk' for t in todos)

    rv = client.put(f'/todos/{todo_id}', data={'title': 'Buy almond milk'})
    assert b'Todo updated' in rv.data

    rv = client.delete(f'/todos/{todo_id}')
    assert b'Todo deleted' in rv.data

    rv = client.get('/todos')
    todos = rv.get_json()
    assert all(t['id'] != todo_id for t in todos)
