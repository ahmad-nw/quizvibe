// Quiz & Presentation Studio Creator
let currentQuiz = {
  id: '',
  title: 'Kuis Kustom Baru',
  description: 'Dibuat dengan QuizVibe Studio',
  icon: '🎯',
  category: 'Umum',
  slides: []
};

let activeSlideIndex = 0;
let ws = null;

function init() {
  connectWebSocket();
  checkEditParam();
}

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Creator WebSocket connected");
    loadQuizList();
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'quizzes_list') {
      renderSavedQuizzes(data.quizzes);
    } else if (data.type === 'quiz_detail') {
      if (data.quiz) {
        currentQuiz = data.quiz;
        activeSlideIndex = 0;
        renderStudio();
      }
    } else if (data.type === 'quiz_saved') {
      alert("✅ " + data.message);
      currentQuiz.id = data.id;
      loadQuizList();
    } else if (data.type === 'quiz_deleted') {
      alert("🗑️ Kuis berhasil dihapus.");
      loadQuizList();
    }
  };
}

function loadQuizList() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: "get_quizzes" }));
  }
}

function checkEditParam() {
  const params = new URLSearchParams(window.location.search);
  const qid = params.get('id');
  if (qid) {
    setTimeout(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "get_quiz", id: qid }));
      }
    }, 500);
  } else {
    // Start with 1 default slide
    addSlide('quiz');
  }
}

function renderStudio() {
  document.getElementById('quiz-title-input').value = currentQuiz.title;
  document.getElementById('quiz-desc-input').value = currentQuiz.description || '';
  document.getElementById('quiz-icon-input').value = currentQuiz.icon || '🎯';

  renderSlideList();
  renderSlideEditor();
}

function renderSlideList() {
  const listContainer = document.getElementById('slides-sidebar-list');
  listContainer.innerHTML = '';

  currentQuiz.slides.forEach((s, idx) => {
    const item = document.createElement('div');
    item.className = `slide-thumb-card ${idx === activeSlideIndex ? 'active' : ''}`;
    item.onclick = () => {
      activeSlideIndex = idx;
      renderStudio();
    };

    const typeIcons = {
      quiz: '🎯 Kuis',
      true_false: '⚖️ B/S',
      poll: '📊 Polling',
      word_cloud: '☁️ Word Cloud',
      qa: '💬 Q&A'
    };

    item.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.85rem; color:#94a3b8; margin-bottom:0.25rem;">
        <span>#${idx + 1} ${typeIcons[s.type] || s.type}</span>
        <button type="button" class="btn-delete-thumb" onclick="event.stopPropagation(); deleteSlide(${idx})">×</button>
      </div>
      <div style="font-weight:700; font-size:0.95rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
        ${escapeHtml(s.question || 'Pertanyaan Baru...')}
      </div>
    `;
    listContainer.appendChild(item);
  });
}

function renderSlideEditor() {
  const editor = document.getElementById('slide-editor-area');
  const slide = currentQuiz.slides[activeSlideIndex];

  if (!slide) {
    editor.innerHTML = '<p class="text-muted text-center">Belum ada slide. Klik "+ Tambah Slide" di sebelah kiri.</p>';
    return;
  }

  const type = slide.type;

  let optionsHtml = '';
  if (type === 'quiz' || type === 'poll') {
    optionsHtml = `
      <div class="mt-4">
        <label style="font-weight:700; margin-bottom:0.5rem; display:block;">Pilihan Jawaban (Beri centang pada jawaban yang benar):</label>
        <div style="display:flex; flex-direction:column; gap:0.75rem;">
          ${(slide.options || []).map((opt, oIdx) => `
            <div style="display:flex; align-items:center; gap:0.75rem; background:rgba(255,255,255,0.05); padding:0.6rem 1rem; border-radius:8px;">
              <input type="checkbox" ${opt.is_correct ? 'checked' : ''} onchange="toggleOptionCorrect(${oIdx}, this.checked)" style="width:20px; height:20px; accent-color:#10b981; cursor:pointer;" ${type === 'poll' ? 'disabled' : ''} />
              <input type="text" class="pin-input" style="font-size:1rem; padding:0.5rem; letter-spacing:0; margin:0; flex-grow:1;" value="${escapeHtml(opt.text)}" placeholder="Pilihan ${oIdx + 1}" oninput="updateOptionText(${oIdx}, this.value)" />
            </div>
          `).join('')}
        </div>
      </div>
    `;
  } else if (type === 'true_false') {
    optionsHtml = `
      <div class="mt-4">
        <label style="font-weight:700; margin-bottom:0.5rem; display:block;">Kunci Jawaban Benar / Salah:</label>
        <div style="display:flex; gap:1rem;">
          <button type="button" class="btn ${slide.options[0]?.is_correct ? 'btn-primary' : 'btn-outline'}" onclick="setTrueFalseAnswer(true)">
            ✔ BENAR
          </button>
          <button type="button" class="btn ${slide.options[1]?.is_correct ? 'btn-accent' : 'btn-outline'}" onclick="setTrueFalseAnswer(false)">
            ✖ SALAH
          </button>
        </div>
      </div>
    `;
  } else if (type === 'word_cloud') {
    optionsHtml = `
      <div class="mt-4" style="background:rgba(255,255,255,0.05); padding:1.25rem; border-radius:12px;">
        <h4>☁️ Fitur Mentimeter: Word Cloud</h4>
        <p class="text-muted mt-2">Peserta akan menginput 1-3 kata dari smartphone mereka. Kata yang paling sering disebut akan membesar secara dinamis di layar.</p>
      </div>
    `;
  } else if (type === 'qa') {
    optionsHtml = `
      <div class="mt-4" style="background:rgba(255,255,255,0.05); padding:1.25rem; border-radius:12px;">
        <h4>💬 Fitur Mentimeter: Live Q&A</h4>
        <p class="text-muted mt-2">Audiens dapat mengajukan pertanyaan bebas dan memberikan upvote secara real-time.</p>
      </div>
    `;
  }

  editor.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
      <h3>Edit Slide #${activeSlideIndex + 1}</h3>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <label style="font-size:0.9rem; color:#94a3b8;">Batas Waktu:</label>
        <select class="pin-input" style="width:auto; font-size:0.9rem; padding:0.4rem 0.8rem; margin:0;" onchange="updateSlideTime(this.value)">
          <option value="10" ${slide.time_limit == 10 ? 'selected' : ''}>10 Detik</option>
          <option value="15" ${slide.time_limit == 15 ? 'selected' : ''}>15 Detik</option>
          <option value="20" ${slide.time_limit == 20 ? 'selected' : ''}>20 Detik</option>
          <option value="30" ${slide.time_limit == 30 ? 'selected' : ''}>30 Detik</option>
          <option value="60" ${slide.time_limit == 60 ? 'selected' : ''}>60 Detik</option>
        </select>
      </div>
    </div>

    <div>
      <label style="font-weight:700; margin-bottom:0.5rem; display:block;">Teks Pertanyaan / Topik:</label>
      <input type="text" class="pin-input" style="font-size:1.3rem; letter-spacing:0; padding:0.8rem; text-align:left;" value="${escapeHtml(slide.question)}" placeholder="Ketik pertanyaan di sini..." oninput="updateSlideQuestion(this.value)" />
    </div>

    ${optionsHtml}
  `;
}

function addSlide(type) {
  let newSlide = {
    id: 's_' + Date.now(),
    type: type,
    question: type === 'word_cloud' ? 'Satu kata yang menggambarkan harimu?' : 'Pertanyaan baru...',
    time_limit: 20,
    points: 1000,
    options: []
  };

  if (type === 'quiz') {
    newSlide.options = [
      { text: 'Pilihan A', is_correct: true },
      { text: 'Pilihan B', is_correct: false },
      { text: 'Pilihan C', is_correct: false },
      { text: 'Pilihan D', is_correct: false }
    ];
  } else if (type === 'true_false') {
    newSlide.options = [
      { text: 'Benar', is_correct: true },
      { text: 'Salah', is_correct: false }
    ];
  } else if (type === 'poll') {
    newSlide.options = [
      { text: 'Opsi 1', is_correct: false },
      { text: 'Opsi 2', is_correct: false },
      { text: 'Opsi 3', is_correct: false }
    ];
  }

  currentQuiz.slides.push(newSlide);
  activeSlideIndex = currentQuiz.slides.length - 1;
  renderStudio();
}

function deleteSlide(idx) {
  if (currentQuiz.slides.length <= 1) {
    alert("Minimal kuis harus memiliki 1 slide!");
    return;
  }
  currentQuiz.slides.splice(idx, 1);
  if (activeSlideIndex >= currentQuiz.slides.length) {
    activeSlideIndex = currentQuiz.slides.length - 1;
  }
  renderStudio();
}

function updateSlideQuestion(val) {
  currentQuiz.slides[activeSlideIndex].question = val;
  renderSlideList();
}

function updateSlideTime(val) {
  currentQuiz.slides[activeSlideIndex].time_limit = parseInt(val);
}

function updateOptionText(optIdx, val) {
  currentQuiz.slides[activeSlideIndex].options[optIdx].text = val;
}

function toggleOptionCorrect(optIdx, isCorrect) {
  currentQuiz.slides[activeSlideIndex].options[optIdx].is_correct = isCorrect;
}

function setTrueFalseAnswer(isTrueCorrect) {
  const opts = currentQuiz.slides[activeSlideIndex].options;
  opts[0].is_correct = isTrueCorrect;
  opts[1].is_correct = !isTrueCorrect;
  renderSlideEditor();
}

function saveQuiz() {
  currentQuiz.title = document.getElementById('quiz-title-input').value.trim() || 'Kuis Tanpa Judul';
  currentQuiz.description = document.getElementById('quiz-desc-input').value.trim();
  currentQuiz.icon = document.getElementById('quiz-icon-input').value.trim() || '🎯';

  ws.send(JSON.stringify({
    type: "save_quiz",
    quiz: currentQuiz
  }));
}

function playQuizNow() {
  if (!currentQuiz.id) {
    // Save first
    currentQuiz.title = document.getElementById('quiz-title-input').value.trim() || 'Kuis Baru';
    currentQuiz.description = document.getElementById('quiz-desc-input').value.trim();
    currentQuiz.icon = document.getElementById('quiz-icon-input').value.trim() || '🎯';
    ws.send(JSON.stringify({
      type: "save_quiz",
      quiz: currentQuiz
    }));
  }
  // Redirect to host screen
  setTimeout(() => {
    window.location.href = `/host.html?quiz_id=${currentQuiz.id}`;
  }, 300);
}

function exportQuizJSON() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentQuiz, null, 2));
  const dlAnchorElem = document.createElement('a');
  dlAnchorElem.setAttribute("href", dataStr);
  dlAnchorElem.setAttribute("download", `${currentQuiz.title.replace(/\s+/g, '_')}.json`);
  dlAnchorElem.click();
}

function importQuizJSON(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const parsed = JSON.parse(e.target.result);
      if (parsed.slides && Array.isArray(parsed.slides)) {
        currentQuiz = parsed;
        currentQuiz.id = ''; // New ID on save
        activeSlideIndex = 0;
        renderStudio();
        alert("✅ Kuis berhasil diimpor!");
      } else {
        alert("Format JSON tidak valid!");
      }
    } catch (err) {
      alert("Gagal membaca file JSON!");
    }
  };
  reader.readAsText(file);
}

function renderSavedQuizzes(quizzes) {
  const list = document.getElementById('saved-quizzes-library');
  if (!list) return;
  list.innerHTML = '';

  quizzes.forEach(q => {
    const card = document.createElement('div');
    card.style.display = 'flex';
    card.style.justifyContent = 'space-between';
    card.style.alignItems = 'center';
    card.style.padding = '0.75rem';
    card.style.background = 'rgba(255,255,255,0.05)';
    card.style.borderRadius = '8px';
    card.style.marginBottom = '0.5rem';

    card.innerHTML = `
      <div>
        <div style="font-weight:700;">${q.icon} ${escapeHtml(q.title)}</div>
        <div style="font-size:0.8rem; color:#94a3b8;">${q.slide_count} Slide • ${q.category}</div>
      </div>
      <div style="display:flex; gap:0.4rem;">
        <button type="button" class="btn btn-outline" style="padding:0.3rem 0.6rem; font-size:0.85rem;" onclick="loadQuizForEdit('${q.id}')">Edit</button>
        <a href="/host.html?quiz_id=${q.id}" class="btn btn-primary" style="padding:0.3rem 0.6rem; font-size:0.85rem;">Play</a>
      </div>
    `;
    list.appendChild(card);
  });
}

function loadQuizForEdit(qid) {
  ws.send(JSON.stringify({ type: "get_quiz", id: qid }));
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
