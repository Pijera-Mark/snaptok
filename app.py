import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, Response, stream_with_context

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

    # Method 1: Cobalt API with proper Origin & Referer headers
    try:
        cobalt_url = "https://co.wuk.sh/api/json"
        payload = {
            "url": url,
            "vQuality": "max",
            "isAudioOnly": False
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://co.wuk.sh",
            "Referer": "https://co.wuk.sh/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        res = requests.post(cobalt_url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            c_data = res.json()
            if c_data.get('status') in ['stream', 'redirect'] and c_data.get('url'):
                stream_url = c_data.get('url')
                return jsonify({
                    'title': 'TikTok Video (HD No Watermark)',
                    'uploader': 'TikTok Creator',
                    'thumbnail': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80',
                    'duration': '00:30',
                    'platform': 'tiktok',
                    'formats': [
                        {
                            'quality': 'Original HD',
                            'label': '⭐ Original HD (Max Quality / No Watermark)',
                            'url': stream_url
                        }
                    ]
                })
    except Exception as e:
        print(f"Cobalt API error: {e}")

    # Method 2: TikWM API Fallback with proper headers
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.tikwm.com/'
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0:
                vid_data = res_data['data']
                original_hd_url = vid_data.get('hdplay') or vid_data.get('play')
                music_url = vid_data.get('music')

                if original_hd_url:
                    formats = [{
                        'quality': 'Original HD',
                        'label': '⭐ Original HD (Max Quality / No Watermark)',
                        'url': original_hd_url
                    }]
                    if music_url:
                        formats.append({
                            'quality': 'MP3',
                            'label': 'Original MP3 Audio',
                            'url': music_url
                        })

                    return jsonify({
                        'title': vid_data.get('title', 'TikTok Video'),
                        'uploader': vid_data.get('author', {}).get('nickname', 'TikTok Creator'),
                        'thumbnail': vid_data.get('cover', ''),
                        'duration': f"00:{vid_data.get('duration', 10):02d}",
                        'platform': 'tiktok',
                        'formats': formats
                    })
    except Exception as e:
        print(f"TikWM API error: {e}")

    return jsonify({'error': 'Could not fetch video. Please make sure the TikTok link is public and correct.'}), 400

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

        ext = 'mp3' if 'music' in download_url or 'audio' in download_url else 'mp4'

        return Response(
            stream_with_context(r.iter_content(chunk_size=1024*1024)),
            content_type=r.headers.get('content-type', 'video/mp4'),
            headers={
                'Content-Disposition': f'attachment; filename="TikTok_Video.{ext}"'
            }
        )
    except Exception as e:
        return redirect(download_url)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
