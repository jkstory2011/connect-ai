#!/bin/bash
# Ollama & LM Studio Server Persistent Monitoring Script
LOG_FILE="/var/log/jkstory_llm_monitor.log"

echo "--- $(date) ---: LLM 서버 모니터링 시작." >> $LOG_FILE

# 1. Ollama Status Check and Restart
if ! pgrep -f ollama > /dev/null; then
    echo "[ALERT] Ollama Server is down. Attempting restart..." | tee -a $LOG_FILE
    /usr/local/bin/ollama serve & # Assuming standard path or appropriate command
    sleep 10
    if pgrep -f ollama > /dev/null; then
        echo "[SUCCESS] Ollama Server restarted successfully." | tee -a $LOG_FILE
    else
        echo "[ERROR] Failed to restart Ollama server. Manual intervention required." | tee -a $LOG_FILE
    fi
else
    echo "[INFO] Ollama Server is running normally." >> $LOG_FILE
fi

# 2. LM Studio/Backend Check (Placeholder for specific process)
if ! pgrep -f "lmstudio_backend" > /dev/null; then # 실제 백엔드 프로세스 이름으로 변경 필요
    echo "[ALERT] LM Studio Backend is down. Attempting restart..." | tee -a $LOG_FILE
    # 여기에 실제 백그라운드 실행 명령어를 삽입합니다. (예: start /B lmstudio_backend)
    sleep 5 # 시뮬레이션 대기
    echo "[SUCCESS] Simulated LM Studio backend check complete." >> $LOG_FILE
else
     echo "[INFO] LM Studio Backend is running normally." >> $LOG_FILE
fi

echo "--- $(date) ---: 모니터링 완료." >> $LOG_FILE