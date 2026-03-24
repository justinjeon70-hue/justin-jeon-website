/**
 * Jazz Piano CCM - Ambient Background Music
 * for "The Oxytocin Story" by Justin Jeon
 *
 * Generates warm jazz piano with CCM-influenced progressions
 * Pure Web Audio API - no external files needed
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'oxytocin-book-music';
  let ctx, masterGain, reverbNode, delayNode;
  let isPlaying = false;
  let loopTimer = null;

  // === CCM Jazz Chord Progressions (Key of C) ===
  // Using jazz voicings: 7ths, 9ths, add9
  const PROGRESSIONS = [
    // I - V/B - vi - IV (classic CCM "worship" feel)
    {
      chords: [
        { bass: 130.81, notes: [261.63, 329.63, 392.00, 493.88] },     // Cmaj7
        { bass: 246.94, notes: [293.66, 392.00, 493.88, 587.33] },     // G/B
        { bass: 220.00, notes: [261.63, 329.63, 440.00, 523.25] },     // Am7
        { bass: 174.61, notes: [261.63, 349.23, 440.00, 523.25] },     // Fmaj7
      ]
    },
    // I - iii - vi - IV - V
    {
      chords: [
        { bass: 130.81, notes: [261.63, 329.63, 392.00, 493.88] },     // Cmaj7
        { bass: 164.81, notes: [246.94, 329.63, 392.00, 493.88] },     // Em7
        { bass: 220.00, notes: [261.63, 329.63, 415.30, 523.25] },     // Am9
        { bass: 174.61, notes: [261.63, 349.23, 440.00, 523.25] },     // Fmaj7
        { bass: 196.00, notes: [293.66, 392.00, 493.88, 587.33] },     // G9
      ]
    },
    // vi - IV - I - V (emotional CCM)
    {
      chords: [
        { bass: 220.00, notes: [261.63, 329.63, 440.00, 523.25] },     // Am7
        { bass: 174.61, notes: [261.63, 349.23, 440.00, 523.25] },     // Fmaj7
        { bass: 130.81, notes: [261.63, 329.63, 392.00, 493.88] },     // Cmaj7
        { bass: 196.00, notes: [246.94, 349.23, 440.00, 587.33] },     // Gsus4 → G
      ]
    },
    // II - V - I - vi (jazz standard)
    {
      chords: [
        { bass: 146.83, notes: [261.63, 293.66, 369.99, 440.00] },     // Dm9
        { bass: 196.00, notes: [293.66, 349.23, 493.88, 587.33] },     // G13
        { bass: 130.81, notes: [261.63, 329.63, 493.88, 587.33] },     // Cmaj9
        { bass: 220.00, notes: [261.63, 329.63, 392.00, 523.25] },     // Am7
      ]
    },
  ];

  // Jazz scale notes for melody improvisation (C major pentatonic + blue notes)
  const MELODY_SCALE = [
    523.25, 587.33, 659.25, 783.99, 880.00,  // C D E G A (pentatonic, octave 5)
    1046.50, 987.77, 880.00, 783.99, 659.25,  // high C B A G E
    587.33, 523.25, 493.88, 440.00, 392.00,    // D C B A G (octave 4)
  ];

  // Walking bass patterns (scale degrees relative to root)
  const WALK_PATTERNS = [
    [1, 1.25, 1.5, 1.25],
    [1, 0.75, 0.667, 0.75],
    [1, 1.125, 1.25, 1.5],
  ];

  // === Audio Engine ===

  function createReverb(duration, decay) {
    const rate = ctx.sampleRate;
    const len = rate * duration;
    const buf = ctx.createBuffer(2, len, rate);
    for (let ch = 0; ch < 2; ch++) {
      const d = buf.getChannelData(ch);
      for (let i = 0; i < len; i++) {
        d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
      }
    }
    const conv = ctx.createConvolver();
    conv.buffer = buf;
    return conv;
  }

  function initAudio() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();

    masterGain = ctx.createGain();
    masterGain.gain.value = 0;
    masterGain.connect(ctx.destination);

    // Reverb (warm hall)
    reverbNode = createReverb(3.5, 1.8);
    var reverbMix = ctx.createGain();
    reverbMix.gain.value = 0.35;
    reverbNode.connect(reverbMix);
    reverbMix.connect(masterGain);

    // Delay (jazz slapback)
    delayNode = ctx.createDelay(1.0);
    delayNode.delayTime.value = 0.375; // dotted eighth for jazz feel
    var delayFb = ctx.createGain();
    delayFb.gain.value = 0.15;
    var delayMix = ctx.createGain();
    delayMix.gain.value = 0.12;
    delayNode.connect(delayFb);
    delayFb.connect(delayNode);
    delayNode.connect(delayMix);
    delayMix.connect(masterGain);

    // Dry signal
    var dryGain = ctx.createGain();
    dryGain.gain.value = 0.6;
    dryGain.connect(masterGain);

    // Store refs for routing
    ctx._dry = dryGain;
    ctx._reverb = reverbNode;
    ctx._delay = delayNode;
  }

  // Piano-like tone using multiple harmonics
  function playPiano(freq, time, duration, velocity) {
    if (!ctx || !isPlaying) return;
    vel = velocity || 0.04;

    // Fundamental + harmonics for piano timbre
    const harmonics = [
      { ratio: 1, amp: 1.0 },
      { ratio: 2, amp: 0.4 },
      { ratio: 3, amp: 0.15 },
      { ratio: 4, amp: 0.08 },
    ];

    const noteGain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = Math.min(freq * 6, 4000);
    filter.Q.value = 0.7;

    // Piano envelope: quick attack, gradual decay
    noteGain.gain.setValueAtTime(0, time);
    noteGain.gain.linearRampToValueAtTime(vel, time + 0.008);
    noteGain.gain.setTargetAtTime(vel * 0.6, time + 0.008, 0.15);
    noteGain.gain.setTargetAtTime(vel * 0.3, time + duration * 0.4, duration * 0.3);
    noteGain.gain.linearRampToValueAtTime(0, time + duration);

    harmonics.forEach(function(h) {
      var osc = ctx.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = freq * h.ratio;
      var hGain = ctx.createGain();
      hGain.gain.value = h.amp;
      osc.connect(hGain);
      hGain.connect(filter);
      osc.start(time);
      osc.stop(time + duration + 0.1);
    });

    filter.connect(noteGain);
    noteGain.connect(ctx._dry);
    noteGain.connect(ctx._reverb);
    noteGain.connect(ctx._delay);
  }

  // Soft bass note
  function playBass(freq, time, duration) {
    if (!ctx || !isPlaying) return;
    var osc = ctx.createOscillator();
    var osc2 = ctx.createOscillator();
    var gain = ctx.createGain();
    var filter = ctx.createBiquadFilter();

    osc.type = 'sine';
    osc.frequency.value = freq;
    osc2.type = 'triangle';
    osc2.frequency.value = freq * 1.001;

    filter.type = 'lowpass';
    filter.frequency.value = 400;

    gain.gain.setValueAtTime(0, time);
    gain.gain.linearRampToValueAtTime(0.05, time + 0.02);
    gain.gain.setTargetAtTime(0.035, time + 0.1, 0.3);
    gain.gain.linearRampToValueAtTime(0, time + duration);

    osc.connect(filter);
    osc2.connect(filter);
    filter.connect(gain);
    gain.connect(ctx._dry);
    gain.connect(ctx._reverb);

    osc.start(time);
    osc2.start(time);
    osc.stop(time + duration + 0.1);
    osc2.stop(time + duration + 0.1);
  }

  // === Music Composition Engine ===

  function playSection() {
    if (!ctx || !isPlaying) return;

    var prog = PROGRESSIONS[Math.floor(Math.random() * PROGRESSIONS.length)];
    var now = ctx.currentTime + 0.1;
    var beatDur = 0.55 + Math.random() * 0.1; // ~110 BPM swing feel
    var chordDur = beatDur * 4; // 4 beats per chord

    prog.chords.forEach(function(chord, ci) {
      var chordStart = now + ci * chordDur;

      // === Jazz Piano Comping (syncopated) ===
      // Play chord on beat 1
      chord.notes.forEach(function(note, ni) {
        playPiano(note, chordStart + ni * 0.015, chordDur * 0.85, 0.025);
      });

      // Syncopated re-hit on "and of 2" (jazz comp)
      if (Math.random() > 0.3) {
        var rehitTime = chordStart + beatDur * 1.5;
        chord.notes.forEach(function(note, ni) {
          playPiano(note, rehitTime + ni * 0.01, beatDur * 1.5, 0.018);
        });
      }

      // Occasional ghost chord on beat 4 "and"
      if (Math.random() > 0.6) {
        var ghostTime = chordStart + beatDur * 3.5;
        chord.notes.slice(1, 3).forEach(function(note) {
          playPiano(note, ghostTime, beatDur * 0.4, 0.012);
        });
      }

      // === Walking Bass ===
      var walkPat = WALK_PATTERNS[Math.floor(Math.random() * WALK_PATTERNS.length)];
      walkPat.forEach(function(ratio, bi) {
        playBass(chord.bass * ratio, chordStart + bi * beatDur, beatDur * 0.85);
      });

      // === Melody Improvisation (sparse, tasteful) ===
      if (Math.random() > 0.45) {
        var melStart = chordStart + beatDur * (Math.random() > 0.5 ? 0 : 2);
        var numNotes = 2 + Math.floor(Math.random() * 3);
        var startIdx = Math.floor(Math.random() * (MELODY_SCALE.length - numNotes));

        for (var mi = 0; mi < numNotes; mi++) {
          var mNote = MELODY_SCALE[startIdx + mi];
          // Swing timing: long-short pattern
          var swing = mi % 2 === 0 ? 0 : beatDur * 0.15;
          var mTime = melStart + mi * (beatDur * 0.5) + swing;
          var mDur = beatDur * (0.4 + Math.random() * 0.6);
          playPiano(mNote, mTime, mDur, 0.02 + Math.random() * 0.015);
        }
      }
    });

    // Schedule next section
    var totalDur = prog.chords.length * chordDur;
    var pause = 0.5 + Math.random() * 1.5; // brief pause between phrases
    loopTimer = setTimeout(playSection, (totalDur + pause) * 1000);
  }

  // === Controls ===

  function startMusic() {
    if (isPlaying) return;
    if (!ctx) initAudio();
    if (ctx.state === 'suspended') ctx.resume();

    isPlaying = true;
    masterGain.gain.cancelScheduledValues(ctx.currentTime);
    masterGain.gain.setValueAtTime(masterGain.gain.value, ctx.currentTime);
    masterGain.gain.linearRampToValueAtTime(1.0, ctx.currentTime + 3);

    playSection();
    localStorage.setItem(STORAGE_KEY, 'on');
    updateButton(true);
  }

  function stopMusic() {
    if (!isPlaying) return;
    isPlaying = false;

    if (ctx && masterGain) {
      masterGain.gain.cancelScheduledValues(ctx.currentTime);
      masterGain.gain.setValueAtTime(masterGain.gain.value, ctx.currentTime);
      masterGain.gain.linearRampToValueAtTime(0, ctx.currentTime + 2);
    }

    if (loopTimer) clearTimeout(loopTimer);
    localStorage.setItem(STORAGE_KEY, 'off');
    updateButton(false);
  }

  function toggleMusic() {
    if (isPlaying) stopMusic(); else startMusic();
  }

  function updateButton(on) {
    var btn = document.getElementById('music-toggle');
    if (!btn) return;
    btn.classList.toggle('active', on);
    btn.title = on ? 'Pause background music' : 'Play jazz piano BGM';
    btn.querySelector('.music-label').textContent = on ? 'Playing' : 'Music';
  }

  // === UI ===

  function createUI() {
    var btn = document.createElement('button');
    btn.id = 'music-toggle';
    btn.className = 'music-btn';
    btn.title = 'Play jazz piano BGM';
    btn.innerHTML = '<span class="music-icon">' +
      '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
      '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>' +
      '</svg></span><span class="music-label">Music</span>';
    btn.addEventListener('click', toggleMusic);
    document.body.appendChild(btn);

    var style = document.createElement('style');
    style.textContent =
      '.music-btn{position:fixed;bottom:28px;right:28px;z-index:999;' +
      'display:flex;align-items:center;gap:8px;' +
      'padding:12px 20px;border:none;border-radius:50px;cursor:pointer;' +
      'background:rgba(44,44,44,.85);color:#fff;' +
      'font-family:"Source Sans 3",Georgia,sans-serif;font-size:14px;font-weight:600;' +
      'letter-spacing:.5px;box-shadow:0 4px 24px rgba(0,0,0,.2);' +
      'backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);' +
      'transition:all .3s cubic-bezier(.4,0,.2,1)}' +
      '.music-btn:hover{background:rgba(139,58,74,.95);box-shadow:0 6px 32px rgba(139,58,74,.4);transform:translateY(-2px)}' +
      '.music-btn.active{background:linear-gradient(135deg,#8B3A4A,#D4726A);box-shadow:0 4px 28px rgba(212,114,106,.4)}' +
      '.music-btn.active .music-icon svg{animation:musicPulse 1.5s ease-in-out infinite}' +
      '.music-icon{display:flex;align-items:center}' +
      '@keyframes musicPulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.12);opacity:.8}}' +
      '@media(max-width:480px){.music-btn{bottom:16px;right:16px;padding:10px 14px;font-size:12px}.music-label{display:none}}';
    document.head.appendChild(style);

    // Auto-resume if was playing before
    if (localStorage.getItem(STORAGE_KEY) === 'on') {
      var resume = function() {
        startMusic();
        document.removeEventListener('click', resume);
        document.removeEventListener('scroll', resume);
      };
      document.addEventListener('click', resume, { once: false });
      document.addEventListener('scroll', resume, { once: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createUI);
  } else {
    createUI();
  }
})();
