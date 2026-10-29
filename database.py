import sqlite3
import json
import os
import uuid

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

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '🎯',
        category TEXT DEFAULT 'Umum',
        slides_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Seed default quizzes if table is empty
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    count = cursor.fetchone()[0]
    if count == 0:
        for q in DEFAULT_QUIZZES:
            cursor.execute("""
            INSERT INTO quizzes (id, title, description, icon, category, slides_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                q["id"],
                q["title"],
                q["description"],
                q.get("icon", "🎯"),
                q.get("category", "Umum"),
                json.dumps(q["slides"], ensure_ascii=False)
            ))
        conn.commit()
    conn.close()

def get_all_quizzes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, icon, category, slides_json, created_at FROM quizzes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    quizzes = []
    for row in rows:
        quizzes.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "icon": row["icon"],
            "category": row["category"],
            "slides": json.loads(row["slides_json"]),
            "slide_count": len(json.loads(row["slides_json"])),
            "created_at": row["created_at"]
        })
    conn.close()
    return quizzes

def get_quiz_by_id(quiz_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, icon, category, slides_json, created_at FROM quizzes WHERE id = ?", (quiz_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "icon": row["icon"],
        "category": row["category"],
        "slides": json.loads(row["slides_json"]),
        "created_at": row["created_at"]
    }

def save_quiz(quiz_data):
    conn = get_connection()
    cursor = conn.cursor()
    quiz_id = quiz_data.get("id") or str(uuid.uuid4())[:8]
    title = quiz_data.get("title", "Kuis Baru")
    desc = quiz_data.get("description", "")
    icon = quiz_data.get("icon", "🎯")
    category = quiz_data.get("category", "Umum")
    slides = quiz_data.get("slides", [])

    cursor.execute("""
    INSERT INTO quizzes (id, title, description, icon, category, slides_json, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(id) DO UPDATE SET
        title=excluded.title,
        description=excluded.description,
        icon=excluded.icon,
        category=excluded.category,
        slides_json=excluded.slides_json,
        updated_at=CURRENT_TIMESTAMP
    """, (
        quiz_id,
        title,
        desc,
        icon,
        category,
        json.dumps(slides, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    return quiz_id

def delete_quiz(quiz_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with default quizzes!")
