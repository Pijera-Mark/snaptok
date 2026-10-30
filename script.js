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
    const videoPlatformBadge = document.getElementById('videoPlatformBadge');
    const platformName = document.getElementById('platformName');
    const videoDuration = document.getElementById('videoDuration');
    const videoTitle = document.getElementById('videoTitle');
    const videoAuthor = document.getElementById('videoAuthor');
    const formatButtons = document.getElementById('formatButtons');
    const downloadProgressContainer = document.getElementById('downloadProgressContainer');
    const progressStatusText = document.getElementById('progressStatusText');
    const progressPercent = document.getElementById('progressPercent');
    const progressBar = document.getElementById('progressBar');

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

    // Form submit / fetch video info
    downloadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const url = videoUrlInput.value.trim();

        if (!url) {
            showError(true, 'Please enter a valid video URL.');
            return;
        }

        // Validate URL format for YouTube or TikTok
        const isYoutube = url.includes('youtube.com') || url.includes('youtu.be');
        const isTiktok = url.includes('tiktok.com');

        if (!isYoutube && !isTiktok) {
            showError(true, 'Please enter a valid YouTube or TikTok URL.');
            return;
        }

        showError(false);
        setLoadingState(true);

        // Simulate network request to fetch video metadata
        setTimeout(() => {
            setLoadingState(false);
            displayVideoData(url, isYoutube ? 'youtube' : 'tiktok');
        }, 1000);
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
            btnText.textContent = 'Analyzing...';
            btnIcon.className = 'fa-solid fa-spinner fa-spin';
            fetchBtn.disabled = true;
            fetchBtn.classList.add('opacity-75', 'cursor-not-allowed');
        } else {
            btnText.textContent = 'Download';
            btnIcon.className = 'fa-solid fa-arrow-down';
            fetchBtn.disabled = false;
            fetchBtn.classList.remove('opacity-75', 'cursor-not-allowed');
        }
    }

    function displayVideoData(url, platform) {
        resultCard.classList.remove('hidden');
        downloadProgressContainer.classList.add('hidden');

        if (platform === 'youtube') {
            platformName.textContent = 'YouTube';
            videoPlatformBadge.className = 'absolute top-2 left-2 px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider text-white bg-red-600/90 backdrop-blur-md flex items-center space-x-1.5';
            videoPlatformBadge.innerHTML = '<i class="fa-brands fa-youtube"></i><span>YouTube</span>';
            videoThumbnail.src = 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=600&auto=format&fit=crop&q=80';
            videoTitle.textContent = 'Amazing 4K Cinematic Nature Relaxing Music & Stunning Visuals (Official HD)';
            videoAuthor.innerHTML = '<i class="fa-solid fa-user-circle"></i><span>Nature Relax HD</span>';
            videoDuration.textContent = '12:34';

            formatButtons.innerHTML = `
                <button onclick="startDownload('MP4 (1080p - HD)', 'video')" class="p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group">
                    <div class="font-bold text-sm text-white group-hover:text-primary">MP4 1080p</div>
                    <div class="text-xs text-gray-400">High Quality (~45 MB)</div>
                </button>
                <button onclick="startDownload('MP4 (720p - SD)', 'video')" class="p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group">
                    <div class="font-bold text-sm text-white group-hover:text-primary">MP4 720p</div>
                    <div class="text-xs text-gray-400">Standard (~22 MB)</div>
                </button>
                <button onclick="startDownload('MP3 (Audio 320kbps)', 'audio')" class="p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group">
                    <div class="font-bold text-sm text-white group-hover:text-primary">MP3 Audio</div>
                    <div class="text-xs text-gray-400">High Audio (~8 MB)</div>
                </button>
            `;
        } else {
            platformName.textContent = 'TikTok';
            videoPlatformBadge.className = 'absolute top-2 left-2 px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider text-white bg-pink-600/90 backdrop-blur-md flex items-center space-x-1.5';
            videoPlatformBadge.innerHTML = '<i class="fa-brands fa-tiktok"></i><span>TikTok</span>';
            videoThumbnail.src = 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80';
            videoTitle.textContent = 'Viral Trending Dance Choreography 2025 #trending #viral #foryou';
            videoAuthor.innerHTML = '<i class="fa-solid fa-user-circle"></i><span>@dance_queen99</span>';
            videoDuration.textContent = '00:30';

            formatButtons.innerHTML = `
                <button onclick="startDownload('TikTok No Watermark (HD)', 'video')" class="p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group col-span-2">
                    <div class="font-bold text-sm text-white group-hover:text-primary">Download MP4 (No Watermark)</div>
                    <div class="text-xs text-gray-400">Original HD Quality (~12 MB)</div>
                </button>
                <button onclick="startDownload('TikTok MP3 Audio', 'audio')" class="p-3 bg-darkBg hover:bg-primary/20 border border-gray-700 hover:border-primary rounded-xl text-left transition group">
                    <div class="font-bold text-sm text-white group-hover:text-primary">MP3 Audio</div>
                    <div class="text-xs text-gray-400">Sound Track (~3 MB)</div>
                </button>
            `;
        }

        // Scroll smoothly to results
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});

// Global download simulation function
window.startDownload = function(formatName, type) {
    const downloadProgressContainer = document.getElementById('downloadProgressContainer');
    const progressStatusText = document.getElementById('progressStatusText');
    const progressPercent = document.getElementById('progressPercent');
    const progressBar = document.getElementById('progressBar');

    downloadProgressContainer.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressPercent.textContent = '0%';
    progressStatusText.textContent = `Preparing ${formatName}...`;

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 15) + 10;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            progressBar.style.width = '100%';
            progressPercent.textContent = '100%';
            progressStatusText.innerHTML = `<span class="text-emerald-400 font-semibold"><i class="fa-solid fa-circle-check mr-1.5"></i> Download Ready!</span> <a href="#" onclick="alert('Simulated file download started successfully!')" class="ml-3 underline text-primary font-bold">Click here to save file</a>`;
        } else {
            progressBar.style.width = `${progress}%`;
            progressPercent.textContent = `${progress}%`;
            if (progress > 50) {
                progressStatusText.textContent = `Processing and encoding ${formatName}...`;
            } else {
                progressStatusText.textContent = `Downloading from server...`;
            }
        }
    }, 250);
};
