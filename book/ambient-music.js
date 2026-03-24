/**
 * Background Music Player for The Oxytocin Story
 * Plays a soothing ambient MP3 on loop with volume control
 */
(function() {
  var STORAGE_KEY = 'oxytocin-book-music';
  var audio = null;
  var isPlaying = false;

  // Resolve path to bgm.mp3 (works from both /oxytocin.html and /book/*.html)
  function getBgmPath() {
    var path = window.location.pathname;
    if (path.indexOf('/book/') !== -1) {
      return 'bgm.mp3';
    }
    return 'book/bgm.mp3';
  }

  function initAudio() {
    if (audio) return;
    audio = new Audio(getBgmPath());
    audio.loop = true;
    audio.volume = 0;
    audio.preload = 'auto';
  }

  function fadeIn(targetVol, duration) {
    var step = targetVol / (duration / 50);
    var vol = 0;
    var timer = setInterval(function() {
      vol += step;
      if (vol >= targetVol) {
        vol = targetVol;
        clearInterval(timer);
      }
      if (audio) audio.volume = vol;
    }, 50);
  }

  function fadeOut(duration, callback) {
    if (!audio) return;
    var vol = audio.volume;
    var step = vol / (duration / 50);
    var timer = setInterval(function() {
      vol -= step;
      if (vol <= 0) {
        vol = 0;
        clearInterval(timer);
        if (callback) callback();
      }
      if (audio) audio.volume = vol;
    }, 50);
  }

  function startMusic() {
    if (isPlaying) return;
    initAudio();
    isPlaying = true;
    updateButton('playing');
    audio.play().then(function() {
      fadeIn(0.4, 2000);
    }).catch(function(e) {
      // Autoplay blocked — will retry on next click
      isPlaying = false;
      updateButton('stopped');
    });
    localStorage.setItem(STORAGE_KEY, 'on');
  }

  function stopMusic() {
    if (!isPlaying) return;
    isPlaying = false;
    fadeOut(1500, function() {
      if (audio) audio.pause();
    });
    localStorage.setItem(STORAGE_KEY, 'off');
    updateButton('stopped');
  }

  function toggleMusic() {
    if (isPlaying) stopMusic(); else startMusic();
  }

  function updateButton(state) {
    var btn = document.getElementById('music-toggle');
    if (!btn) return;
    var icon = btn.querySelector('.music-icon');
    var label = btn.querySelector('.music-label');
    btn.classList.remove('active');

    if (state === 'playing') {
      btn.classList.add('active');
      icon.innerHTML = '\u266B';
      label.textContent = 'Playing';
      btn.title = 'Pause music';
    } else {
      icon.innerHTML = '\u266A';
      label.textContent = 'Music';
      btn.title = 'Play soothing background music';
    }
  }

  function createUI() {
    var btn = document.createElement('button');
    btn.id = 'music-toggle';
    btn.className = 'music-btn';
    btn.innerHTML = '<span class="music-icon">\u266A</span><span class="music-label">Music</span>';
    btn.addEventListener('click', toggleMusic);
    document.body.appendChild(btn);

    var s = document.createElement('style');
    s.textContent =
      '.music-btn{position:fixed;bottom:28px;right:28px;z-index:999;' +
      'display:flex;align-items:center;gap:8px;' +
      'padding:12px 22px;border:none;border-radius:50px;cursor:pointer;' +
      'background:rgba(44,44,44,.88);color:#fff;' +
      'font-family:"Source Sans 3",Georgia,sans-serif;font-size:15px;font-weight:600;' +
      'letter-spacing:.5px;box-shadow:0 4px 24px rgba(0,0,0,.2);' +
      'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);' +
      'transition:all .3s ease}' +
      '.music-btn:hover{background:rgba(139,58,74,.95);box-shadow:0 6px 32px rgba(139,58,74,.4);transform:translateY(-2px)}' +
      '.music-btn.active{background:linear-gradient(135deg,#8B3A4A,#D4726A);box-shadow:0 4px 28px rgba(212,114,106,.4)}' +
      '.music-btn.active .music-icon{animation:mp 2s ease-in-out infinite}' +
      '.music-icon{font-size:20px}' +
      '@keyframes mp{0%,100%{transform:scale(1)}50%{transform:scale(1.2)}}' +
      '@media(max-width:480px){.music-btn{bottom:16px;right:16px;padding:10px 16px}.music-label{display:none}}';
    document.head.appendChild(s);

    // Auto-resume if user had music on
    if (localStorage.getItem(STORAGE_KEY) === 'on') {
      var resume = function() {
        startMusic();
        document.removeEventListener('click', resume);
        document.removeEventListener('scroll', resume);
      };
      document.addEventListener('click', resume, { once: true });
      document.addEventListener('scroll', resume, { once: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createUI);
  } else {
    createUI();
  }
})();
