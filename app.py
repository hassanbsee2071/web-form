
from config import Config
from app import app
if __name__ == "__main__":
    app.run(debug=Config.DEBUG)
    app.run(host="0.0.0.0")
