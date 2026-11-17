
# 대화 기록을 임시로 저장하는 공간
conversation_history = {}


# 대화 기록 가져오기
def get_history(session_id: str):
    return conversation_history.get(session_id, [])


# 사용자 질문과 챗봇 답변 저장하기
def add_history(session_id: str, question: str, answer: str):
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({
        "role": "user",
        "content": question
    })

    conversation_history[session_id].append({
        "role": "assistant",
        "content": answer
    })

    # 최근 대화 10개 메시지만 유지
    conversation_history[session_id] = (
        conversation_history[session_id][-10:]
    )


# 대화 기록 초기화
def clear_history(session_id: str):
    conversation_history.pop(session_id, None)
