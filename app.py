from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os

# ---------------------- LOAD ENV ----------------------
load_dotenv()

app = Flask(__name__)

# ---------------------- DATABASE SETUP ----------------------
mongo_uri = os.getenv("MONGO_URI")

if not mongo_uri:
    raise ValueError("MONGO_URI not found in environment variables")

client = MongoClient(mongo_uri)
db = client["webhookdb"]
collection = db["events"]

# ---------------------- HOME ROUTE ----------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------------- WEBHOOK ROUTE ----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        event_type = request.headers.get("X-GitHub-Event")
        payload = request.get_json()

        if not payload:
            return jsonify({"error": "No payload received"}), 400

        data = None

        # ---------------- PUSH EVENT ----------------
        if event_type == "push":
            data = {
                "request_id": payload.get("after"),
                "author": payload.get("pusher", {}).get("name"),
                "action": "PUSH",
                "from_branch": None,
                "to_branch": payload.get("ref", "").split("/")[-1],
                "timestamp": datetime.utcnow()
            }

        # ---------------- PULL REQUEST EVENT ----------------
        elif event_type == "pull_request":
            pr = payload.get("pull_request", {})
            action = payload.get("action")

            if action == "opened":
                data = {
                    "request_id": str(pr.get("id")),
                    "author": pr.get("user", {}).get("login"),
                    "action": "PULL_REQUEST",
                    "from_branch": pr.get("head", {}).get("ref"),
                    "to_branch": pr.get("base", {}).get("ref"),
                    "timestamp": datetime.utcnow()
                }

            elif action == "closed" and pr.get("merged"):
                data = {
                    "request_id": str(pr.get("id")),
                    "author": pr.get("user", {}).get("login"),
                    "action": "MERGE",
                    "from_branch": pr.get("head", {}).get("ref"),
                    "to_branch": pr.get("base", {}).get("ref"),
                    "timestamp": datetime.utcnow()
                }

        # Insert into DB if valid event
        if data:
            collection.insert_one(data)
            return jsonify({"status": "Event stored successfully"}), 200

        return jsonify({"status": "Event ignored"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- EVENTS API ----------------------
@app.route("/events", methods=["GET"])
def get_events():
    try:
        events = list(
            collection.find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(20)
        )

        # Format timestamp for frontend
        for event in events:
            if isinstance(event.get("timestamp"), datetime):
                event["timestamp"] = event["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC")

        return jsonify(events), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)