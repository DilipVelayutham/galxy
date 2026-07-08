import bcrypt
import jwt
import datetime
from bson import ObjectId
from app.config import Config
from app.db import db

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    @classmethod
    def generate_access_token(cls, user_id: str, email: str, role: str) -> str:
        payload = {
            "user_id": str(user_id),
            "email": email,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    @classmethod
    def generate_refresh_token(cls, user_id: str) -> str:
        payload = {
            "user_id": str(user_id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    @classmethod
    def signup(cls, name, email, phone, password):
        # Clean inputs
        email = email.lower().strip()
        
        # Check if email already exists in users or admin_users
        if db.users.find_one({"email": email}) or db.admin_users.find_one({"email": email}):
            return {"success": False, "message": "Email is already registered"}, 400
            
        password_hash = cls.hash_password(password)
        
        user_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "password_hash": password_hash,
            "addresses": [],
            "auth_provider": "email",
            "is_verified": False,
            "created_at": datetime.datetime.utcnow(),
            "last_login": None
        }
        
        result = db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return {"success": True, "message": "User registered successfully"}, 201

    @classmethod
    def login(cls, email, password):
        email = email.lower().strip()
        
        # Check admin_users first
        admin = db.admin_users.find_one({"email": email})
        if admin:
            if cls.verify_password(password, admin["password_hash"]):
                user_id = str(admin["_id"])
                role = admin.get("role", "super_admin")
                
                access_token = cls.generate_access_token(user_id, email, role)
                refresh_token = cls.generate_refresh_token(user_id)
                
                db.admin_users.update_one({"_id": admin["_id"]}, {"$set": {"last_login": datetime.datetime.utcnow()}})
                
                return {
                    "success": True,
                    "data": {
                        "user": {
                            "id": user_id,
                            "name": admin["name"],
                            "email": admin["email"],
                            "role": role
                        },
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    }
                }, 200
            else:
                return {"success": False, "message": "Invalid email or password"}, 401
                
        # Check standard users
        user = db.users.find_one({"email": email})
        if user:
            if cls.verify_password(password, user["password_hash"]):
                user_id = str(user["_id"])
                role = "customer"
                
                access_token = cls.generate_access_token(user_id, email, role)
                refresh_token = cls.generate_refresh_token(user_id)
                
                db.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.datetime.utcnow()}})
                
                return {
                    "success": True,
                    "data": {
                        "user": {
                            "id": user_id,
                            "name": user["name"],
                            "email": user["email"],
                            "role": role,
                            "phone": user.get("phone", "")
                        },
                        "access_token": access_token,
                        "refresh_token": refresh_token
                    }
                }, 200
            else:
                return {"success": False, "message": "Invalid email or password"}, 401
                
        return {"success": False, "message": "Invalid email or password"}, 401

    @classmethod
    def get_profile(cls, user_id, role):
        if role == "super_admin":
            user = db.admin_users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"success": False, "message": "Admin user not found"}, 404
            return {
                "success": True,
                "data": {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "role": "super_admin"
                }
            }, 200
        else:
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"success": False, "message": "User not found"}, 404
            return {
                "success": True,
                "data": {
                    "id": str(user["_id"]),
                    "name": user["name"],
                    "email": user["email"],
                    "phone": user.get("phone", ""),
                    "addresses": [{**addr, "id": str(addr.get("id"))} for addr in user.get("addresses", [])],
                    "role": "customer"
                }
            }, 200

    @classmethod
    def update_profile(cls, user_id, role, name, phone=None):
        update_data = {"name": name}
        if phone is not None:
            update_data["phone"] = phone
            
        if role == "super_admin":
            res = db.admin_users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        else:
            res = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
            
        if res.matched_count == 0:
            return {"success": False, "message": "User not found"}, 404
            
        return {"success": True, "message": "Profile updated successfully"}, 200

    @classmethod
    def add_address(cls, user_id, address_data):
        address_id = ObjectId()
        new_address = {
            "id": address_id,
            "label": address_data.get("label", "Home"),
            "line1": address_data.get("line1"),
            "line2": address_data.get("line2", ""),
            "city": address_data.get("city"),
            "state": address_data.get("state"),
            "pincode": address_data.get("pincode"),
            "is_default": address_data.get("is_default", False)
        }
        
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found"}, 404
            
        addresses = user.get("addresses", [])
        
        if new_address["is_default"]:
            # Set all others to false
            for addr in addresses:
                addr["is_default"] = False
                
        addresses.append(new_address)
        
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"addresses": addresses}})
        return {"success": True, "message": "Address added successfully", "data": {"id": str(address_id)}}, 201

    @classmethod
    def update_address(cls, user_id, address_id_str, address_data):
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found"}, 404
            
        addresses = user.get("addresses", [])
        target_found = False
        address_id = ObjectId(address_id_str)
        
        is_default_update = address_data.get("is_default", False)
        
        for addr in addresses:
            if addr.get("id") == address_id:
                addr["label"] = address_data.get("label", addr["label"])
                addr["line1"] = address_data.get("line1", addr["line1"])
                addr["line2"] = address_data.get("line2", addr.get("line2", ""))
                addr["city"] = address_data.get("city", addr["city"])
                addr["state"] = address_data.get("state", addr["state"])
                addr["pincode"] = address_data.get("pincode", addr["pincode"])
                addr["is_default"] = is_default_update
                target_found = True
            elif is_default_update:
                addr["is_default"] = False
                
        if not target_found:
            return {"success": False, "message": "Address not found"}, 404
            
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"addresses": addresses}})
        return {"success": True, "message": "Address updated successfully"}, 200

    @classmethod
    def delete_address(cls, user_id, address_id_str):
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {"success": False, "message": "User not found"}, 404
            
        addresses = user.get("addresses", [])
        address_id = ObjectId(address_id_str)
        
        new_addresses = [addr for addr in addresses if addr.get("id") != address_id]
        
        if len(new_addresses) == len(addresses):
            return {"success": False, "message": "Address not found"}, 404
            
        # If we deleted the default, set another one as default (first if available)
        was_deleted_default = any(addr.get("id") == address_id and addr.get("is_default") for addr in addresses)
        if was_deleted_default and new_addresses:
            new_addresses[0]["is_default"] = True
            
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"addresses": new_addresses}})
        return {"success": True, "message": "Address deleted successfully"}, 200
