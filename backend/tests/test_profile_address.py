import pytest
import datetime
from bson import ObjectId
from backend.app import create_app
from backend.app.utils.token_helper import generate_access_token

@pytest.fixture
def app():
    # Force mock database configuration
    app = create_app({"MOCK_DB": True})
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    from backend.app import db
    user_id = ObjectId()
    user_data = {
        "_id": user_id,
        "name": "Test User",
        "email": "test@galxy.com",
        "phone": "9876543210",
        "password_hash": "hashed_pw_placeholder",
        "addresses": [],
        "auth_provider": "email",
        "is_verified": False,
        "is_active": True,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc)
    }
    db.users.insert_one(user_data)
    yield user_data
    db.users.delete_many({})
    db.orders.delete_many({})

def test_get_profile_requires_auth(client):
    response = client.get('/api/user/profile')
    assert response.status_code == 401
    assert response.json['success'] is False

def test_get_profile_success(client, test_user):
    token = generate_access_token(test_user['_id'])
    response = client.get('/api/user/profile', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data']['email'] == "test@galxy.com"
    assert "password_hash" not in response.json['data']

def test_update_profile_success(client, test_user):
    token = generate_access_token(test_user['_id'])
    response = client.put('/api/user/profile', 
                          headers={"Authorization": f"Bearer {token}"},
                          json={"name": "Updated Name", "phone": "9887654321"})
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['data']['name'] == "Updated Name"
    assert response.json['data']['phone'] == "9887654321"

def test_update_profile_rejects_email(client, test_user):
    token = generate_access_token(test_user['_id'])
    response = client.put('/api/user/profile', 
                          headers={"Authorization": f"Bearer {token}"},
                          json={"email": "newemail@galxy.com"})
    assert response.status_code == 400
    assert response.json['success'] is False
    assert "email" in response.json['errors']

def test_address_invariants(client, test_user):
    token = generate_access_token(test_user['_id'])
    
    # 1. Add first address (should be default automatically)
    address_1 = {
        "label": "Home",
        "line1": "123 Main St",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "pincode": "600001",
        "is_default": False
    }
    res = client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json=address_1)
    assert res.status_code == 201
    assert res.json['success'] is True
    assert res.json['data']['is_default'] is True
    addr1_id = res.json['data']['_id']
    
    # 2. Add second address (is_default = False)
    address_2 = {
        "label": "Work",
        "line1": "456 Office Rd",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560001",
        "is_default": False
    }
    res = client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json=address_2)
    assert res.status_code == 201
    assert res.json['data']['is_default'] is False
    addr2_id = res.json['data']['_id']

    # 3. Add third address (is_default = True) - should unset others
    address_3 = {
        "label": "Other",
        "line1": "789 Resort Ave",
        "city": "Ooty",
        "state": "Tamil Nadu",
        "pincode": "643001",
        "is_default": True
    }
    res = client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json=address_3)
    assert res.status_code == 201
    assert res.json['data']['is_default'] is True
    addr3_id = res.json['data']['_id']

    # Verify database state - only addr3 should be default
    from backend.app import db
    user = db.users.find_one({"_id": ObjectId(test_user['_id'])})
    for addr in user['addresses']:
        if str(addr['_id']) == addr3_id:
            assert addr['is_default'] is True
        else:
            assert addr['is_default'] is False

    # 4. Try to delete address 1 (should succeed, non-default)
    res = client.delete(f'/api/user/addresses/{addr1_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    # 5. Try to delete the only remaining addresses until 1 left
    # Currently address 2 (non-default) and address 3 (default) exist
    res = client.delete(f'/api/user/addresses/{addr2_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

    # Now only address 3 exists. Deleting it should fail due to minimum address count (1)
    res = client.delete(f'/api/user/addresses/{addr3_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "retain at least one address" in res.json['errors']['message']

def test_delete_default_address_changes_default(client, test_user):
    token = generate_access_token(test_user['_id'])
    
    # Add two addresses, second is default
    client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json={
        "label": "Home", "line1": "123 Main St", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600001", "is_default": False
    })
    res2 = client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json={
        "label": "Work", "line1": "456 Office Rd", "city": "Bangalore", "state": "Karnataka", "pincode": "560001", "is_default": True
    })
    
    from backend.app import db
    user = db.users.find_one({"_id": ObjectId(test_user['_id'])})
    addr1 = user['addresses'][0]
    addr2 = user['addresses'][1]
    assert addr1['is_default'] is False
    assert addr2['is_default'] is True
    
    # Delete default address (addr2). It should set addr1 as default
    res = client.delete(f'/api/user/addresses/{addr2["_id"]}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    
    user = db.users.find_one({"_id": ObjectId(test_user['_id'])})
    assert len(user['addresses']) == 1
    assert user['addresses'][0]['is_default'] is True

def test_delete_default_address_blocked_by_pending_order(client, test_user):
    token = generate_access_token(test_user['_id'])
    from backend.app import db
    
    # Add two addresses, second is default
    client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json={
        "label": "Home", "line1": "123 Main St", "city": "Chennai", "state": "Tamil Nadu", "pincode": "600001", "is_default": False
    })
    res2 = client.post('/api/user/addresses', headers={"Authorization": f"Bearer {token}"}, json={
        "label": "Work", "line1": "456 Office Rd", "city": "Bangalore", "state": "Karnataka", "pincode": "560001", "is_default": True
    })
    addr2_id = res2.json['data']['_id']
    
    # Insert a pending order for this user
    db.orders.insert_one({
        "_id": ObjectId(),
        "user_id": str(test_user['_id']),
        "status": "confirmed", # pending status
        "items": []
    })
    
    # Attempt to delete the default address
    res = client.delete(f'/api/user/addresses/{addr2_id}', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "pending order" in res.json['errors']['message']
