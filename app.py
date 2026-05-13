import json
import os
import uuid
import subprocess
import time
from flask import Flask, request, session, render_template, Response, jsonify, send_from_directory

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

CLAUDE_EXEC = os.environ.get("CLAUDE_CODE_EXECPATH", "claude")

conversations = {}  # conv_id -> claude_session_id


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), "static"), filename)


@app.route("/")
def index():
    if "logged_in" not in session:
        return render_template("index.html", logged_in=False)
    return render_template("index.html", logged_in=True)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data.get("password", "") == "123456":
        session["logged_in"] = True
        session["conv_id"] = uuid.uuid4().hex
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "密码错误"}), 401


@app.route("/new-chat", methods=["POST"])
def new_chat():
    if "logged_in" not in session:
        return jsonify({"error": "未登录"}), 401
    conv_id = session.pop("conv_id", None)
    conversations.pop(conv_id, None)
    session["conv_id"] = uuid.uuid4().hex
    return jsonify({"success": True})


@app.route("/logout", methods=["POST"])
def logout():
    conv_id = session.pop("conv_id", None)
    conversations.pop(conv_id, None)
    session.clear()
    return jsonify({"success": True})


@app.route("/stream", methods=["POST"])
def stream():
    if "logged_in" not in session:
        return jsonify({"error": "未登录"}), 401

    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "消息为空"}), 400

    conv_id = session.get("conv_id")
    claude_session_id = conversations.get(conv_id)

    def generate():
        nonlocal claude_session_id

        cmd = [
            CLAUDE_EXEC,
            "--print", "--verbose",
            "--output-format", "stream-json",
            "--input-format", "stream-json",
            "--include-partial-messages",
            "--dangerously-skip-permissions",
            "--max-budget-usd", "5",
        ]
        if claude_session_id:
            cmd.extend(["--resume", claude_session_id])
        else:
            cmd.extend(["--session-id", str(uuid.uuid4())])

        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                bufsize=1,
                cwd=os.getcwd(),
                env=env,
            )

            # Send user message as stream-json
            user_json = json.dumps({"type": "user", "message": {"role": "user", "content": user_message}}, ensure_ascii=False)
            proc.stdin.write(user_json + "\n")
            proc.stdin.close()

            # Read stream-json output line by line, forward as SSE
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)

                    # Capture session ID from init event
                    if event.get("type") == "system" and event.get("subtype") == "init":
                        claude_session_id = event.get("session_id")
                        conversations[conv_id] = claude_session_id

                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

                except json.JSONDecodeError:
                    continue

            proc.wait()

            # Drain stderr
            stderr_output = proc.stderr.read()
            if stderr_output:
                yield f"data: {json.dumps({'type': 'stderr', 'text': stderr_output}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
