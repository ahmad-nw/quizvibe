// Host / Presenter Controller
let ws = null;
let roomPin = null;
let currentSlideIndex = -1;
let totalSlides = 0;
let currentSlide = null;
let wordCloudRenderer = null;

const KAHOOT_COLORS = ['k-red', 'k-blue', 'k-yellow', 'k-green'];
const KAHOOT_SHAPES = ['▲', '◆', '●', '■'];

function init() {
  connectWebSocket();
  setupKeyboardShortcuts();
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Host WebSocket connected");
    // Check if quiz_id is in query string
    const params = new URLSearchParams(window.location.search);
    const quizId = params.get('quiz_id');
    ws.send(JSON.stringify({
      type: "create_room",
      quiz_id: quizId
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };

  ws.onclose = () => {
    console.warn("WebSocket disconnected, reconnecting in 2s...");
    setTimeout(connectWebSocket, 2000);
  };
}

function handleMessage(msg) {
  switch (msg.type) {
    case "room_created":
      roomPin = msg.pin;
      totalSlides = msg.total_slides;
      showLobby(msg);
      break;

    case "player_joined":
      updatePlayerJoined(msg);
      break;

    case "player_left":
      updatePlayerLeft(msg);
      break;

    case "question_started":
      showQuestion(msg);
      break;

    case "timer_tick":
      updateTimer(msg.time_left);
      break;

    case "answer_count_updated":
      updateAnswerCount(msg);
      break;

    case "live_tally_update":
      updateLiveTally(msg);
      break;

    case "results_revealed":
      showResults(msg);
      break;

    case "leaderboard_revealed":
      showLeaderboard(msg);
      break;

    case "game_over_podium":
      showPodium(msg);
      break;

    case "qa_list_updated":
      updateQAList(msg.questions);
      break;

    case "error":
      alert("Error: " + msg.message);
      break;
  }
}

// === LOBBY SCREEN ===
async function showLobby(data) {
  document.getElementById('screen-lobby').style.display = 'block';
  document.getElementById('screen-question').style.display = 'none';
  document.getElementById('screen-results').style.display = 'none';
  document.getElementById('screen-leaderboard').style.display = 'none';
  document.getElementById('screen-podium').style.display = 'none';

  document.getElementById('display-pin').innerText = data.pin;
  document.getElementById('lobby-quiz-title').innerText = data.quiz_title;

  // Gunakan origin halaman saat ini (bekerja sempurna baik di domain online HTTPS maupun lokal)
  const joinUrl = `${window.location.origin}/player.html?pin=${data.pin}`;
  
  const joinUrlTextEl = document.getElementById('join-url-text');
  joinUrlTextEl.innerHTML = `<strong>${window.location.host}/player.html</strong>`;

  const qrImg = document.getElementById('lobby-qr-img');
  qrImg.src = `/api/qr?data=${encodeURIComponent(joinUrl)}`;

  // Start pleasant background lobby music
  soundEngine.startLobbyMusic();
}

function updatePlayerJoined(data) {
  soundEngine.playSwoosh();
  const container = document.getElementById('lobby-players-container');
  const countEl = document.getElementById('player-count-display');
  const startBtn = document.getElementById('btn-start-game');

  countEl.innerText = `${data.total_players} Peserta Siap`;
  startBtn.innerText = `Mulai Game (${data.total_players} Pemain)`;

  container.innerHTML = '';
  data.players.forEach(p => {
    const chip = document.createElement('div');
    chip.className = 'player-chip';
    chip.innerHTML = `<span>${p.avatar}</span> <span>${escapeHtml(p.name)}</span>`;
    container.appendChild(chip);
  });
}

function updatePlayerLeft(data) {
  const countEl = document.getElementById('player-count-display');
  const startBtn = document.getElementById('btn-start-game');
  countEl.innerText = `${data.total_players} Peserta Siap`;
  startBtn.innerText = `Mulai Game (${data.total_players} Pemain)`;
}

// === START GAME ===
function startGame() {
  soundEngine.stopLobbyMusic();
  soundEngine.playSwoosh();
  ws.send(JSON.stringify({
    type: "start_game",
    pin: roomPin
  }));
}

// === QUESTION SCREEN ===
function showQuestion(data) {
  currentSlideIndex = data.slide_index;
  currentSlide = data.slide;

  document.getElementById('screen-lobby').style.display = 'none';
  document.getElementById('screen-question').style.display = 'flex';
  document.getElementById('screen-results').style.display = 'none';
  document.getElementById('screen-leaderboard').style.display = 'none';
  document.getElementById('screen-podium').style.display = 'none';

  // Header info
  document.getElementById('question-progress').innerText = `Slide ${data.slide_index + 1} / ${data.total_slides}`;
  document.getElementById('slide-type-tag').innerText = getSlideTypeLabel(data.slide.type);

  // Question title
  document.getElementById('question-text').innerText = data.slide.question;

  // Answers count badge
  document.getElementById('answered-counter-text').innerText = `0 / ${data.total_players} Sudah Menjawab`;

  // Timer
  const timerCircle = document.getElementById('timer-display');
  timerCircle.innerText = data.slide.time_limit;
  timerCircle.classList.remove('warning');

  // Render Options or Inputs according to slide type
  const optionsContainer = document.getElementById('question-options-container');
  optionsContainer.innerHTML = '';

  if (data.slide.type === 'quiz' || data.slide.type === 'poll') {
    const grid = document.createElement('div');
    grid.className = 'kahoot-grid';

    data.slide.options.forEach((opt, idx) => {
      const btn = document.createElement('div');
      const colorClass = KAHOOT_COLORS[idx % 4];
      const shape = KAHOOT_SHAPES[idx % 4];
      btn.className = `kahoot-btn ${colorClass}`;
      btn.innerHTML = `
        <span class="kahoot-shape">${shape}</span>
        <span class="kahoot-text">${escapeHtml(opt.text)}</span>
      `;
      grid.appendChild(btn);
    });
    optionsContainer.appendChild(grid);
  } else if (data.slide.type === 'true_false') {
    const grid = document.createElement('div');
    grid.className = 'tf-grid';
    grid.innerHTML = `
      <div class="kahoot-btn k-blue" style="font-size:2rem;">
        <span class="kahoot-shape">✔</span>
        <span class="kahoot-text">BENAR</span>
      </div>
      <div class="kahoot-btn k-red" style="font-size:2rem;">
        <span class="kahoot-shape">✖</span>
        <span class="kahoot-text">SALAH</span>
      </div>
    `;
    optionsContainer.appendChild(grid);
  } else if (data.slide.type === 'word_cloud') {
    optionsContainer.innerHTML = `
      <div style="text-align:center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">☁️</div>
        <h3>Peserta sedang mengetik kata pilihan di smartphone mereka...</h3>
        <p class="text-muted mt-2">Kata-kata akan muncul langsung di layar dalam bentuk Awan Kata (Word Cloud)!</p>
      </div>
    `;
  } else if (data.slide.type === 'qa') {
    optionsContainer.innerHTML = `
      <div style="text-align:center; padding: 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">💬</div>
        <h3>Sesi Tanya Jawab Langsung (Q&A)</h3>
        <p class="text-muted mt-2">Peserta dapat menuliskan pertanyaan dan memberi upvote (jempol) pada pertanyaan peserta lain.</p>
      </div>
    `;
  }
}

function updateTimer(timeLeft) {
  const timerCircle = document.getElementById('timer-display');
  if (timerCircle) {
    timerCircle.innerText = timeLeft;
    if (timeLeft <= 5) {
      timerCircle.classList.add('warning');
      soundEngine.playUrgentTick();
    } else {
      soundEngine.playTick();
    }
  }
}

function updateAnswerCount(data) {
  const counter = document.getElementById('answered-counter-text');
  if (counter) {
    counter.innerText = `${data.answered_count} / ${data.total_players} Sudah Menjawab`;
  }
}

function updateLiveTally(data) {
  // If word cloud or live poll is on screen, update dynamic visuals
}

function skipTimer() {
  ws.send(JSON.stringify({
    type: "skip_timer",
    pin: roomPin
  }));
}

// === RESULTS SCREEN ===
function showResults(data) {
  soundEngine.playTimesUp();

  document.getElementById('screen-question').style.display = 'none';
  document.getElementById('screen-results').style.display = 'flex';

  document.getElementById('results-question-text').innerText = currentSlide ? currentSlide.question : '';

  const chartArea = document.getElementById('results-chart-area');
  chartArea.innerHTML = '';

  if (data.slide_type === 'quiz' || data.slide_type === 'true_false' || data.slide_type === 'poll') {
    // Render Bar Chart
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-container';

    const maxVotes = Math.max(1, ...Object.values(data.answers_tally || {}));

    data.options.forEach((opt, idx) => {
      const votes = (data.answers_tally && data.answers_tally[idx]) || 0;
      const heightPercent = Math.max(12, Math.round((votes / maxVotes) * 90));
      const isCorrect = (data.correct_index === idx);

      const col = document.createElement('div');
      col.className = 'chart-bar-col';

      const bar = document.createElement('div');
      bar.className = `chart-bar ${KAHOOT_COLORS[idx % 4]}`;
      bar.style.height = `${heightPercent}%`;
      bar.innerHTML = `<span>${votes}</span>`;

      if (isCorrect) {
        bar.innerHTML += `<span class="correct-indicator">✅</span>`;
        bar.style.boxShadow = '0 0 20px #10b981';
      }

      const label = document.createElement('div');
      label.className = 'chart-label';
      label.innerText = `${KAHOOT_SHAPES[idx % 4]} ${opt.text}`;

      col.appendChild(bar);
      col.appendChild(label);
      chartContainer.appendChild(col);
    });

    chartArea.appendChild(chartContainer);
  } else if (data.slide_type === 'word_cloud') {
    // Render Word Cloud Canvas
    const canvas = document.createElement('canvas');
    canvas.className = 'word-cloud-canvas';
    canvas.width = 900;
    canvas.height = 420;
    chartArea.appendChild(canvas);

    if (!wordCloudRenderer) {
      wordCloudRenderer = new WordCloudRenderer(canvas);
    } else {
      wordCloudRenderer.setCanvas(canvas);
    }
    wordCloudRenderer.render(data.word_cloud_tally || {});
  } else if (data.slide_type === 'qa') {
    // Render Q&A list
    const list = document.createElement('div');
    list.className = 'qa-card-list';
    if (!data.qa_questions || data.qa_questions.length === 0) {
      list.innerHTML = '<p class="text-muted text-center">Belum ada pertanyaan diajukan.</p>';
    } else {
      data.qa_questions.forEach(q => {
        const item = document.createElement('div');
        item.className = 'qa-card';
        item.innerHTML = `
          <div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.25rem;">
              <span>${q.avatar}</span> <strong>${escapeHtml(q.author)}</strong>
            </div>
            <div style="font-size:1.1rem; font-weight:700;">${escapeHtml(q.text)}</div>
          </div>
          <div style="font-size:1.2rem; font-weight:800; color:#38bdf8; display:flex; align-items:center; gap:0.4rem;">
            👍 <span>${q.votes}</span>
          </div>
        `;
        list.appendChild(item);
      });
    }
    chartArea.appendChild(list);
  }
}

// === LEADERBOARD SCREEN ===
function showLeaderboardBtn() {
  ws.send(JSON.stringify({
    type: "show_leaderboard",
    pin: roomPin
  }));
}

function showLeaderboard(data) {
  soundEngine.playSwoosh();

  document.getElementById('screen-results').style.display = 'none';
  document.getElementById('screen-leaderboard').style.display = 'flex';

  const listContainer = document.getElementById('leaderboard-list');
  listContainer.innerHTML = '';

  data.leaderboard.forEach(p => {
    const item = document.createElement('div');
    item.className = `leaderboard-item ${p.rank === 1 ? 'rank-1' : ''}`;

    let streakHtml = '';
    if (p.streak >= 2) {
      streakHtml = `<span class="streak-badge">🔥 ${p.streak} Streak</span>`;
    }

    item.innerHTML = `
      <div class="rank-badge">${p.rank}</div>
      <div class="player-info">
        <span style="font-size:1.6rem;">${p.avatar}</span>
        <span>${escapeHtml(p.name)}</span>
        ${streakHtml}
      </div>
      <div class="player-score">${p.score.toLocaleString()} pts</div>
    `;
    listContainer.appendChild(item);
  });

  const nextBtn = document.getElementById('btn-next-action');
  if (data.is_last_slide) {
    nextBtn.innerText = 'Lihat Pemenang Akhir (Podium) 🏆';
  } else {
    nextBtn.innerText = 'Lanjut ke Soal Berikutnya ➡️';
  }
}

function nextSlideAction() {
  ws.send(JSON.stringify({
    type: "next_slide",
    pin: roomPin
  }));
}

// === PODIUM SCREEN ===
function showPodium(data) {
  document.getElementById('screen-leaderboard').style.display = 'none';
  document.getElementById('screen-podium').style.display = 'flex';

  soundEngine.playPodiumFanfare();
  confetti.shoot(250);

  // Interval confetti showers
  setTimeout(() => confetti.shoot(150), 1200);
  setTimeout(() => confetti.shoot(150), 2400);

  const podium = data.podium || [];
  const p1 = podium[0];
  const p2 = podium[1];
  const p3 = podium[2];

  if (p1) {
    document.getElementById('podium-1-name').innerText = p1.name;
    document.getElementById('podium-1-avatar').innerText = p1.avatar;
    document.getElementById('podium-1-score').innerText = `${p1.score.toLocaleString()} pts`;
  }
  if (p2) {
    document.getElementById('podium-2-name').innerText = p2.name;
    document.getElementById('podium-2-avatar').innerText = p2.avatar;
    document.getElementById('podium-2-score').innerText = `${p2.score.toLocaleString()} pts`;
  }
  if (p3) {
    document.getElementById('podium-3-name').innerText = p3.name;
    document.getElementById('podium-3-avatar').innerText = p3.avatar;
    document.getElementById('podium-3-score').innerText = `${p3.score.toLocaleString()} pts`;
  }

  // Full rankings table
  const rankingsContainer = document.getElementById('full-rankings-table');
  rankingsContainer.innerHTML = '';
  (data.rankings || []).forEach(p => {
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.justifyContent = 'space-between';
    row.style.padding = '0.6rem 1rem';
    row.style.borderBottom = '1px solid rgba(255,255,255,0.08)';
    row.innerHTML = `
      <div><strong>#${p.rank}</strong> ${p.avatar} ${escapeHtml(p.name)}</div>
      <div style="color:#38bdf8; font-weight:800;">${p.score.toLocaleString()} pts</div>
    `;
    rankingsContainer.appendChild(row);
  });
}

function toggleMute() {
  const isMuted = soundEngine.toggleMute();
  const btn = document.getElementById('btn-mute');
  btn.innerText = isMuted ? '🔇 Audio Mati' : '🔊 Audio Hidup';
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
}

function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && e.target === document.body) {
      e.preventDefault();
      const resultsScreen = document.getElementById('screen-results');
      const leaderboardScreen = document.getElementById('screen-leaderboard');
      if (resultsScreen.style.display === 'flex') {
        showLeaderboardBtn();
      } else if (leaderboardScreen.style.display === 'flex') {
        nextSlideAction();
      }
    }
  });
}

function getSlideTypeLabel(type) {
  const map = {
    quiz: "🎯 Kuis Pilihan Ganda",
    true_false: "⚖️ Benar atau Salah",
    poll: "📊 Polling Opini (Mentimeter)",
    word_cloud: "☁️ Awan Kata (Word Cloud)",
    qa: "💬 Tanya Jawab (Q&A)"
  };
  return map[type] || "Slide Interaktif";
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[m]));
}

window.addEventListener('DOMContentLoaded', init);
