
import re


# 개인정보 검사
def check_personal_info(text: str):
    patterns = {
        "전화번호": r"01[016789]-?\d{3,4}-?\d{4}",
        "이메일": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "주민등록번호": r"\d{6}-?[1-4]\d{6}",
    }

    for info_type, pattern in patterns.items():
        if re.search(pattern, text):
            return {
                "blocked": True,
                "reason": "personal_info",
                "message": (
                    f"개인정보 보호를 위해 {info_type}이 "
                    "포함된 질문에는 답변할 수 없어요. "
                    "개인정보를 삭제하고 다시 질문해 주세요."
                )
            }

    return {"blocked": False}


# 부적절한 표현 검사
def check_inappropriate_words(text: str):
    blocked_words = [
        "패드립",
        "개새끼",
        "씨발",
        "병신",
    ]

    normalized_text = text.replace(" ", "").lower()

    for word in blocked_words:
        if word.replace(" ", "") in normalized_text:
            return {
                "blocked": True,
                "reason": "inappropriate_language",
                "message": (
                    "서로 존중하는 표현을 사용해 주세요. "
                    "다른 표현으로 질문해 주시면 도와드릴게요."
                )
            }

    return {"blocked": False}


# 전체 안전 검사
def check_safety(text: str):
    if not text or not text.strip():
        return {
            "blocked": True,
            "reason": "empty",
            "message": "질문 내용을 입력해 주세요."
        }

    if len(text) > 1000:
        return {
            "blocked": True,
            "reason": "too_long",
            "message": "질문은 1000자 이내로 입력해 주세요."
        }

    result = check_personal_info(text)
    if result["blocked"]:
        return result

    result = check_inappropriate_words(text)
    if result["blocked"]:
        return result

    return {"blocked": False}
