class CustomPyMongo:
    @property
    def db(self):
        from app.db import get_db
        return get_db()

    def init_app(self, app):
        pass

mongo = CustomPyMongo()
