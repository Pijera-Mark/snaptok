import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, Response, stream_with_context
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    if 'tiktok.com' not in url.lower():
        return jsonify({'error': 'Please enter a valid TikTok URL.'}), 400

    # Expand short TikTok URLs (vm.tiktok.com, vt.tiktok.com)
    try:
        if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            r_redir = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}, allow_redirects=True, timeout=5)
            if r_redir.url:
                url = r_redir.url
    except Exception as e:
        print(f"URL expansion error: {e}")

    # Fallback 1: Cobalt API
    try:
        cobalt_url = "https://co.wuk.sh/api/json"
        payload = {"url": url, "vQuality": "max", "isAudioOnly": False}
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://co.wuk.sh",
            "Referer": "https://co.wuk.sh/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        res = requests.post(cobalt_url, json=payload, headers=headers, timeout=8)
        if res.status_code == 200:
            c_data = res.json()
            if c_data.get('status') in ['stream', 'redirect'] and c_data.get('url'):
                return jsonify({
                    'title': 'TikTok Video (HD No Watermark)',
                    'uploader': 'TikTok Creator',
                    'thumbnail': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80',
                    'duration': '00:30',
                    'platform': 'tiktok',
                    'formats': [{
                        'quality': 'Original HD',
                        'label': '⭐ Original HD (Max Quality / No Watermark)',
                        'url': c_data.get('url')
                    }]
                })
    except Exception as e:
        print(f"Cobalt error: {e}")

    # Fallback 2: TikWM API
    try:
        api_url = "https://www.tikwm.com/api/"
        payload = {'url': url, 'hd': 1}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Referer': 'https://www.tikwm.com/'
        }
        response = requests.post(api_url, data=payload, headers=headers, timeout=8)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0:
                vid_data = res_data['data']
                hd_url = vid_data.get('hdplay') or vid_data.get('play')
                if hd_url:
                    return jsonify({
                        'title': vid_data.get('title', 'TikTok Video'),
                        'uploader': vid_data.get('author', {}).get('nickname', 'TikTok Creator'),
                        'thumbnail': vid_data.get('cover', ''),
                        'duration': '00:30',
                        'platform': 'tiktok',
                        'formats': [{
                            'quality': 'Original HD',
                            'label': '⭐ Original HD (Max Quality / No Watermark)',
                            'url': hd_url
                        }]
                    })
    except Exception as e:
        print(f"TikWM error: {e}")

    # Fallback 3: yt-dlp Python Library
    try:
        ydl_opts = {'no_warnings': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            if video_url:
                return jsonify({
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'TikTok Creator'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': '00:30',
                    'platform': 'tiktok',
                    'formats': [{
                        'quality': 'Original HD',
                        'label': '⭐ Original HD (Max Quality / No Watermark)',
                        'url': video_url
                    }]
                })
    except Exception as e:
        print(f"yt-dlp error: {e}")

    return jsonify({'error': 'API connection error (HTTP 403). All extraction services are temporarily blocked or restricted for this link.'}), 400

@app.route('/api/download', methods=['GET'])
def download_video():
    download_url = request.args.get('url')
    if not download_url:
        return "Missing download URL", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
        r = requests.get(download_url, headers=headers, stream=True, timeout=30)

        if r.status_code != 200:
            return redirect(download_url)

        return Response(
            stream_with_context(r.iter_content(chunk_size=1024*1024)),
            content_type='video/mp4',
            headers={
                'Content-Disposition': 'attachment; filename="TikTok_Original_HD.mp4"'
            }
        )
    except Exception as e:
        return redirect(download_url)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
