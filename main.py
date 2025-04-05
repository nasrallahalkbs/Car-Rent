from app import app

if __name__ == "__main__":
    # This file is only used when debugging the application directly
    # For production, gunicorn will import the app directly
    app.run(host="0.0.0.0", port=5000, debug=True)
