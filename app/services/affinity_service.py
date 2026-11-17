
# 호감도 분석 및 관리 서비스

# 임시 호감도 저장 공간
affinity_scores = {}

# 호감도 점수별 선생님 TIP
AFFINITY_TIPS = [
    {
        "score": 5,
        "title": "질문 잘하는 방법",
        "content": "궁금한 점을 구체적으로 질문하면 더 정확한 답변을 받을 수 있어요."
    },
    {
        "score": 10,
        "title": "학교생활 정보 활용하기",
        "content": "학교 일정과 급식 정보를 미리 확인하면 학교생활을 계획하기 편해요."
    },
    {
        "score": 15,
        "title": "전공 탐색하기",
        "content": "관심 있는 분야와 관련된 활동을 찾아보면 전공 선택에 도움이 돼요."
    }
]


# 학생의 대화 참여도 분석
def analyze_engagement(message: str):
    points = 0
    reasons = []

    school_keywords = [
        "급식", "일정", "시험", "수행평가",
        "동아리", "전공", "공부", "학교",
        "과제", "수업"
    ]

    follow_up_keywords = [
        "그럼", "왜", "어떻게",
        "더 알려줘", "자세히",
        "다시 설명", "무슨 뜻"
    ]

    if any(word in message for word in school_keywords):
        points += 1
        reasons.append("학교 관련 질문")

    if any(word in message for word in follow_up_keywords):
        points += 1
        reasons.append("추가 질문 및 적극적인 참여")

    points = min(points, 2)

    return {
        "points_earned": points,
        "reasons": reasons
    }


# 호감도 점수 추가
def add_affinity_points(session_id: str, points: int):
    if session_id not in affinity_scores:
        affinity_scores[session_id] = 0

    affinity_scores[session_id] += points

    return affinity_scores[session_id]


# 현재 호감도 조회
def get_affinity(session_id: str):
    return affinity_scores.get(session_id, 0)


# 점수에 따라 공개할 TIP 조회
def get_unlocked_tips(total_score: int):
    return [
        tip for tip in AFFINITY_TIPS
        if total_score >= tip["score"]
    ]


# 호감도 초기화
def clear_affinity(session_id: str):
    affinity_scores.pop(session_id, None)
