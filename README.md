# ⚡ QuizVibe - Platform Kuis & Presentasi Interaktif Real-Time
> **Kombinasi Terbaik Fitur Kahoot & Mentimeter dalam Satu Web App Modern**

QuizVibe adalah aplikasi web interaktif real-time yang memadukan keseruan kuis kompetitif berbasis kecepatan dan skor ala **Kahoot!**, dengan fitur presentasi audiens, awan kata (*Word Cloud*), jajak pendapat (*Live Polling*), dan sesi tanya jawab (*Q&A*) ala **Mentimeter**.

Aplikasi ini dibangun menggunakan **Python 3 (WebSockets & SQLite)** untuk backend berkecepatan tinggi dan **Vanilla HTML5, CSS3, dan Modern JavaScript (ES6+)** untuk frontend tanpa dependensi luar yang rumit, sehingga dapat langsung dijalankan di komputer lokal maupun jaringan LAN / Wi-Fi.

---

## 🌟 Fitur Utama

### 1. 🎯 Fitur Ala Kahoot! (Kuis & Kompetisi Cepat)
* **4 Tombol Warna & Bentuk Geometris Ikonik**:
  * Merah (▲ Segitiga)
  * Biru (◆ Wajik / Belah Ketupat)
  * Kuning (● Lingkaran)
  * Hijau (■ Persegi)
* **Format Soal Variatif**:
  * Pilihan Ganda (2 s/d 4 opsi)
  * Benar atau Salah (*True or False*)
* **Scoring Berbasis Kecepatan**:
  * Semakin cepat peserta menjawab dengan benar, semakin tinggi poin yang didapat (hingga 1.000 poin/soal).
* **Streak Bonus**:
  * Poin ekstra untuk peserta yang berhasil menjawab benar berturut-turut (🔥 *2+ Streak*).
* **Klasemen & Peringkat Real-Time (*Leaderboard*)**:
  * Menampilkan 5 besar peserta teratas dengan indikator kenaikan peringkat.
* **Podium 3D Juara & Hujan Konfeti**:
  * Animasi pedestal juara 1 (Emas 🥇), juara 2 (Perak 🥈), dan juara 3 (Perunggu 🥉) disertai semburan konfeti kanvas dan lagu kemenangan.
* **Web Audio API Synthesizer (Tanpa Perlu File MP3)**:
  * Musik tema lobby santai, efek *tick* detik waktu, bunyi *arpeggio* jawaban benar, bunyi dengung jawaban salah, gong waktu habis, dan *fanfare* podium juara.

### 2. 📊 Fitur Ala Mentimeter (Presentasi, Polling & Brainstorming)
* **Awan Kata Dinamis (*Live Word Cloud*)**:
  * Peserta mengetikkan kata atau perasaan mereka dari smartphone.
  * Kata yang paling sering disebut otomatis membesar dan ditata rapi secara animasi di kanvas layar presenter.
* **Polling Opini Langsung (*Live Survey/Poll*)**:
  * Audiens memilih opsi tanpa jawaban benar/salah.
  * Diagram batang (*bar chart*) animasi bergerak naik secara dinamis begitu ada suara masuk.
* **Sesi Tanya Jawab (*Live Q&A*)**:
  * Peserta dapat mengajukan pertanyaan secara langsung.
  * Peserta lain dapat memberikan *upvote* (jempol) sehingga pertanyaan paling penting berada di urutan teratas.

### 3. 📱 Pengalaman Peserta (*Mobile & Tablet First*)
* **Scan QR Code & Auto-Join**:
  * Peserta cukup mengarahkan kamera HP ke QR Code yang terpampang di layar host untuk langsung masuk tanpa perlu mengetik URL.
* **16 Karakter Avatar Emoji Interaktif**:
  * Peserta bebas memilih avatar (🦊, 🦁, 🐼, 🚀, ⚡, 🍕, 👑, 🎯, dll.) dan memasukkan nama panggilan (*nickname*).
* **Getaran Taktil Smartphone**:
  * Efek getar (*haptic feedback*) saat menekan tombol jawaban di perangkat mobile.

### 4. 🛠️ Quiz & Presentation Studio (Pembuat Kuis)
* Editor visual intuitif untuk menambah, menyusun ulang, dan mengedit slide kuis.
* Pengaturan batas waktu (10 detik, 15 detik, 20 detik, 30 detik, 60 detik).
* Ekspor dan Impor paket kuis dalam format `.json` untuk dibagikan ke pengguna lain.
* Tersedia 3 paket kuis bawaan siap main:
  1. *Kuis Seru: Pengetahuan Umum & Budaya Nusantara* (Trivia gaya Kahoot)
  2. *Interactive Workshop & Icebreaker* (Polling, Word Cloud & Q&A gaya Mentimeter)
  3. *Tantangan Kuis: Dunia Coding & Teknologi* (Trivia pemrograman)

---

## 🚀 Cara Menjalankan Aplikasi

Pastikan Python 3 sudah terpasang di komputer Anda.

### 1. Jalankan Server
Buka terminal pada folder proyek ini, lalu ketik perintah:

```bash
python3 server.py
```

Server akan langsung aktif dan menampilkan informasi berikut:
```text
=================================================================
🚀  QUIZVIBE PLATFORM (Kahoot + Mentimeter Clone)
=================================================================
👉 Local Access:   http://localhost:8000/
👉 Presenter Mode: http://localhost:8000/host.html
👉 Player Join:    http://localhost:8000/player.html
👉 Quiz Studio:    http://localhost:8000/creator.html
📱 LAN Smartphone: http://192.168.x.x:8000/player.html
=================================================================
Server siap menerima koneksi HTTP dan WebSocket!
=================================================================
```

### 2. Membuka Halaman di Browser
* **Beranda / Halaman Utama**: Buka [http://localhost:8000/](http://localhost:8000/)
* **Host / Layar Proyektor**: Buka [http://localhost:8000/host.html](http://localhost:8000/host.html) (atau klik tombol **Mulai Host** di salah satu kuis).
* **Pemain / Peserta**: Buka [http://localhost:8000/player.html](http://localhost:8000/player.html) pada browser laptop atau smartphone di jaringan Wi-Fi yang sama, masukkan **Game PIN** yang tampil di layar Host.
* **Studio Pembuat Kuis**: Buka [http://localhost:8000/creator.html](http://localhost:8000/creator.html) untuk membuat atau mengedit kuis Anda sendiri.

---

## 📁 Struktur Berkas

```
.
├── server.py              # Server asynchronous tunggal (HTTP static, REST API, & WebSocket)
├── database.py            # Manajemen database SQLite & default seed quizzes
├── game_manager.py        # Logika room, peserta, timer, penilaian Kahoot, & state machine
├── quizvibe.db            # Database SQLite lokal
├── static/                # Aset frontend
│   ├── css/
│   │   └── style.css      # Desain modern, tema warna Kahoot & animasi responsif
│   ├── js/
│   │   ├── sound.js       # Synthesizer audio Web Audio API (Lobby, Chime, Fanfare)
│   │   ├── confetti.js    # Mesin partikel konfeti kanvas untuk perayaan podium
│   │   ├── wordcloud.js   # Renderer awan kata kanvas dinamis (gaya Mentimeter)
│   │   ├── host.js        # Logika presenter/host kuis & kendali slide
│   │   ├── player.js      # Logika peserta di smartphone / browser
│   │   └── creator.js     # Logika studio pembuat kuis kustom
│   ├── index.html         # Halaman beranda & etalase kuis
│   ├── host.html          # Layar presenter / proyektor
│   ├── player.html        # Antarmuka peserta / smartphone
│   └── creator.html       # Studio pembuat kuis & polling
└── README.md              # Dokumentasi lengkap
```

---

## 💡 Tombol Pintasan Keyboard untuk Host
* **Spasi / Spacebar**: Lanjut ke tahap berikutnya (Buka klasemen / Lanjut ke soal berikutnya).
* **F11**: Masuk atau keluar dari mode layar penuh (*Fullscreen*).
* **Tombol Audio**: Menyalakan atau mematikan suara background synthesizer kuis.
