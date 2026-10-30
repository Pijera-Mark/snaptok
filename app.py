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

    # Use official TikWM POST API (Extremely reliable for all TikTok links)
    try:
        api_url = "https://www.tikwm.com/api/"
        payload = {'url': url, 'hd': 1}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://www.tikwm.com',
            'Referer': 'https://www.tikwm.com/'
        }
        response = requests.post(api_url, data=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('code') == 0:
                vid_data = res_data['data']
                original_hd_url = vid_data.get('hdplay') or vid_data.get('play')
                music_url = vid_data.get('music')

                if not original_hd_url:
                    return jsonify({'error': 'Video stream not found in response.'}), 400

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
            else:
                err_msg = res_data.get('msg', 'Unknown extractor error')
                return jsonify({'error': f'Failed to extract video: {err_msg}. Please ensure the link is public.'}), 400
        else:
            return jsonify({'error': f'API connection error (HTTP {response.status_code}).'}), 400

    except Exception as e:
        return jsonify({'error': f'Extraction error: {str(e)}'}), 500

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
