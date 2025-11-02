from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "yt-dlp API is running 🚀"})

@app.route('/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400
    try:
        ydl_opts = {"quiet": True, "dump_single_json": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400
    try:
        temp_dir = tempfile.mkdtemp()
        outtmpl = os.path.join(temp_dir, "%(title)s.%(ext)s")
        ydl_opts = {"outtmpl": outtmpl, "quiet": True, "merge_output_format": "mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/transcript', methods=['POST'])
def get_transcript():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400
    try:
        ydl_opts = {"skip_download": True, "writesubtitles": True, "subtitleslangs": ["en"], "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get("subtitles") or info.get("automatic_captions")
            if not subs:
                return jsonify({"error": "No subtitles found"}), 404
            en_sub = subs.get("en", [])[0]
            return jsonify({"subtitle_url": en_sub["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
