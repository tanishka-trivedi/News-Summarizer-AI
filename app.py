"""
News Summarizer - Flask Backend
---------------------------------
Serves the frontend and exposes a small JSON API that wraps the NLP
logic in summarizer.py.

Endpoints:
    GET  /                  -> frontend (templates/index.html)
    POST /api/summarize     -> { text | url, num_sentences, mode } -> { summary }
"""

from flask import Flask, render_template, request, jsonify

import summarizer

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json(silent=True) or {}

    raw_text = (data.get("text") or "").strip()
    url = (data.get("url") or "").strip()
    mode = (data.get("mode") or "extractive").strip().lower()

    try:
        num_sentences = int(data.get("num_sentences", 3))
    except (TypeError, ValueError):
        num_sentences = 3
    num_sentences = max(1, min(num_sentences, 10))

    # Step 1: figure out the source text
    if url:
        try:
            raw_text = summarizer.get_article_text(url)
        except Exception as exc:  # noqa: BLE001 - surface a clean error to the UI
            return jsonify({"error": f"Could not fetch article from URL: {exc}"}), 400

    if not raw_text:
        return jsonify({"error": "Please provide article text or a URL."}), 400

    # Step 2: run the requested summarizer
    try:
        if mode == "abstractive":
            summary = summarizer.summarize_abstractive(raw_text)
        else:
            summary = summarizer.summarize_extractive(raw_text, num=num_sentences)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Summarization failed: {exc}"}), 500

    return jsonify({
        "summary": summary,
        "source_word_count": len(raw_text.split()),
        "summary_word_count": len(summary.split()),
        "mode": mode,
    })


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
