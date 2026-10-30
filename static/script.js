document.addEventListener('DOMContentLoaded', () => {
    const downloadForm = document.getElementById('downloadForm');
    const videoUrlInput = document.getElementById('videoUrl');
    const pasteBtn = document.getElementById('pasteBtn');
    const fetchBtn = document.getElementById('fetchBtn');
    const btnText = document.getElementById('btnText');
    const btnIcon = document.getElementById('btnIcon');
    const errorBox = document.getElementById('errorBox');
    const errorMessage = document.getElementById('errorMessage');
    const resultCard = document.getElementById('resultCard');
    const videoThumbnail = document.getElementById('videoThumbnail');
    const videoDuration = document.getElementById('videoDuration');
    const videoTitle = document.getElementById('videoTitle');
    const videoAuthor = document.getElementById('videoAuthor');
    const formatButtons = document.getElementById('formatButtons');

    // Clipboard paste helper
    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                videoUrlInput.value = text;
                showError(false);
            }
        } catch (err) {
            console.error('Failed to read clipboard contents: ', err);
            showError(true, 'Clipboard access denied. Please paste manually (Ctrl+V).');
        }
    });

    // Form submit / fetch video info directly client-side (bypasses cloud server IP blocks)
    downloadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = videoUrlInput.value.trim();

        if (!url) {
            showError(true, 'Please enter a valid TikTok URL.');
            return;
        }

        if (!url.includes('tiktok.com')) {
            showError(true, 'Please enter a valid TikTok video URL.');
            return;
        }

        showError(false);
        setLoadingState(true);

        try {
            // Client-side fetch directly from TikWM API using browser IP
            const apiUrl = `https://www.tikwm.com/api/?url=${encodeURIComponent(url)}&hd=1`;
            const response = await fetch(apiUrl);
            const resData = await response.json();

            if (resData.code !== 0 || !resData.data) {
                throw new Error('Could not fetch video. Please ensure the link is public and correct.');
            }

            const vidData = resData.data;
            const videoData = {
                title: vidData.title || 'TikTok Video',
                uploader: vidData.author?.nickname || 'TikTok Creator',
                thumbnail: vidData.cover || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80',
                duration: `00:${vidData.duration || 10}`,
                formats: [
                    {
                        quality: 'Original HD',
                        label: '⭐ Original HD (Max Quality / No Watermark)',
                        url: vidData.hdplay || vidData.play
                    }
                ]
            };

            if (vidData.music) {
                videoData.formats.push({
                    quality: 'MP3',
                    label: 'Original MP3 Audio',
                    url: vidData.music
                });
            }

            displayVideoData(videoData);
        } catch (err) {
            showError(true, err.message || 'An error occurred while fetching the TikTok video.');
        } finally {
            setLoadingState(false);
        }
    });

    function showError(show, msg = '') {
        if (show) {
            errorMessage.textContent = msg;
            errorBox.classList.remove('hidden');
            resultCard.classList.add('hidden');
        } else {
            errorBox.classList.add('hidden');
        }
    }

    function setLoadingState(loading) {
        if (loading) {
            btnText.textContent = 'Fetching...';
            btnIcon.className = 'fa-solid fa-spinner fa-spin';
            fetchBtn.disabled = true;
            fetchBtn.classList.add('opacity-75', 'cursor-not-allowed');
        } else {
            btnText.textContent = 'Fetch Video';
            btnIcon.className = 'fa-solid fa-arrow-down';
            fetchBtn.disabled = false;
            fetchBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    }

    function displayVideoData(data) {
        resultCard.classList.remove('hidden');

        videoTitle.textContent = data.title;
        videoAuthor.innerHTML = `<i class="fa-solid fa-user-circle"></i><span>${data.uploader}</span>`;
        videoThumbnail.src = data.thumbnail;
        videoDuration.textContent = data.duration;

        formatButtons.innerHTML = '';

        if (data.formats && data.formats.length > 0) {
            data.formats.forEach(format => {
                const btn = document.createElement('a');
                btn.href = format.url;
                btn.target = '_blank';
                btn.download = 'TikTok_Video.mp4';
                btn.className = 'p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group block';
                btn.innerHTML = `
                    <div class="font-bold text-sm text-white group-hover:text-primary flex items-center justify-between">
                        <span>${format.label}</span>
                        <i class="fa-solid fa-download text-xs text-primary"></i>
                    </div>
                    <div class="text-xs text-gray-400 mt-0.5">Click to download ${format.quality}</div>
                `;
                formatButtons.appendChild(btn);
            });
        } else {
            formatButtons.innerHTML = '<p class="text-sm text-gray-400 col-span-2">No formats found.</p>';
        }

        // Scroll smoothly to results
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
