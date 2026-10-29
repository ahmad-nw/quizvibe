import sqlite3
import json
import os
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "quizvibe.db")

DEFAULT_QUIZZES = [
    {
        "id": "quiz_trivia_indo",
        "title": "Kuis Seru: Pengetahuan Umum & Budaya",
        "description": "Kuis seru gaya Kahoot dengan beragam pertanyaan trivia budaya, geografi, dan keunikan Nusantara!",
        "icon": "🇮🇩",
        "category": "Trivia",
        "slides": [
            {
                "id": "s1",
                "type": "quiz",
                "question": "Pulau manakah di Indonesia yang terkenal sebagai habitat alami Komodo?",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "Pulau Bali", "is_correct": False},
                    {"text": "Pulau Komodo & Rinca", "is_correct": True},
                    {"text": "Pulau Madura", "is_correct": False},
                    {"text": "Pulau Bunaken", "is_correct": False}
                ]
            },
            {
                "id": "s2",
                "type": "true_false",
                "question": "Danau Toba di Sumatera Utara adalah danau vulkanik terbesar di dunia.",
                "time_limit": 15,
                "points": 1000,
                "options": [
                    {"text": "Benar", "is_correct": True},
                    {"text": "Salah", "is_correct": False}
                ]
            },
            {
                "id": "s3",
                "type": "quiz",
                "question": "Alat musik tradisional dari Jawa Barat yang terbuat dari bambu dan digoyangkan adalah...",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "Saluang", "is_correct": False},
                    {"text": "Sasando", "is_correct": False},
                    {"text": "Angklung", "is_correct": True},
                    {"text": "Kolintang", "is_correct": False}
                ]
            },
            {
                "id": "s4",
                "type": "word_cloud",
                "question": "Satu kata yang paling menggambarkan Indonesia menurut kamu?",
                "time_limit": 30,
                "options": []
            },
            {
                "id": "s5",
                "type": "quiz",
                "question": "Berapa jumlah warna pada lambang Olimpiade?",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "4 Warna", "is_correct": False},
                    {"text": "5 Warna", "is_correct": True},
                    {"text": "6 Warna", "is_correct": False},
                    {"text": "7 Warna", "is_correct": False}
                ]
            },
            {
                "id": "s6",
                "type": "poll",
                "question": "Makanan khas Nusantara mana yang paling jadi favoritmu saat lapar?",
                "time_limit": 25,
                "options": [
                    {"text": "Rendang Sapi Padang", "is_correct": False},
                    {"text": "Nasi Goreng Spesial", "is_correct": False},
                    {"text": "Sate Ayam Madura", "is_correct": False},
                    {"text": "Bakso Urat Malang", "is_correct": False}
                ]
            },
            {
                "id": "s7",
                "type": "quiz",
                "question": "Planet terdekat dari Matahari dalam tata surya kita adalah...",
                "time_limit": 15,
                "points": 1000,
                "options": [
                    {"text": "Venus", "is_correct": False},
                    {"text": "Mars", "is_correct": False},
                    {"text": "Merkurius", "is_correct": True},
                    {"text": "Bumi", "is_correct": False}
                ]
            }
        ]
    },
    {
        "id": "quiz_menti_workshop",
        "title": "Interactive Workshop & Icebreaker (Mentimeter Style)",
        "description": "Presentasi interaktif dengan Polling Langsung, Word Cloud, dan Tanya Jawab (Q&A).",
        "icon": "📊",
        "category": "Interaktif",
        "slides": [
            {
                "id": "m1",
                "type": "word_cloud",
                "question": "Bagaimana perasaan atau mood kamu hari ini? (Tulis 1 kata)",
                "time_limit": 35,
                "options": []
            },
            {
                "id": "m2",
                "type": "poll",
                "question": "Dari mana kamu mengikuti sesi pertemuan / workshop kali ini?",
                "time_limit": 30,
                "options": [
                    {"text": "Rumah (Work From Home)", "is_correct": False},
                    {"text": "Kantor / Sekolah / Kampus", "is_correct": False},
                    {"text": "Cafe / Tempat Nongkrong", "is_correct": False},
                    {"text": "Dalam Perjalanan", "is_correct": False}
                ]
            },
            {
                "id": "m3",
                "type": "poll",
                "question": "Topik apa yang paling ingin kamu pelajari lebih dalam?",
                "time_limit": 30,
                "options": [
                    {"text": "Artificial Intelligence & Otomasi", "is_correct": False},
                    {"text": "Fullstack Web & Mobile Development", "is_correct": False},
                    {"text": "UI/UX & Desain Produk Digital", "is_correct": False},
                    {"text": "Data Science & Analisis Bisnis", "is_correct": False}
                ]
            },
            {
                "id": "m4",
                "type": "word_cloud",
                "question": "Harapan atau goals terbesar kamu di tahun ini?",
                "time_limit": 40,
                "options": []
            },
            {
                "id": "m5",
                "type": "qa",
                "question": "Sesi Tanya Jawab Terbuka (Q&A): Ada pertanyaan untuk pemateri?",
                "time_limit": 60,
                "options": []
            }
        ]
    },
    {
        "id": "quiz_tech_coding",
        "title": "Tantangan Kuis: Dunia Coding & Teknologi",
        "description": "Uji wawasan seputar bahasa pemrograman, web development, dan sejarah teknologi!",
        "icon": "💻",
        "category": "Teknologi",
        "slides": [
            {
                "id": "t1",
                "type": "quiz",
                "question": "Bahasa pemrograman apa yang awalnya dibuat oleh Brendan Eich hanya dalam waktu 10 hari?",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "Python", "is_correct": False},
                    {"text": "JavaScript", "is_correct": True},
                    {"text": "Java", "is_correct": False},
                    {"text": "PHP", "is_correct": False}
                ]
            },
            {
                "id": "t2",
                "type": "true_false",
                "question": "HTML (HyperText Markup Language) adalah bahasa pemrograman.",
                "time_limit": 15,
                "points": 1000,
                "options": [
                    {"text": "Benar", "is_correct": False},
                    {"text": "Salah (HTML adalah Bahasa Markup)", "is_correct": True}
                ]
            },
            {
                "id": "t3",
                "type": "quiz",
                "question": "Protokol standar yang digunakan untuk komunikasi real-time dua arah secara persisten di browser adalah...",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "FTP", "is_correct": False},
                    {"text": "HTTP/1.0", "is_correct": False},
                    {"text": "WebSocket", "is_correct": True},
                    {"text": "SMTP", "is_correct": False}
                ]
            },
            {
                "id": "t4",
                "type": "word_cloud",
                "question": "Framework atau bahasa pemrograman favoritmu saat ini?",
                "time_limit": 30,
                "options": []
            },
            {
                "id": "t5",
                "type": "quiz",
                "question": "Apa kepanjangan dari singkatan 'CSS' dalam desain web?",
                "time_limit": 20,
                "points": 1000,
                "options": [
                    {"text": "Creative Style Sheets", "is_correct": False},
                    {"text": "Cascading Style Sheets", "is_correct": True},
                    {"text": "Computer System Sheets", "is_correct": False},
                    {"text": "Colorful Screen Sheets", "is_correct": False}
                ]
            }
        ]
    }
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- PASSWORD HASHING HELPER (Salted SHA-256) ---
def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split('$')
        check = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return secrets.compare_digest(hashed, check)
    except Exception:
        return False

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Quizzes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '🎯',
        category TEXT DEFAULT 'Umum',
        slides_json TEXT NOT NULL,
        user_id TEXT,
        custom_branding_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Check and migrate columns if older table exists
    cursor.execute("PRAGMA table_info(quizzes)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE quizzes ADD COLUMN user_id TEXT")
    if "custom_branding_json" not in columns:
        cursor.execute("ALTER TABLE quizzes ADD COLUMN custom_branding_json TEXT")

    # 2. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        subscription_tier TEXT DEFAULT 'free',
        organization TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. User Sessions Table (Tokens)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # 4. Game Sessions & Reports Table (For History & Excel/CSV Export)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        quiz_id TEXT,
        quiz_title TEXT NOT NULL,
        pin TEXT NOT NULL,
        player_count INTEGER DEFAULT 0,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        results_json TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed default quizzes if table is empty
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    count = cursor.fetchone()[0]
    if count == 0:
        for q in DEFAULT_QUIZZES:
            cursor.execute("""
            INSERT INTO quizzes (id, title, description, icon, category, slides_json, user_id)
            VALUES (?, ?, ?, ?, ?, ?, NULL)
            """, (
                q["id"],
                q["title"],
                q["description"],
                q.get("icon", "🎯"),
                q.get("category", "Umum"),
                json.dumps(q["slides"], ensure_ascii=False)
            ))
        conn.commit()

    # Seed demo host user if none exists
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        demo_user_id = "user_demo_1"
        cursor.execute("""
        INSERT INTO users (id, name, email, password_hash, role, subscription_tier, organization)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            demo_user_id,
            "Ahmad Organizer",
            "host@quizvibe.id",
            hash_password("admin123"),
            "host",
            "pro",
            "QuizVibe Event Organizer"
        ))
        conn.commit()

    conn.close()

# --- USER AUTHENTICATION & SESSIONS ---
def register_user(name, email, password, organization=None):
    conn = get_connection()
    cursor = conn.cursor()
    email_clean = email.strip().lower()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
    if cursor.fetchone():
        conn.close()
        return None, "Email sudah terdaftar! Silakan login."

    user_id = f"usr_{uuid.uuid4().hex[:10]}"
    p_hash = hash_password(password)

    cursor.execute("""
    INSERT INTO users (id, name, email, password_hash, role, subscription_tier, organization)
    VALUES (?, ?, ?, ?, 'host', 'free', ?)
    """, (user_id, name.strip(), email_clean, p_hash, organization))
    conn.commit()
    conn.close()

    token = create_user_session(user_id)
    return {"id": user_id, "name": name, "email": email_clean, "subscription_tier": "free", "token": token}, None

def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    email_clean = email.strip().lower()
    cursor.execute("SELECT id, name, email, password_hash, role, subscription_tier, organization FROM users WHERE email = ?", (email_clean,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None, "Email tidak ditemukan!"
    if not verify_password(password, row["password_hash"]):
        return None, "Password salah!"

    token = create_user_session(row["id"])
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "subscription_tier": row["subscription_tier"],
        "organization": row["organization"],
        "token": token
    }, None

def create_user_session(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    token = f"tk_{secrets.token_urlsafe(32)}"
    expires_at = datetime.now() + timedelta(days=30)

    cursor.execute("""
    INSERT INTO user_sessions (token, user_id, expires_at)
    VALUES (?, ?, ?)
    """, (token, user_id, expires_at.isoformat()))
    conn.commit()
    conn.close()
    return token

def get_user_by_token(token):
    if not token:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.name, u.email, u.role, u.subscription_tier, u.organization
    FROM user_sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.token = ? AND s.expires_at > ?
    """, (token, datetime.now().isoformat()))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def delete_user_session(token):
    if not token:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# --- QUIZZES MANAGEMENT ---
def get_all_quizzes(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        # User's own quizzes + default system templates
        cursor.execute("""
        SELECT id, title, description, icon, category, slides_json, user_id, custom_branding_json, created_at
        FROM quizzes
        WHERE user_id = ? OR user_id IS NULL
        ORDER BY created_at DESC
        """, (user_id,))
    else:
        cursor.execute("SELECT id, title, description, icon, category, slides_json, user_id, custom_branding_json, created_at FROM quizzes ORDER BY created_at DESC")

    rows = cursor.fetchall()
    quizzes = []
    for row in rows:
        slides = json.loads(row["slides_json"])
        branding = json.loads(row["custom_branding_json"]) if row["custom_branding_json"] else None
        quizzes.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "icon": row["icon"],
            "category": row["category"],
            "slides": slides,
            "slide_count": len(slides),
            "user_id": row["user_id"],
            "is_custom": bool(row["user_id"]),
            "custom_branding": branding,
            "created_at": row["created_at"]
        })
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, icon, category, slides_json, user_id, custom_branding_json, created_at FROM quizzes WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    branding = json.loads(row["custom_branding_json"]) if row["custom_branding_json"] else None
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "icon": row["icon"],
        "category": row["category"],
        "slides": json.loads(row["slides_json"]),
        "user_id": row["user_id"],
        "custom_branding": branding,
        "created_at": row["created_at"]
    }

def save_quiz(quiz_data, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    quiz_id = quiz_data.get("id") or str(uuid.uuid4())[:8]
    title = quiz_data.get("title", "Kuis Baru")
    desc = quiz_data.get("description", "")
    icon = quiz_data.get("icon", "🎯")
    category = quiz_data.get("category", "Umum")
    slides = quiz_data.get("slides", [])
    branding = quiz_data.get("custom_branding")

    cursor.execute("""
    INSERT INTO quizzes (id, title, description, icon, category, slides_json, user_id, custom_branding_json, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
        title=excluded.title,
        description=excluded.description,
        icon=excluded.icon,
        category=excluded.category,
        slides_json=excluded.slides_json,
        user_id=COALESCE(excluded.user_id, quizzes.user_id),
        custom_branding_json=excluded.custom_branding_json,
        updated_at=CURRENT_TIMESTAMP
    """, (
        quiz_id,
        title,
        desc,
        icon,
        category,
        json.dumps(slides, ensure_ascii=False),
        user_id,
        json.dumps(branding, ensure_ascii=False) if branding else None
    ))
    conn.commit()
    conn.close()
    return quiz_id

def delete_quiz(quiz_id, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("DELETE FROM quizzes WHERE id = ? AND user_id = ?", (quiz_id, user_id))
    else:
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    return True

# --- GAME SESSIONS & REPORTING (EXPORT EXCEL / CSV) ---
def save_game_session(session_data):
    conn = get_connection()
    cursor = conn.cursor()
    session_id = session_data.get("id") or f"sess_{secrets.token_hex(6)}"

    cursor.execute("""
    INSERT INTO game_sessions (id, user_id, quiz_id, quiz_title, pin, player_count, results_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        session_data.get("user_id"),
        session_data.get("quiz_id"),
        session_data.get("quiz_title", "Kuis"),
        session_data.get("pin", "000000"),
        session_data.get("player_count", 0),
        json.dumps(session_data.get("results", {}), ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    return session_id

def get_game_sessions(user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("""
        SELECT id, user_id, quiz_id, quiz_title, pin, player_count, started_at, results_json
        FROM game_sessions
        WHERE user_id = ? OR user_id IS NULL
        ORDER BY started_at DESC LIMIT 50
        """, (user_id,))
    else:
        cursor.execute("""
        SELECT id, user_id, quiz_id, quiz_title, pin, player_count, started_at, results_json
        FROM game_sessions
        ORDER BY started_at DESC LIMIT 50
        """)

    rows = cursor.fetchall()
    sessions = []
    for r in rows:
        res = json.loads(r["results_json"]) if r["results_json"] else {}
        podium = res.get("podium", [])
        winner = podium[0]["name"] if podium else "-"
        sessions.append({
            "id": r["id"],
            "quiz_id": r["quiz_id"],
            "quiz_title": r["quiz_title"],
            "pin": r["pin"],
            "player_count": r["player_count"],
            "started_at": r["started_at"],
            "winner": winner
        })
    conn.close()
    return sessions

def get_game_session_detail(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, user_id, quiz_id, quiz_title, pin, player_count, started_at, results_json
    FROM game_sessions
    WHERE id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "quiz_id": row["quiz_id"],
        "quiz_title": row["quiz_title"],
        "pin": row["pin"],
        "player_count": row["player_count"],
        "started_at": row["started_at"],
        "results": json.loads(row["results_json"]) if row["results_json"] else {}
    }

def generate_session_csv(session_id):
    session = get_game_session_detail(session_id)
    if not session:
        return None

    results = session.get("results", {})
    rankings = results.get("rankings", [])

    lines = []
    lines.append(f"LAPORAN HASIL SESI EVENT - QUIZVIBE PRO")
    lines.append(f"Judul Kuis: \"{session.get('quiz_title')}\"")
    lines.append(f"Game PIN: {session.get('pin')}")
    lines.append(f"Waktu Pelaksanaan: {session.get('started_at')}")
    lines.append(f"Total Peserta: {session.get('player_count')} Orang")
    lines.append("")
    lines.append("RANKING PESERTA:")
    lines.append("Peringkat,Nama Peserta,Avatar,Total Skor (Poin)")

    for idx, p in enumerate(rankings):
        rank = p.get("rank", idx + 1)
        name = p.get("name", "").replace('"', '""')
        avatar = p.get("avatar", "")
        score = p.get("score", 0)
        lines.append(f"{rank},\"{name}\",{avatar},{score}")

    lines.append("")
    lines.append("Generated by QuizVibe Pro Platform - https://quizvibe.id")
    return "\r\n".join(lines)

if __name__ == "__main__":
    init_db()
    print("Database upgraded successfully with Users, Sessions, and Reports tables!")
