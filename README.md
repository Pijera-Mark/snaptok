# SnapTok - TikTok No-Watermark Video Downloader

A full-stack web application powered by **Flask** and **yt-dlp** specialized for downloading TikTok videos without watermarks and extracting MP3 audio.

## Project Structure

- `[run.bat](file:///C:/Users/admin/Desktop/tiktokdownloader/run.bat)`: One-click local startup script for Windows.
- `[app.py](file:///C:/Users/admin/Desktop/tiktokdownloader/app.py)`: Flask backend server using `yt-dlp`.
- `[requirements.txt](file:///C:/Users/admin/Desktop/tiktokdownloader/requirements.txt)`: Python dependencies (`flask`, `yt-dlp`, `gunicorn`).
- `[Procfile](file:///C:/Users/admin/Desktop/tiktokdownloader/Procfile)`: Deployment startup command (`web: gunicorn app:app`).
- `[templates/index.html](file:///C:/Users/admin/Desktop/tiktokdownloader/templates/index.html)`: TikTok frontend UI.
- `[static/script.js](file:///C:/Users/admin/Desktop/tiktokdownloader/static/script.js)`: Frontend interaction script.

## How to Run Locally

Double-click **[run.bat](file:///C:/Users/admin/Desktop/tiktokdownloader/run.bat)** to install dependencies, start the server, and open `http://127.0.0.1:5000` automatically!
