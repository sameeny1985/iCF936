"""
Optional Flask wrapper for deploying the FI9 demo on Render (Web Service).
The pure static index.html is preferred for simplicity, but this allows
server-side Python verification if desired.
"""

from flask import Flask, render_template, request, jsonify
from fi9 import FI9

app = Flask(__name__)
encoder = FI9()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/encode", methods=["POST"])
def api_encode():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    states = encoder.encode(text)
    return jsonify({
        "states": states,
        "length": len(states),
        "ascii_preview": encoder.render_token_ascii(states[:16], cols=8)
    })


@app.route("/api/decode", methods=["POST"])
def api_decode():
    data = request.get_json(force=True) or {}
    states = data.get("states", [])
    try:
        text = encoder.decode_str(states)
        return jsonify({"text": text, "ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/matrix/<int:state>")
def api_matrix(state):
    if not 0 <= state <= 511:
        return jsonify({"error": "state out of range"}), 400
    return jsonify({
        "state": state,
        "matrix": encoder.matrix(state),
        "bits": encoder.state_to_bits(state),
        "region": "I" if state <= 255 else "II"
    })


@app.route("/api/hash", methods=["POST"])
def api_hash():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    states = encoder.graphical_hash(text)
    return jsonify({"states": states, "algorithm": "sha256"})


@app.route("/api/native_hash", methods=["POST"])
def api_native_hash():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    out_len = int(data.get("out_len", 32))
    rounds = int(data.get("rounds", 16))
    states = encoder.native_fi_hash(text, out_len=out_len, rounds=rounds)
    return jsonify({
        "states": states,
        "algorithm": "native_fi_hash",
        "out_len": out_len,
        "rounds": rounds,
        "note": "Research prototype – not cryptographically proven (paper §7.1)"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
