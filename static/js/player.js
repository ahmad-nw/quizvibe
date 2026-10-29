// Participant / Player Client Logic
let ws = null;
let currentPin = null;
let myPlayerId = null;
let selectedAvatar = '🦊';
let myScore = 0;
let myStreak = 0;
let hasAnsweredCurrentQuestion = false;

const AVATARS = ['🦊', '🦁', '🐼', '🐱', '🦄', '🚀', '⚡', '🎮', '🍕', '🥑', '👑', '🎯', '🏆', '🌟', '💡', '🤖'];

function init() {
  renderAvatarSelector();
  checkUrlParams();
  connectWebSocket();
}

function checkUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const pin = params.get('pin');
  if (pin) {
    const pinInput = document.getElementById('player-pin-input');
    if (pinInput) {
      pinInput.value = pin;
    }
  }
}

function renderAvatarSelector() {
  const container = document.getElementById('avatar-selector-grid');
  if (!container) return;

  container.innerHTML = '';
  AVATARS.forEach(av => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `avatar-btn ${av === selectedAvatar ? 'selected' : ''}`;
    btn.innerText = av;
    btn.onclick = () => {
      selectedAvatar = av;
      document.querySelectorAll('.avatar-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
    };
    container.appendChild(btn);
  });
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Player WebSocket connected");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleServerMessage(data);
  };

  ws.onclose = () => {
    console.warn("Player disconnected, reconnecting...");
    setTimeout(connectWebSocket, 2000);
  };
}

function joinGame() {
  const pinInput = document.getElementById('player-pin-input');
  const nameInput = document.getElementById('player-name-input');

  const pin = pinInput.value.trim();
  const name = nameInput.value.trim() || 'Pemain';

  if (!pin || pin.length < 5) {
    alert("Masukkan 6-digit PIN Game yang valid!");
    return;
  }

  currentPin = pin;

  ws.send(JSON.stringify({
    type: "join_room",
    pin: pin,
    name: name,
    avatar: selectedAvatar
  }));
}

function handleServerMessage(msg) {
  switch (msg.type) {
    case "joined_success":
      myPlayerId = msg.player.id;
      myScore = msg.player.score;
      showPlayerLobby(msg);
      break;

    case "question_started":
      showInGameQuestion(msg);
      break;

    case "timer_tick":
      updatePlayerTimer(msg.time_left);
      break;

    case "answer_received":
      showAnswerLocked(msg);
      break;

    case "word_submitted":
      showWordSubmitted();
      break;

    case "results_revealed":
      showQuestionResult(msg);
      break;

    case "leaderboard_revealed":
      showPlayerLeaderboard(msg);
      break;

    case "game_over_podium":
      showPlayerPodium(msg);
      break;

    case "qa_list_updated":
      renderPlayerQAList(msg.questions);
      break;

    case "error":
      alert(msg.message);
      break;
  }
}

// === SCREEN: PLAYER LOBBY ===
function showPlayerLobby(data) {
  document.getElementById('screen-join').style.display = 'none';
  document.getElementById('screen-waiting-lobby').style.display = 'flex';
  document.getElementById('screen-game-active').style.display = 'none';
  document.getElementById('screen-feedback').style.display = 'none';
  document.getElementById('screen-final').style.display = 'none';

  document.getElementById('lobby-player-avatar').innerText = selectedAvatar;
  document.getElementById('lobby-player-name').innerText = data.player.name;
  document.getElementById('lobby-quiz-info').innerText = data.quiz_title;
}

// === SCREEN: IN-GAME QUESTION ===
function showInGameQuestion(data) {
  hasAnsweredCurrentQuestion = false;

  document.getElementById('screen-waiting-lobby').style.display = 'none';
  document.getElementById('screen-game-active').style.display = 'flex';
  document.getElementById('screen-feedback').style.display = 'none';
  document.getElementById('screen-final').style.display = 'none';

  document.getElementById('player-slide-counter').innerText = `${data.slide_index + 1} / ${data.total_slides}`;
  document.getElementById('player-timer-badge').innerText = `⏱️ ${data.slide.time_limit}s`;
  document.getElementById('player-status-msg').innerText = 'Pilih jawabanmu!';

  const container = document.getElementById('player-input-container');
  container.innerHTML = '';

  const slideType = data.slide.type;

  if (slideType === 'quiz') {
    // 4 Big Kahoot Color/Shape Buttons
    const grid = document.createElement('div');
    grid.className = 'kahoot-grid';
    grid.style.height = '360px';

    const colors = ['k-red', 'k-blue', 'k-yellow', 'k-green'];
    const shapes = ['▲', '◆', '●', '■'];

    data.slide.options.forEach((opt, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `kahoot-btn ${colors[idx % 4]} kahoot-mobile-btn`;
      btn.innerHTML = `<span style="font-size:3rem;">${shapes[idx % 4]}</span>`;
      btn.onclick = () => submitAnswer(idx, btn);
      grid.appendChild(btn);
    });
    container.appendChild(grid);
  } else if (slideType === 'true_false') {
    const grid = document.createElement('div');
    grid.className = 'tf-grid';
    grid.style.height = '300px';

    const trueBtn = document.createElement('button');
    trueBtn.type = 'button';
    trueBtn.className = 'kahoot-btn k-blue kahoot-mobile-btn';
    trueBtn.innerHTML = '<span>✔ BENAR</span>';
    trueBtn.onclick = () => submitAnswer(0, trueBtn);

    const falseBtn = document.createElement('button');
    falseBtn.type = 'button';
    falseBtn.className = 'kahoot-btn k-red kahoot-mobile-btn';
    falseBtn.innerHTML = '<span>✖ SALAH</span>';
    falseBtn.onclick = () => submitAnswer(1, falseBtn);

    grid.appendChild(trueBtn);
    grid.appendChild(falseBtn);
    container.appendChild(grid);
  } else if (slideType === 'poll') {
    const list = document.createElement('div');
    list.style.display = 'flex';
    list.style.flexDirection = 'column';
    list.style.gap = '0.75rem';
    list.style.width = '100%';

    data.slide.options.forEach((opt, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-outline';
      btn.style.padding = '1.2rem';
      btn.style.fontSize = '1.1rem';
      btn.style.textAlign = 'left';
      btn.innerText = opt.text;
      btn.onclick = () => submitAnswer(idx, btn);
      list.appendChild(btn);
    });
    container.appendChild(list);
  } else if (slideType === 'word_cloud') {
    container.innerHTML = `
      <div style="width: 100%; text-align: center;">
        <h3 style="margin-bottom: 1rem;">Ketik 1 Kata / Frasa:</h3>
        <input type="text" id="word-cloud-input" class="pin-input" placeholder="contoh: Seru!" maxlength="25" style="font-size:1.4rem; letter-spacing:0;" />
        <button type="button" class="btn btn-primary btn-lg w-full mt-2" onclick="submitWordCloud()">Kirim Kata 🚀</button>
      </div>
    `;
  } else if (slideType === 'qa') {
    container.innerHTML = `
      <div style="width: 100%;">
        <h4 style="margin-bottom: 0.5rem;">Tulis Pertanyaanmu:</h4>
        <div style="display:flex; gap:0.5rem; margin-bottom: 1rem;">
          <input type="text" id="qa-text-input" class="pin-input" placeholder="Tuliskan pertanyaan..." style="font-size:1rem; letter-spacing:0; padding:0.6rem;" />
          <button type="button" class="btn btn-primary" onclick="submitQAQuestion()">Kirim</button>
        </div>
        <h4 style="margin-bottom: 0.5rem;">Daftar Pertanyaan (Beri Upvote):</h4>
        <div id="player-qa-list" style="display:flex; flex-direction:column; gap:0.5rem; max-height:200px; overflow-y:auto;">
          <p class="text-muted" style="font-size:0.9rem;">Belum ada pertanyaan.</p>
        </div>
      </div>
    `;
  }
}

function updatePlayerTimer(timeLeft) {
  const timerBadge = document.getElementById('player-timer-badge');
  if (timerBadge) {
    timerBadge.innerText = `⏱️ ${timeLeft}s`;
  }
}

function submitAnswer(choiceIndex, btnElement) {
  if (hasAnsweredCurrentQuestion) return;
  hasAnsweredCurrentQuestion = true;

  if (navigator.vibrate) {
    navigator.vibrate(60);
  }

  // Visual lock
  document.querySelectorAll('#player-input-container button').forEach(b => {
    b.classList.add('disabled');
  });
  if (btnElement) {
    btnElement.style.border = '4px solid #fff';
  }

  document.getElementById('player-status-msg').innerText = 'Jawaban Terkirim! ✅ Menunggu yang lain...';

  ws.send(JSON.stringify({
    type: "submit_answer",
    pin: currentPin,
    choice: choiceIndex
  }));
}

function submitWordCloud() {
  if (hasAnsweredCurrentQuestion) return;
  const input = document.getElementById('word-cloud-input');
  const word = input.value.trim();
  if (!word) return;

  hasAnsweredCurrentQuestion = true;
  document.getElementById('player-status-msg').innerText = 'Kata terkirim ke Awan Kata! ☁️';

  ws.send(JSON.stringify({
    type: "submit_answer",
    pin: currentPin,
    words: [word]
  }));

  input.disabled = true;
}

function submitQAQuestion() {
  const input = document.getElementById('qa-text-input');
  const text = input.value.trim();
  if (!text) return;

  ws.send(JSON.stringify({
    type: "submit_answer",
    pin: currentPin,
    text: text
  }));

  input.value = '';
}

function upvoteQuestion(qId) {
  ws.send(JSON.stringify({
    type: "upvote_qa",
    pin: currentPin,
    question_id: qId
  }));
}

function renderPlayerQAList(questions) {
  const listEl = document.getElementById('player-qa-list');
  if (!listEl) return;
  listEl.innerHTML = '';
  (questions || []).forEach(q => {
    const card = document.createElement('div');
    card.className = 'qa-card';
    card.style.padding = '0.6rem 0.8rem';
    card.innerHTML = `
      <div style="font-size:0.9rem;">
        <span style="font-size:0.75rem; color:#94a3b8;">${q.avatar} ${escapeHtml(q.author)}</span>
        <div>${escapeHtml(q.text)}</div>
      </div>
      <button type="button" class="btn btn-outline" style="padding:0.3rem 0.6rem; font-size:0.85rem;" onclick="upvoteQuestion('${q.id}')">
        👍 ${q.votes}
      </button>
    `;
    listEl.appendChild(card);
  });
}

function showAnswerLocked(msg) {
  // Handled
}

function showWordSubmitted() {
  document.getElementById('player-status-msg').innerText = 'Kata terkirim ke layar presentasi! ☁️';
}

// === SCREEN: RESULTS & FEEDBACK ===
function showQuestionResult(msg) {
  document.getElementById('screen-game-active').style.display = 'none';
  document.getElementById('screen-feedback').style.display = 'flex';

  const banner = document.getElementById('feedback-banner-box');
  const title = document.getElementById('feedback-title');
  const scoreGain = document.getElementById('feedback-points-gain');
  const streakText = document.getElementById('feedback-streak');
  const rankText = document.getElementById('feedback-rank');

  myScore = msg.total_score || myScore;
  myStreak = msg.streak || 0;

  if (msg.slide_type === 'quiz' || msg.slide_type === 'true_false') {
    if (msg.is_correct) {
      soundEngine.playCorrect();
      banner.className = 'feedback-banner feedback-correct';
      title.innerText = 'Luar Biasa! Jawaban Benar! 🎉';
      scoreGain.innerText = `+${msg.last_score_gain.toLocaleString()} Poin`;
    } else {
      soundEngine.playWrong();
      banner.className = 'feedback-banner feedback-wrong';
      title.innerText = 'Oops! Kurang Tepat 😢';
      scoreGain.innerText = '+0 Poin';
    }

    if (myStreak >= 2) {
      streakText.innerText = `Streak 🔥 ${myStreak} Berturut-turut!`;
      streakText.style.display = 'block';
    } else {
      streakText.style.display = 'none';
    }

    rankText.innerText = `Peringkat #${msg.rank} | Total Poin: ${myScore.toLocaleString()}`;
  } else {
    // Poll / Word Cloud
    banner.className = 'feedback-banner feedback-correct';
    title.innerText = 'Terima kasih atas partisipasimu! 🙌';
    scoreGain.innerText = 'Respons Dicatat';
    streakText.style.display = 'none';
    rankText.innerText = 'Lihat hasil bersama di layar proyektor host';
  }
}

// === SCREEN: LEADERBOARD SYNC ===
function showPlayerLeaderboard(msg) {
  document.getElementById('feedback-title').innerText = 'Klasemen Sementara 📊';
  document.getElementById('feedback-rank').innerText = `Peringkat Kamu: #${msg.rank} (${msg.score.toLocaleString()} pts)`;
}

// === SCREEN: PODIUM / GAME OVER ===
function showPlayerPodium(msg) {
  document.getElementById('screen-feedback').style.display = 'none';
  document.getElementById('screen-final').style.display = 'flex';

  const myRecord = (msg.rankings || []).find(p => p.id === myPlayerId);
  const finalRank = myRecord ? myRecord.rank : '-';
  const finalScore = myRecord ? myRecord.score : myScore;

  document.getElementById('final-rank-display').innerText = `#${finalRank}`;
  document.getElementById('final-score-display').innerText = `${finalScore.toLocaleString()} Poin`;

  if (finalRank === 1) {
    document.getElementById('final-congrats').innerText = '🏆 SELAMAT! KAMU JUARA 1!';
    confetti.shoot(200);
  } else if (finalRank <= 3) {
    document.getElementById('final-congrats').innerText = '🎉 Hebat! Kamu Masuk Podium 3 Besar!';
    confetti.shoot(100);
  } else {
    document.getElementById('final-congrats').innerText = 'Permainan yang bagus! Terima kasih sudah berpartisipasi.';
  }
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
