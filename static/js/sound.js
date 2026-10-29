// Web Audio API Synthesizer Engine for Sound FX & Lobby Music
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.lobbyInterval = null;
    this.musicGain = null;
  }

  ensureContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.isMuted) {
      this.stopLobbyMusic();
    }
    return this.isMuted;
  }

  // Play a simple tone
  playTone(freq, duration = 0.15, type = 'sine', gainVal = 0.2) {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn("Audio error:", e);
    }
  }

  // Countdown tick
  playTick() {
    this.playTone(880, 0.08, 'triangle', 0.15);
  }

  // Final 5 seconds tick (higher pitch)
  playUrgentTick() {
    this.playTone(1200, 0.1, 'square', 0.2);
  }

  // Correct answer chime (Upbeat arpeggio)
  playCorrect() {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 0.25, 'sine', 0.25);
      }, idx * 70);
    });
  }

  // Wrong answer (Descending soft buzz)
  playWrong() {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(260, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(110, this.ctx.currentTime + 0.4);

      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.4);
    } catch (e) {}
  }

  // Time's up buzzer
  playTimesUp() {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    this.playTone(180, 0.6, 'sawtooth', 0.25);
  }

  // Swoosh sound for transitions
  playSwoosh() {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(200, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(800, this.ctx.currentTime + 0.2);

      gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.2);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.2);
    } catch (e) {}
  }

  // Victory fanfare for podium
  playPodiumFanfare() {
    if (this.isMuted) return;
    this.ensureContext();
    if (!this.ctx) return;

    const sequence = [
      { note: 523.25, time: 0, dur: 0.2 },      // C5
      { note: 659.25, time: 200, dur: 0.2 },    // E5
      { note: 783.99, time: 400, dur: 0.2 },    // G5
      { note: 1046.50, time: 600, dur: 0.6 },   // C6 (hold)
      { note: 880.00, time: 1300, dur: 0.2 },   // A5
      { note: 1046.50, time: 1500, dur: 0.9 }   // C6 (grand finish)
    ];

    sequence.forEach(s => {
      setTimeout(() => {
        this.playTone(s.note, s.dur, 'triangle', 0.3);
      }, s.time);
    });
  }

  // Catchy lobby synth loop
  startLobbyMusic() {
    if (this.isMuted || this.lobbyInterval) return;
    this.ensureContext();

    const melody = [
      392.00, 0, 440.00, 0, 523.25, 0, 659.25, 0,
      587.33, 523.25, 440.00, 0, 392.00, 0, 329.63, 0
    ];
    let step = 0;

    this.lobbyInterval = setInterval(() => {
      if (this.isMuted) {
        this.stopLobbyMusic();
        return;
      }
      const note = melody[step % melody.length];
      if (note > 0) {
        this.playTone(note, 0.12, 'sine', 0.08);
      }
      step++;
    }, 180);
  }

  stopLobbyMusic() {
    if (this.lobbyInterval) {
      clearInterval(this.lobbyInterval);
      this.lobbyInterval = null;
    }
  }
}

const soundEngine = new SoundEngine();
