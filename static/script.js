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

    // Form submit / fetch video info from backend
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
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch TikTok information.');
            }

            displayVideoData(data);
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
        videoThumbnail.src = data.thumbnail || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80';
        videoDuration.textContent = data.duration || '00:30';

        formatButtons.innerHTML = '';

        if (data.formats && data.formats.length > 0) {
            data.formats.forEach(format => {
                const btn = document.createElement('a');
                btn.href = `/api/download?url=${encodeURIComponent(format.url)}`;
                btn.target = '_blank';
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
