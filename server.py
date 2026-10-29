import asyncio
import os
import sys
import json
import logging
import mimetypes
import urllib.parse
from http import HTTPStatus
import io
import socket
import websockets
import qrcode

import database
from game_manager import game_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("QuizVibeServer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure mime types
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("text/html; charset=utf-8", ".html")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("image/x-icon", ".ico")
mimetypes.add_type("application/json", ".json")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

async def process_http_request(path, headers):
    """
    Handle HTTP requests before WebSocket upgrade.
    If path starts with /ws, return None to trigger WebSocket upgrade.
    Otherwise, respond with HTTP status, headers, and body.
    """
    parsed = urllib.parse.urlparse(path)
    req_path = parsed.path
    query_params = urllib.parse.parse_qs(parsed.query)

    # Allow WebSocket upgrade on /ws or /socket
    if req_path in ["/ws", "/socket"]:
        return None

    # Favicon fallback
    if req_path in ["/favicon.ico", "/favicon.png"]:
        svg_icon = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">\xe2\x9a\xa1</text></svg>'
        return (
            HTTPStatus.OK,
            [
                ("Content-Type", "image/svg+xml"),
                ("Content-Length", str(len(svg_icon))),
                ("Cache-Control", "public, max-age=86400")
            ],
            svg_icon
        )

    # API: QR Code generator
    if req_path == "/api/qr":
        data = query_params.get("data", [""])[0]
        if not data:
            return (HTTPStatus.BAD_REQUEST, [("Content-Type", "text/plain")], b"Missing 'data' query parameter")
        
        try:
            qr = qrcode.QRCode(box_size=8, border=2)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#1E1B4B", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            body = buf.getvalue()
            return (
                HTTPStatus.OK,
                [
                    ("Content-Type", "image/png"),
                    ("Content-Length", str(len(body))),
                    ("Cache-Control", "public, max-age=3600"),
                    ("Access-Control-Allow-Origin", "*")
                ],
                body
            )
        except Exception as e:
            logger.error(f"Error generating QR: {e}")
            return (HTTPStatus.INTERNAL_SERVER_ERROR, [("Content-Type", "text/plain")], b"QR Generation Error")

    # API: Quizzes list (GET)
    if req_path == "/api/quizzes":
        quizzes = database.get_all_quizzes()
        body = json.dumps(quizzes, ensure_ascii=False).encode("utf-8")
        return (
            HTTPStatus.OK,
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Access-Control-Allow-Origin", "*")
            ],
            body
        )

    # API: Single Quiz (GET)
    if req_path == "/api/quiz":
        qid = query_params.get("id", [""])[0]
        quiz = database.get_quiz_by_id(qid)
        if not quiz:
            return (HTTPStatus.NOT_FOUND, [("Content-Type", "application/json")], b'{"error": "Quiz not found"}')
        body = json.dumps(quiz, ensure_ascii=False).encode("utf-8")
        return (
            HTTPStatus.OK,
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Access-Control-Allow-Origin", "*")
            ],
            body
        )

    # API: Server Info (Local IP & Port)
    if req_path == "/api/info":
        info = {
            "local_ip": get_local_ip(),
            "port": 8000,
            "name": "QuizVibe Platform",
            "version": "1.0.0"
        }
        body = json.dumps(info).encode("utf-8")
        return (
            HTTPStatus.OK,
            [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Access-Control-Allow-Origin", "*")
            ],
            body
        )

    # Clean Route Mapping with trailing-slash normalization
    clean_path = req_path.rstrip("/")
    if not clean_path:
        clean_path = "/"

    file_map = {
        "/": "index.html",
        "/host": "host.html",
        "/player": "player.html",
        "/creator": "creator.html"
    }

    rel_path = file_map.get(clean_path, req_path.lstrip("/"))
    target_file = os.path.normpath(os.path.join(STATIC_DIR, rel_path))

    # Security check: prevent directory traversal outside STATIC_DIR
    try:
        common = os.path.commonpath([STATIC_DIR, target_file])
        if common != STATIC_DIR:
            return (HTTPStatus.FORBIDDEN, [("Content-Type", "text/plain")], b"Access Denied")
    except ValueError:
        return (HTTPStatus.FORBIDDEN, [("Content-Type", "text/plain")], b"Access Denied")

    if not os.path.isfile(target_file):
        logger.warning(f"File not found: {req_path} -> {target_file}")
        return (HTTPStatus.NOT_FOUND, [("Content-Type", "text/html; charset=utf-8")], b"<h1>404 Not Found</h1>")

    # Read and serve file
    mime_type, _ = mimetypes.guess_type(target_file)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(target_file, "rb") as f:
        content = f.read()

    return (
        HTTPStatus.OK,
        [
            ("Content-Type", mime_type),
            ("Content-Length", str(len(content))),
            ("Cache-Control", "no-cache"),
            ("Access-Control-Allow-Origin", "*")
        ],
        content
    )

async def handle_ws(websocket):
    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            # --- HOST ACTIONS ---
            if msg_type == "create_room":
                quiz_id = data.get("quiz_id")
                quiz = None
                if quiz_id:
                    quiz = database.get_quiz_by_id(quiz_id)
                if not quiz:
                    quiz = data.get("quiz_data")
                if not quiz:
                    quizzes = database.get_all_quizzes()
                    quiz = quizzes[0] if quizzes else None

                if not quiz or not quiz.get("slides"):
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Kuis tidak ditemukan atau belum memiliki slide soal!"
                    }))
                    continue

                room = game_manager.create_room(quiz, websocket)
                await websocket.send(json.dumps({
                    "type": "room_created",
                    "pin": room.pin,
                    "quiz_title": quiz.get("title", "Kuis"),
                    "total_slides": len(room.slides)
                }))
                logger.info(f"Room {room.pin} created for quiz: {quiz.get('title')}")

            elif msg_type == "start_game":
                pin = data.get("pin")
                room = game_manager.get_room(pin)
                if room and room.host_ws == websocket:
                    await game_manager.start_game(room)

            elif msg_type == "next_slide":
                pin = data.get("pin")
                room = game_manager.get_room(pin)
                if room and room.host_ws == websocket:
                    await game_manager.next_slide(room)

            elif msg_type == "skip_timer":
                pin = data.get("pin")
                room = game_manager.get_room(pin)
                if room and room.host_ws == websocket:
                    await game_manager.reveal_results(room)

            elif msg_type == "show_leaderboard":
                pin = data.get("pin")
                room = game_manager.get_room(pin)
                if room and room.host_ws == websocket:
                    await game_manager.show_leaderboard(room)

            # --- PLAYER ACTIONS ---
            elif msg_type == "join_room":
                pin = str(data.get("pin", "")).strip()
                name = str(data.get("name", "")).strip() or "Pemain"
                avatar = data.get("avatar", "🦊")
                await game_manager.handle_join(pin, name, avatar, websocket)

            elif msg_type == "submit_answer":
                pin = data.get("pin")
                room = game_manager.get_room(pin)
                if room:
                    player_info = game_manager.ws_to_player.get(websocket)
                    if player_info:
                        _, p_id = player_info
                        player = room.players.get(p_id)
                        if player:
                            await game_manager.handle_submit_answer(room, player, data)

            elif msg_type == "upvote_qa":
                pin = data.get("pin")
                question_id = data.get("question_id")
                room = game_manager.get_room(pin)
                if room and question_id:
                    await game_manager.upvote_qa_question(room, question_id)

            # --- QUIZ STUDIO & MANAGEMENT ---
            elif msg_type == "get_quizzes":
                quizzes = database.get_all_quizzes()
                await websocket.send(json.dumps({
                    "type": "quizzes_list",
                    "quizzes": quizzes
                }, ensure_ascii=False))

            elif msg_type == "get_quiz":
                qid = data.get("id")
                quiz = database.get_quiz_by_id(qid)
                await websocket.send(json.dumps({
                    "type": "quiz_detail",
                    "quiz": quiz
                }, ensure_ascii=False))

            elif msg_type == "save_quiz":
                quiz_data = data.get("quiz")
                if quiz_data:
                    saved_id = database.save_quiz(quiz_data)
                    await websocket.send(json.dumps({
                        "type": "quiz_saved",
                        "id": saved_id,
                        "message": "Kuis berhasil disimpan!"
                    }))

            elif msg_type == "delete_quiz":
                qid = data.get("id")
                if qid:
                    database.delete_quiz(qid)
                    await websocket.send(json.dumps({
                        "type": "quiz_deleted",
                        "id": qid
                    }))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        await game_manager.handle_disconnect(websocket)

async def main():
    database.init_db()
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"

    local_ip = get_local_ip()

    server = await websockets.serve(
        handle_ws,
        host,
        port,
        process_request=process_http_request,
        ping_interval=20,
        ping_timeout=30,
        max_size=10 * 1024 * 1024
    )

    print("=" * 65)
    print("🚀  QUIZVIBE PLATFORM (Kahoot + Mentimeter Clone)")
    print("=" * 65)
    print(f"👉 Local Access:   http://localhost:{port}/")
    print(f"👉 Presenter Mode: http://localhost:{port}/host.html")
    print(f"👉 Player Join:    http://localhost:{port}/player.html")
    print(f"👉 Quiz Studio:    http://localhost:{port}/creator.html")
    if local_ip != "127.0.0.1":
        print(f"📱 LAN Smartphone: http://{local_ip}:{port}/player.html")
    print("=" * 65)
    print("Server siap menerima koneksi HTTP dan WebSocket!")
    print("=" * 65)

    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
