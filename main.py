from flask import Flask
from models import create_table
from auth import register_auth
from routes import register_routes

app = Flask(__name__)
app.secret_key = "secret123"

create_table()

register_auth(app)
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)