#!/bin/bash
echo "Memulai QuizVibe service..."
systemctl --user start quizvibe
systemctl --user status quizvibe --no-pager
echo ""
echo "🚀 QuizVibe aktif!"
echo "Buka: http://localhost:8000/"
