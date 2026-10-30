import os
import re
import json
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

    # Native Python TikTok Extractor (Works reliably on Render & Local)
    video_url = None
    title = "TikTok Video"
    author = "TikTok Creator"
    thumbnail = ""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text

        # Parse SIGI_STATE JSON embedded in TikTok page
        sigi_match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html)
        if sigi_match:
            try:
                sigi_data = json.loads(sigi_match.group(1))
                item_module = sigi_data.get('ItemModule', {})
                for k, v in item_module.items():
                    title = v.get('desc', title)
                    author = v.get('author', author)
                    thumbnail = v.get('video', {}).get('cover', thumbnail)
                    play_addr = v.get('video', {}).get('playAddr') or v.get('video', {}).get('downloadAddr')
                    if play_addr:
                        video_url = play_addr
                        break
            except Exception as e:
                print(f"SIGI parse error: {e}")

    except Exception as e:
        print(f"Native extraction error: {e}")

    # Fallback to TikWM API if native extraction didn't catch the stream
    if not video_url:
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}&hd=1"
            api_resp = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://www.tikwm.com/'}, timeout=8)
            if api_resp.status_code == 200:
                api_json = api_resp.json()
                if api_json.get('code') == 0:
                    v_data = api_json['data']
                    video_url = v_data.get('hdplay') or v_data.get('play')
                    title = v_data.get('title', title)
                    author = v_data.get('author', {}).get('nickname', author)
                    thumbnail = v_data.get('cover', thumbnail)
        except Exception as e:
            print(f"TikWM fallback error: {e}")

    if not video_url:
        return jsonify({'error': 'Could not extract video stream. Please ensure the TikTok link is public and correct.'}), 400

    return jsonify({
        'title': title,
        'uploader': author,
        'thumbnail': thumbnail or 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80',
        'duration': '00:30',
        'platform': 'tiktok',
        'formats': [
            {
                'quality': 'Original HD',
                'label': '⭐ Original HD (Max Quality / No Watermark)',
                'url': video_url
            }
        ]
    })

@app.route('/api/download', methods=['GET'])
def download_video():
    download_url = request.args.get('url')
    if not download_url:
        return "Missing download URL", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
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
