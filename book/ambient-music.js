/**
 * Jazz Piano CCM - Real Piano Samples
 * Uses free piano soundfont samples for natural sound
 * Plays gentle jazz CCM worship progressions
 */
(function() {
  'use strict';

  var STORAGE_KEY = 'oxytocin-book-music';
  var SOUNDFONT_BASE = 'https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/acoustic_grand_piano-mp3/';
  var ctx, masterGain;
  var isPlaying = false;
  var loopTimer = null;
  var samples = {};
  var loaded = false;
  var loading = false;

  // Notes we need (covering 3 octaves for bass + chords + melody)
  var NOTE_NAMES = [
    // Bass (octave 2-3)
    'C2','D2','E2','F2','G2','A2','Bb2','B2',
    'C3','D3','Eb3','E3','F3','G3','A3','Bb3','B3',
    // Chords (octave 3-4)
    'C4','D4','Eb4','E4','F4','Gb4','G4','Ab4','A4','Bb4','B4',
    // Melody (octave 4-5)
    'C5','D5','Eb5','E5','F5','G5','A5','Bb5','B5','C6'
  ];

  // === CCM Jazz Progressions (note names) ===
  var PROGRESSIONS = [
    // I - V/B - vi7 - IVmaj7 (classic worship)
    [
      { bass: 'C2', chord: ['E3','G3','B3','D4'], mel: ['E5','G5','C6'] },
      { bass: 'B2', chord: ['D3','G3','B3','E4'], mel: ['D5','G5','B5'] },
      { bass: 'A2', chord: ['C3','E3','G3','B3'], mel: ['C5','E5','A5'] },
      { bass: 'F2', chord: ['A3','C4','E4','G4'], mel: ['A5','C6','E5'] },
    ],
    // ii7 - V9 - Imaj9 - vi7 (jazz standard)
    [
      { bass: 'D2', chord: ['F3','A3','C4','E4'], mel: ['F5','A5','C6'] },
      { bass: 'G2', chord: ['B3','D4','F4','A4'], mel: ['D5','F5','B5'] },
      { bass: 'C2', chord: ['E3','G3','B3','D4'], mel: ['E5','G5','D5'] },
      { bass: 'A2', chord: ['C3','E3','G3','B3'], mel: ['C5','E5','G5'] },
    ],
    // I - iii7 - vi - IV - V (emotional CCM)
    [
      { bass: 'C2', chord: ['E3','G3','B3','D4'], mel: ['G5','E5','C5'] },
      { bass: 'E2', chord: ['G3','B3','D4','E4'], mel: ['B5','G5','E5'] },
      { bass: 'A2', chord: ['C3','E3','A3','B3'], mel: ['A5','E5','C5'] },
      { bass: 'F2', chord: ['A3','C4','E4','G4'], mel: ['C6','A5','F5'] },
      { bass: 'G2', chord: ['B3','D4','G4','A4'], mel: ['D5','G5','B5'] },
    ],
    // vi - IV - I - V (10000 Reasons / worship feel)
    [
      { bass: 'A2', chord: ['C3','E3','A3','B3'], mel: ['E5','A5','C6'] },
      { bass: 'F2', chord: ['A3','C4','F4','G4'], mel: ['C5','F5','A5'] },
      { bass: 'C2', chord: ['E3','G3','C4','D4'], mel: ['G5','C6','E5'] },
      { bass: 'G2', chord: ['B3','D4','G4','A4'], mel: ['D5','G5','B5'] },
    ],
  ];

  // Load piano samples
  function loadSamples(callback) {
    if (loaded) { callback(); return; }
    if (loading) return;
    loading = true;

    var remaining = NOTE_NAMES.length;
    var loadCount = 0;

    NOTE_NAMES.forEach(function(note) {
      var url = SOUNDFONT_BASE + note + '.mp3';
      var req = new XMLHttpRequest();
      req.open('GET', url, true);
      req.responseType = 'arraybuffer';
      req.onload = function() {
        if (req.status === 200) {
          ctx.decodeAudioData(req.response, function(buffer) {
            samples[note] = buffer;
            loadCount++;
            remaining--;
            if (remaining <= 0) {
              loaded = true;
              loading = false;
              callback();
            }
          }, function() {
            remaining--;
            if (remaining <= 0) { loaded = true; loading = false; callback(); }
          });
        } else {
          remaining--;
          if (remaining <= 0) { loaded = true; loading = false; callback(); }
        }
      };
      req.onerror = function() {
        remaining--;
        if (remaining <= 0) { loaded = true; loading = false; callback(); }
      };
      req.send();
    });

    // Timeout safety
    setTimeout(function() {
      if (!loaded) { loaded = true; loading = false; callback(); }
    }, 15000);
  }

  // Play a single piano note using real sample
  function playNote(noteName, time, duration, velocity) {
    if (!ctx || !samples[noteName]) return;
    var source = ctx.createBufferSource();
    source.buffer = samples[noteName];

    var gain = ctx.createGain();
    var vel = velocity || 0.5;

    // Natural piano envelope
    gain.gain.setValueAtTime(0, time);
    gain.gain.linearRampToValueAtTime(vel, time + 0.01);
    gain.gain.setTargetAtTime(vel * 0.7, time + 0.1, 0.3);
    gain.gain.setTargetAtTime(vel * 0.3, time + duration * 0.6, duration * 0.2);
    gain.gain.linearRampToValueAtTime(0, time + duration);

    source.connect(gain);
    gain.connect(masterGain);

    source.start(time);
    source.stop(time + duration + 0.5);
  }

  // Play a full musical phrase
  function playPhrase() {
    if (!ctx || !isPlaying) return;

    var prog = PROGRESSIONS[Math.floor(Math.random() * PROGRESSIONS.length)];
    var now = ctx.currentTime + 0.1;
    var beatLen = 0.5 + Math.random() * 0.08; // ~100-115 BPM
    var chordLen = beatLen * 4;
    var totalLen = 0;

    prog.forEach(function(ch, ci) {
      var t = now + ci * chordLen;

      // Bass note (beat 1, gentle)
      playNote(ch.bass, t, chordLen * 0.9, 0.35);

      // Chord voicing - slight arpeggiation for jazz feel
      ch.chord.forEach(function(note, ni) {
        var arpDelay = ni * 0.04; // subtle arpeggio
        playNote(note, t + arpDelay, chordLen * 0.8, 0.25);
      });

      // Jazz comp: re-hit chord on "and of 2"
      if (Math.random() > 0.25) {
        var rehit = t + beatLen * 1.5;
        ch.chord.slice(1, 3).forEach(function(note, ni) {
          playNote(note, rehit + ni * 0.03, beatLen * 1.2, 0.18);
        });
      }

      // Ghost chord on beat 4 "and" (very soft)
      if (Math.random() > 0.55) {
        var ghost = t + beatLen * 3.5;
        ch.chord.slice(0, 2).forEach(function(note) {
          playNote(note, ghost, beatLen * 0.5, 0.1);
        });
      }

      // Melody - sparse, tasteful improvisation
      if (Math.random() > 0.3) {
        var melStart = t + beatLen * (Math.random() > 0.5 ? 0.5 : 2);
        var numNotes = 1 + Math.floor(Math.random() * 3);
        for (var mi = 0; mi < numNotes && mi < ch.mel.length; mi++) {
          var swing = mi % 2 === 1 ? beatLen * 0.12 : 0; // swing feel
          var mTime = melStart + mi * beatLen * 0.6 + swing;
          var mDur = beatLen * (0.8 + Math.random() * 1.0);
          playNote(ch.mel[mi], mTime, mDur, 0.2 + Math.random() * 0.1);
        }
      }

      // Walking bass (beats 2-4)
      var walkNotes = [ch.bass]; // start from root
      var bassOctave = ch.bass.charAt(ch.bass.length - 1);
      // Simple chromatic walk
      if (Math.random() > 0.4) {
        for (var bi = 1; bi < 4; bi++) {
          playNote(ch.bass, t + bi * beatLen, beatLen * 0.7, 0.2);
        }
      }

      totalLen = (ci + 1) * chordLen;
    });

    // Schedule next phrase with a breath
    var pause = 1.5 + Math.random() * 2.5;
    loopTimer = setTimeout(function() {
      if (isPlaying) playPhrase();
    }, (totalLen + pause) * 1000);
  }

  function initAudio() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    masterGain = ctx.createGain();
    masterGain.gain.value = 0;
    masterGain.connect(ctx.destination);
  }

  function startMusic() {
    if (isPlaying) return;
    if (!ctx) initAudio();
    if (ctx.state === 'suspended') ctx.resume();

    isPlaying = true;
    updateButton('loading');

    loadSamples(function() {
      if (!isPlaying) return; // user stopped during loading
      masterGain.gain.cancelScheduledValues(ctx.currentTime);
      masterGain.gain.setValueAtTime(0, ctx.currentTime);
      masterGain.gain.linearRampToValueAtTime(1.0, ctx.currentTime + 2);
      playPhrase();
      localStorage.setItem(STORAGE_KEY, 'on');
      updateButton('playing');
    });
  }

  function stopMusic() {
    if (!isPlaying) return;
    isPlaying = false;

    if (ctx && masterGain) {
      masterGain.gain.cancelScheduledValues(ctx.currentTime);
      masterGain.gain.setValueAtTime(masterGain.gain.value, ctx.currentTime);
      masterGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 1.5);
    }

    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }
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

    btn.classList.remove('active', 'loading');
    if (state === 'playing') {
      btn.classList.add('active');
      icon.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>';
      label.textContent = 'Playing';
      btn.title = 'Pause jazz piano';
    } else if (state === 'loading') {
      btn.classList.add('loading');
      icon.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>';
      label.textContent = 'Loading...';
      btn.title = 'Loading piano samples...';
    } else {
      icon.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>';
      label.textContent = 'Music';
      btn.title = 'Play jazz piano BGM';
    }
  }

  function createUI() {
    var btn = document.createElement('button');
    btn.id = 'music-toggle';
    btn.className = 'music-btn';
    btn.title = 'Play jazz piano BGM';
    btn.innerHTML =
      '<span class="music-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg></span>' +
      '<span class="music-label">Music</span>';
    btn.addEventListener('click', toggleMusic);
    document.body.appendChild(btn);

    var style = document.createElement('style');
    style.textContent =
      '.music-btn{position:fixed;bottom:28px;right:28px;z-index:999;' +
      'display:flex;align-items:center;gap:8px;' +
      'padding:12px 20px;border:none;border-radius:50px;cursor:pointer;' +
      'background:rgba(44,44,44,.88);color:#fff;' +
      'font-family:"Source Sans 3",Georgia,sans-serif;font-size:14px;font-weight:600;' +
      'letter-spacing:.5px;box-shadow:0 4px 24px rgba(0,0,0,.2);' +
      'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);' +
      'transition:all .3s cubic-bezier(.4,0,.2,1)}' +
      '.music-btn:hover{background:rgba(139,58,74,.95);box-shadow:0 6px 32px rgba(139,58,74,.4);transform:translateY(-2px)}' +
      '.music-btn.active{background:linear-gradient(135deg,#8B3A4A,#D4726A);box-shadow:0 4px 28px rgba(212,114,106,.4)}' +
      '.music-btn.active .music-icon svg{animation:musicPulse 1.5s ease-in-out infinite}' +
      '.music-btn.loading{background:rgba(196,148,74,.85);cursor:wait}' +
      '.music-btn.loading .music-icon svg{animation:spin 1s linear infinite}' +
      '.music-icon{display:flex;align-items:center}' +
      '@keyframes musicPulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.12);opacity:.8}}' +
      '@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}' +
      '@media(max-width:480px){.music-btn{bottom:16px;right:16px;padding:10px 14px;font-size:12px}.music-label{display:none}}';
    document.head.appendChild(style);

    // Auto-resume on interaction if was playing
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
