import time
import random
import asyncio
import json
import logging

logger = logging.getLogger("GameManager")

class Player:
    def __init__(self, player_id, name, avatar, websocket):
        self.id = player_id
        self.name = name
        self.avatar = avatar
        self.websocket = websocket
        self.score = 0
        self.streak = 0
        self.last_score_gain = 0
        self.has_answered = False
        self.last_answer = None
        self.is_correct = False
        self.previous_rank = 0
        self.current_rank = 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "score": self.score,
            "streak": self.streak,
            "has_answered": self.has_answered,
            "last_score_gain": self.last_score_gain,
            "is_correct": self.is_correct,
            "rank": self.current_rank
        }

class GameRoom:
    def __init__(self, pin, quiz, host_ws, host_user_id=None):
        self.pin = pin
        self.quiz = quiz
        self.host_user_id = host_user_id or quiz.get("user_id")
        self.slides = quiz.get("slides", [])
        self.host_ws = host_ws
        self.players = {}  # player_id -> Player
        self.state = "LOBBY"  # LOBBY, QUESTION, RESULT, LEADERBOARD, PODIUM
        self.current_slide_index = -1
        self.question_start_time = 0
        self.time_limit = 20
        self.answers_tally = {}  # option_index -> count
        self.word_cloud_tally = {}  # word -> count
        self.qa_questions = []  # list of {id, author, text, votes, is_answered}
        self.timer_task = None

    def get_current_slide(self):
        if 0 <= self.current_slide_index < len(self.slides):
            return self.slides[self.current_slide_index]
        return None

    def update_ranks(self):
        # Sort players by score descending
        sorted_players = sorted(self.players.values(), key=lambda p: p.score, reverse=True)
        for idx, p in enumerate(sorted_players):
            p.previous_rank = p.current_rank if p.current_rank > 0 else idx + 1
            p.current_rank = idx + 1

    def get_leaderboard(self, top_n=10):
        self.update_ranks()
        sorted_players = sorted(self.players.values(), key=lambda p: p.score, reverse=True)
        return [
            {
                "id": p.id,
                "name": p.name,
                "avatar": p.avatar,
                "score": p.score,
                "streak": p.streak,
                "rank": p.current_rank,
                "rank_delta": p.previous_rank - p.current_rank  # positive means moved up
            }
            for p in sorted_players[:top_n]
        ]

    def reset_slide_answers(self):
        self.answers_tally = {}
        self.word_cloud_tally = {}
        for p in self.players.values():
            p.has_answered = False
            p.last_answer = None
            p.last_score_gain = 0
            p.is_correct = False

class GameManager:
    def __init__(self):
        self.rooms = {}  # pin -> GameRoom
        self.ws_to_player = {}  # ws -> (pin, player_id)
        self.ws_to_host = {}  # ws -> pin

    def generate_unique_pin(self):
        while True:
            pin = f"{random.randint(100000, 999999)}"
            if pin not in self.rooms:
                return pin

    def create_room(self, quiz, host_ws, host_user_id=None):
        pin = self.generate_unique_pin()
        room = GameRoom(pin, quiz, host_ws, host_user_id)
        self.rooms[pin] = room
        self.ws_to_host[host_ws] = pin
        return room

    def get_room(self, pin):
        return self.rooms.get(pin)

    async def broadcast_to_room(self, room, message):
        msg_str = json.dumps(message, ensure_ascii=False)
        targets = []
        if room.host_ws:
            targets.append(room.host_ws)
        for p in room.players.values():
            if p.websocket:
                targets.append(p.websocket)

        for ws in targets:
            try:
                await ws.send(msg_str)
            except Exception as e:
                logger.debug(f"Broadcast error: {e}")

    async def send_to_host(self, room, message):
        if room.host_ws:
            try:
                await room.host_ws.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.debug(f"Host send error: {e}")

    async def send_to_player(self, player, message):
        if player.websocket:
            try:
                await player.websocket.send(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.debug(f"Player send error: {e}")

    async def handle_join(self, pin, player_name, avatar, websocket):
        room = self.get_room(pin)
        if not room:
            await websocket.send(json.dumps({"type": "error", "message": "Kode PIN Game tidak ditemukan!"}))
            return None

        if room.state != "LOBBY":
            # Allow reconnect if player name exists
            existing_player = None
            for p in room.players.values():
                if p.name.lower() == player_name.strip().lower():
                    existing_player = p
                    break
            if not existing_player:
                await websocket.send(json.dumps({"type": "error", "message": "Game sudah dimulai! Tidak dapat bergabung baru."}))
                return None
            else:
                existing_player.websocket = websocket
                self.ws_to_player[websocket] = (pin, existing_player.id)
                # Send current state
                await self.send_sync_state_to_player(room, existing_player)
                return existing_player

        player_id = f"p_{random.randint(10000, 99999)}"
        player = Player(player_id, player_name.strip()[:20], avatar, websocket)
        room.players[player_id] = player
        self.ws_to_player[websocket] = (pin, player_id)

        # Notify player of success
        await websocket.send(json.dumps({
            "type": "joined_success",
            "pin": pin,
            "player": player.to_dict(),
            "quiz_title": room.quiz.get("title", "Kuis"),
            "total_slides": len(room.slides)
        }))

        # Notify host of new player
        await self.send_to_host(room, {
            "type": "player_joined",
            "player": player.to_dict(),
            "total_players": len(room.players),
            "players": [p.to_dict() for p in room.players.values()]
        })

        return player

    async def send_sync_state_to_player(self, room, player):
        slide = room.get_current_slide()
        data = {
            "type": "sync_state",
            "state": room.state,
            "current_slide_index": room.current_slide_index,
            "total_slides": len(room.slides),
            "player": player.to_dict()
        }
        if slide and room.state == "QUESTION":
            time_left = max(0, int(room.time_limit - (time.time() - room.question_start_time)))
            data["slide"] = {
                "type": slide.get("type", "quiz"),
                "question": slide.get("question", ""),
                "time_limit": room.time_limit,
                "time_left": time_left,
                "options": [{"text": opt.get("text", "")} for opt in slide.get("options", [])]
            }
        await self.send_to_player(player, data)

    async def start_game(self, room):
        if not room.slides:
            await self.send_to_host(room, {"type": "error", "message": "Kuis belum memiliki soal!"})
            return
        await self.next_slide(room)

    async def next_slide(self, room):
        # Cancel any pending timer
        if room.timer_task and not room.timer_task.done():
            room.timer_task.cancel()

        room.current_slide_index += 1
        if room.current_slide_index >= len(room.slides):
            # All slides completed -> PODIUM
            await self.show_podium(room)
            return

        slide = room.get_current_slide()
        room.state = "QUESTION"
        room.reset_slide_answers()
        room.time_limit = slide.get("time_limit", 20)
        room.question_start_time = time.time()

        slide_type = slide.get("type", "quiz")

        # Sanitize options for players (hide is_correct)
        safe_options = [
            {"index": idx, "text": opt.get("text", "")}
            for idx, opt in enumerate(slide.get("options", []))
        ]

        # Host payload
        host_msg = {
            "type": "question_started",
            "slide_index": room.current_slide_index,
            "total_slides": len(room.slides),
            "slide": {
                "type": slide_type,
                "question": slide.get("question", ""),
                "time_limit": room.time_limit,
                "options": safe_options,
                "correct_index": next((i for i, opt in enumerate(slide.get("options", [])) if opt.get("is_correct")), None)
            },
            "total_players": len(room.players)
        }
        await self.send_to_host(room, host_msg)

        # Player payload
        player_msg = {
            "type": "question_started",
            "slide_index": room.current_slide_index,
            "total_slides": len(room.slides),
            "slide": {
                "type": slide_type,
                "question": slide.get("question", ""),
                "time_limit": room.time_limit,
                "options": safe_options
            }
        }
        for p in room.players.values():
            await self.send_to_player(p, player_msg)

        # Start server-side countdown timer task
        room.timer_task = asyncio.create_task(self.run_timer(room, room.time_limit))

    async def run_timer(self, room, seconds):
        try:
            for remaining in range(seconds, 0, -1):
                await asyncio.sleep(1)
                # Broadcast tick every second
                tick_msg = {"type": "timer_tick", "time_left": remaining - 1}
                await self.broadcast_to_room(room, tick_msg)

            # Timer expired: automatically reveal results
            await self.reveal_results(room)
        except asyncio.CancelledError:
            pass

    async def handle_submit_answer(self, room, player, payload):
        if room.state != "QUESTION":
            return
        if player.has_answered:
            return  # Already answered

        slide = room.get_current_slide()
        if not slide:
            return

        slide_type = slide.get("type", "quiz")
        player.has_answered = True
        elapsed = max(0.1, time.time() - room.question_start_time)

        if slide_type in ["quiz", "true_false"]:
            choice = payload.get("choice")
            player.last_answer = choice
            room.answers_tally[choice] = room.answers_tally.get(choice, 0) + 1

            # Check correctness
            options = slide.get("options", [])
            max_points = slide.get("points", 1000)
            is_correct = False
            if 0 <= choice < len(options) and options[choice].get("is_correct", False):
                is_correct = True

            player.is_correct = is_correct

            if is_correct:
                player.streak += 1
                # Kahoot score calculation: faster = more points
                # Base formula: 500 to 1000 depending on time elapsed
                time_ratio = min(1.0, elapsed / room.time_limit)
                score_gain = int(max_points * (1 - (time_ratio / 2)))
                # Streak bonus: up to +250
                streak_bonus = min(player.streak - 1, 5) * 50
                total_gain = score_gain + streak_bonus
                player.last_score_gain = total_gain
                player.score += total_gain
            else:
                player.streak = 0
                player.last_score_gain = 0

            # Instant feedback to player (answer locked in)
            await self.send_to_player(player, {
                "type": "answer_received",
                "choice": choice
            })

        elif slide_type == "poll":
            choice = payload.get("choice")
            player.last_answer = choice
            room.answers_tally[choice] = room.answers_tally.get(choice, 0) + 1
            await self.send_to_player(player, {
                "type": "answer_received",
                "choice": choice
            })

        elif slide_type == "word_cloud":
            words = payload.get("words", [])
            if isinstance(words, str):
                words = [words]
            for w in words:
                cleaned = w.strip().lower()
                if cleaned:
                    room.word_cloud_tally[cleaned] = room.word_cloud_tally.get(cleaned, 0) + 1

            await self.send_to_player(player, {
                "type": "word_submitted",
                "status": "ok"
            })

        elif slide_type == "qa":
            question_text = payload.get("text", "").strip()
            if question_text:
                q_id = f"q_{len(room.qa_questions) + 1}"
                q_item = {
                    "id": q_id,
                    "author": player.name,
                    "avatar": player.avatar,
                    "text": question_text,
                    "votes": 0,
                    "is_answered": False
                }
                room.qa_questions.append(q_item)
                await self.broadcast_to_room(room, {
                    "type": "qa_list_updated",
                    "questions": room.qa_questions
                })

        # Update Host on answer counts in real-time
        answered_count = sum(1 for p in room.players.values() if p.has_answered)
        await self.send_to_host(room, {
            "type": "answer_count_updated",
            "answered_count": answered_count,
            "total_players": len(room.players),
            "answers_tally": room.answers_tally,
            "word_cloud_tally": room.word_cloud_tally
        })

        # If it's a word cloud or poll, broadcast live tally update to host!
        if slide_type in ["poll", "word_cloud"]:
            await self.send_to_host(room, {
                "type": "live_tally_update",
                "answers_tally": room.answers_tally,
                "word_cloud_tally": room.word_cloud_tally
            })

        # If everyone has answered in quiz/poll mode, auto reveal after 0.5s!
        if slide_type in ["quiz", "true_false", "poll"] and answered_count >= len(room.players) and len(room.players) > 0:
            if room.timer_task and not room.timer_task.done():
                room.timer_task.cancel()
            await asyncio.sleep(0.5)
            await self.reveal_results(room)

    async def reveal_results(self, room):
        if room.state != "QUESTION":
            return

        if room.timer_task and not room.timer_task.done():
            room.timer_task.cancel()

        room.state = "RESULT"
        slide = room.get_current_slide()
        if not slide:
            return

        slide_type = slide.get("type", "quiz")
        options = slide.get("options", [])
        correct_index = next((i for i, opt in enumerate(options) if opt.get("is_correct")), None)

        room.update_ranks()

        # Host results payload
        host_msg = {
            "type": "results_revealed",
            "slide_type": slide_type,
            "correct_index": correct_index,
            "answers_tally": room.answers_tally,
            "word_cloud_tally": room.word_cloud_tally,
            "qa_questions": room.qa_questions,
            "total_players": len(room.players),
            "options": [{"text": opt.get("text", "")} for opt in options]
        }
        await self.send_to_host(room, host_msg)

        # Player results payload
        for p in room.players.values():
            player_res = {
                "type": "results_revealed",
                "slide_type": slide_type,
                "correct_index": correct_index,
                "is_correct": p.is_correct if p.has_answered else False,
                "has_answered": p.has_answered,
                "last_score_gain": p.last_score_gain,
                "total_score": p.score,
                "streak": p.streak,
                "rank": p.current_rank,
                "rank_delta": p.previous_rank - p.current_rank
            }
            await self.send_to_player(p, player_res)

    async def show_leaderboard(self, room):
        room.state = "LEADERBOARD"
        leaderboard = room.get_leaderboard(top_n=5)

        msg = {
            "type": "leaderboard_revealed",
            "leaderboard": leaderboard,
            "slide_index": room.current_slide_index,
            "total_slides": len(room.slides),
            "is_last_slide": (room.current_slide_index >= len(room.slides) - 1)
        }
        await self.send_to_host(room, msg)

        for p in room.players.values():
            await self.send_to_player(p, {
                "type": "leaderboard_revealed",
                "rank": p.current_rank,
                "score": p.score,
                "streak": p.streak
            })

    async def show_podium(self, room):
        room.state = "PODIUM"
        room.update_ranks()
        sorted_players = sorted(self.players_of(room), key=lambda p: p.score, reverse=True)
        top3 = [p.to_dict() for p in sorted_players[:3]]
        all_rankings = [p.to_dict() for p in sorted_players]

        # Automatically persist session report to database
        import database
        session_id = f"sess_{room.pin}_{int(time.time())}"
        try:
            database.save_game_session({
                "id": session_id,
                "user_id": room.host_user_id or room.quiz.get("user_id"),
                "quiz_id": room.quiz.get("id"),
                "quiz_title": room.quiz.get("title", "Kuis Selesai"),
                "pin": room.pin,
                "player_count": len(sorted_players),
                "results": {
                    "podium": top3,
                    "rankings": all_rankings,
                    "answers_tally": room.answers_tally,
                    "word_cloud_tally": room.word_cloud_tally,
                    "qa_questions": room.qa_questions
                }
            })
            logger.info(f"Game session {session_id} saved successfully to database!")
        except Exception as e:
            logger.error(f"Error saving game session: {e}")

        msg = {
            "type": "game_over_podium",
            "session_id": session_id,
            "podium": top3,
            "rankings": all_rankings,
            "total_players": len(sorted_players),
            "quiz_title": room.quiz.get("title", "Kuis Selesai")
        }
        await self.broadcast_to_room(room, msg)

    async def upvote_qa_question(self, room, question_id):
        for q in room.qa_questions:
            if q["id"] == question_id:
                q["votes"] += 1
                break
        # Sort questions by votes descending
        room.qa_questions.sort(key=lambda x: x["votes"], reverse=True)
        await self.broadcast_to_room(room, {
            "type": "qa_list_updated",
            "questions": room.qa_questions
        })

    def players_of(self, room):
        return list(room.players.values())

    async def handle_disconnect(self, websocket):
        # Check if it was host
        if websocket in self.ws_to_host:
            pin = self.ws_to_host.pop(websocket)
            room = self.rooms.get(pin)
            if room:
                room.host_ws = None
                logger.info(f"Host disconnected from room {pin}")

        # Check if it was player
        if websocket in self.ws_to_player:
            pin, player_id = self.ws_to_player.pop(websocket)
            room = self.rooms.get(pin)
            if room and player_id in room.players:
                p = room.players[player_id]
                p.websocket = None
                logger.info(f"Player {p.name} disconnected from room {pin}")
                # If in lobby, notify host of player left
                if room.state == "LOBBY":
                    # We can keep them or remove them
                    await self.send_to_host(room, {
                        "type": "player_left",
                        "player_id": player_id,
                        "total_players": len([x for x in room.players.values() if x.websocket is not None])
                    })

game_manager = GameManager()
