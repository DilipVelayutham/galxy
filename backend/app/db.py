import os
import json
import uuid
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class Database:
    def __init__(self):
        self.fallback_file = os.path.join(os.path.dirname(__file__), "db_fallback.json")
        self.mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        self.client = None
        self.db = None
        self.is_fallback = False

        # Default admin settings
        self.default_settings = {
            "base_price": 99.0,
            "size_price_per_percent": 1.0,  # e.g., +$1 for each 1% above 100%
            "color_prices": {
                "#00f3ff": 0.0,   # Cyber Cyan (Free)
                "#ff0055": 15.0,  # Magic Magenta
                "#00ff66": 10.0,  # Krypton Green
                "#ff9900": 12.0,  # Helium Orange
                "#0066ff": 5.0,   # Electric Blue
            },
            "text_price_per_char": 2.0,
            "float_price_per_level": 5.0
        }

        # Initialize JSON file fallback database if it doesn't exist
        if not os.path.exists(self.fallback_file):
            self._save_fallback_data({"settings": self.default_settings, "configurations": []})

        # Try connecting to MongoDB
        try:
            # We set a low serverSelectionTimeoutMS so we don't block the backend startup for too long if MongoDB is down
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=1500)
            # Force a connection check
            self.client.admin.command('ping')
            self.db = self.client["galxy_antigravity"]
            print("Successfully connected to MongoDB.")
            
            # Ensure settings exist in DB, if not, write defaults
            if self.db["settings"].count_documents({}) == 0:
                self.db["settings"].insert_one(self.default_settings)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"MongoDB connection failed: {e}. Falling back to JSON file storage at {self.fallback_file}")
            self.is_fallback = True
        except Exception as e:
            print(f"An unexpected database initialization error occurred: {e}. Using JSON file storage.")
            self.is_fallback = True

    # Fallback helper methods
    def _read_fallback_data(self):
        try:
            with open(self.fallback_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading fallback JSON: {e}")
            return {"settings": self.default_settings, "configurations": []}

    def _save_fallback_data(self, data):
        try:
            with open(self.fallback_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error writing fallback JSON: {e}")

    # Core Database API
    def get_admin_settings(self):
        if self.is_fallback:
            data = self._read_fallback_data()
            # Ensure settings exist and return them
            return data.get("settings", self.default_settings)
        else:
            try:
                settings = self.db["settings"].find_one({}, {"_id": 0})
                return settings if settings else self.default_settings
            except Exception as e:
                print(f"MongoDB read settings error, using fallback: {e}")
                data = self._read_fallback_data()
                return data.get("settings", self.default_settings)

    def update_admin_settings(self, new_settings):
        # Filter settings to match structure
        sanitized_settings = {
            "base_price": float(new_settings.get("base_price", self.default_settings["base_price"])),
            "size_price_per_percent": float(new_settings.get("size_price_per_percent", self.default_settings["size_price_per_percent"])),
            "color_prices": new_settings.get("color_prices", self.default_settings["color_prices"]),
            "text_price_per_char": float(new_settings.get("text_price_per_char", self.default_settings["text_price_per_char"])),
            "float_price_per_level": float(new_settings.get("float_price_per_level", self.default_settings["float_price_per_level"]))
        }

        if self.is_fallback:
            data = self._read_fallback_data()
            data["settings"] = sanitized_settings
            self._save_fallback_data(data)
            return sanitized_settings
        else:
            try:
                self.db["settings"].replace_one({}, sanitized_settings, upsert=True)
                return sanitized_settings
            except Exception as e:
                print(f"MongoDB write settings error, updating fallback instead: {e}")
                data = self._read_fallback_data()
                data["settings"] = sanitized_settings
                self._save_fallback_data(data)
                return sanitized_settings

    def save_configuration(self, config_data):
        # Generate an ID if not present
        if "id" not in config_data:
            config_data["id"] = str(uuid.uuid4())
        
        # Ensure prices are computed on save just in case
        config_data["price"] = float(config_data.get("price", 0.0))

        if self.is_fallback:
            data = self._read_fallback_data()
            # If configuration exists, update it, else append it
            configs = data.get("configurations", [])
            existing_idx = next((i for i, c in enumerate(configs) if c.get("id") == config_data["id"]), -1)
            if existing_idx != -1:
                configs[existing_idx] = config_data
            else:
                configs.append(config_data)
            data["configurations"] = configs
            self._save_fallback_data(data)
            return config_data
        else:
            try:
                # Save to MongoDB
                # Remove MongoDB _id if present to avoid PyMongo write errors, we use our own uuid
                mongo_config = dict(config_data)
                if "_id" in mongo_config:
                    del mongo_config["_id"]
                self.db["configurations"].replace_one({"id": config_data["id"]}, mongo_config, upsert=True)
                return config_data
            except Exception as e:
                print(f"MongoDB write config error, saving to fallback instead: {e}")
                data = self._read_fallback_data()
                configs = data.get("configurations", [])
                configs.append(config_data)
                data["configurations"] = configs
                self._save_fallback_data(data)
                return config_data

    def get_configurations(self):
        if self.is_fallback:
            data = self._read_fallback_data()
            return data.get("configurations", [])
        else:
            try:
                # Return in reverse chronological order
                configs = list(self.db["configurations"].find({}, {"_id": 0}))
                return configs[::-1] if configs else []
            except Exception as e:
                print(f"MongoDB read configs error, reading fallback: {e}")
                data = self._read_fallback_data()
                return data.get("configurations", [])

    def delete_configuration(self, config_id):
        if self.is_fallback:
            data = self._read_fallback_data()
            configs = data.get("configurations", [])
            filtered_configs = [c for c in configs if c.get("id") != config_id]
            data["configurations"] = filtered_configs
            self._save_fallback_data(data)
            return True
        else:
            try:
                self.db["configurations"].delete_one({"id": config_id})
                return True
            except Exception as e:
                print(f"MongoDB delete config error, deleting in fallback: {e}")
                data = self._read_fallback_data()
                configs = data.get("configurations", [])
                filtered_configs = [c for c in configs if c.get("id") != config_id]
                data["configurations"] = filtered_configs
                self._save_fallback_data(data)
                return True

db = Database()
