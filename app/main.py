
from datetime import date, timedelta
import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.teacher_service import (
    load_teachers,
    get_teacher,
    add_teacher,
    update_teacher,
    create_teacher_prompt
)
from app.services.memory_service import (
    get_history,
    add_history,
    clear_history
)

from app.services.safety_service import check_safety

from app.services.affinity_service import (
    analyze_engagement,
    add_affinity_points,
    get_affinity,
    get_unlocked_tips
)

from app.services.neis_service import (
    get_school_info,
    get_school_schedule,
    get_meal_info,
    get_school_codes,
    format_meal_info,
    format_schedule_info
)


app = FastAPI(
    title="AI 선생님 챗봇",
    description="NEIS API와 Qwen을 활용한 학교 정보 챗봇",
    version="1.0.0"
)
# 선생님 등록 및 수정에 사용할 데이터 구조
class TeacherRequest(BaseModel):
    id: str
    name: str
    subject: str
    personality: str = ""
    speaking_style: str = ""
    teaching_style: str = ""
    values: list[str] = []
    specialties: list[str] = []
    system_prompt: str = ""


# 메인 페이지
@app.get("/")
def home():
    return {
        "message": "AI 선생님 챗봇 서버가 실행 중입니다!"
    }


# 서버 상태 확인
@app.get("/health")
def health_check():
    return {"status": "ok"}

# 전체 선생님 목록 조회
@app.get("/teachers")
def teacher_list():
    return {
        "teachers": load_teachers()
    }
# 새로운 선생님 등록
@app.post("/teachers")
def register_teacher(teacher: TeacherRequest):
    try:
        return add_teacher(teacher.model_dump())

    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

# 기존 선생님 정보 수정
@app.put("/teachers/{teacher_id}")
def edit_teacher(teacher_id: str, teacher: TeacherRequest):
    try:
        updated_data = teacher.model_dump(exclude={"id"})
        return update_teacher(teacher_id, updated_data)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 특정 선생님 정보 조회
@app.get("/teachers/{teacher_id}")
def teacher_detail(teacher_id: str):
    teacher = get_teacher(teacher_id)

# 특정 선생님의 AI 프롬프트 조회
@app.get("/teachers/{teacher_id}/prompt")
def teacher_prompt(teacher_id: str):
    prompt = create_teacher_prompt(teacher_id)

    if prompt is None:
        raise HTTPException(
            status_code=404,
            detail="해당 선생님을 찾을 수 없습니다."
        )

    return {
        "teacher_id": teacher_id,
        "prompt": prompt
    }

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="해당 선생님을 찾을 수 없습니다."
        )

    return teacher

# 학교 정보 조회
@app.get("/school")
def school_info(school_name: str):
    try:
        return get_school_info(school_name)

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 학교 코드 조회
@app.get("/school/codes")
def school_codes(school_name: str):
    try:
        result = get_school_codes(school_name)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="학교 정보를 찾을 수 없습니다."
            )

        return result

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 학사일정 조회
@app.get("/schedule")
def school_schedule(
    education_office_code: str,
    school_code: str,
    start_date: str,
    end_date: str
):
    try:
        return get_school_schedule(
            education_office_code,
            school_code,
            start_date,
            end_date
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 급식 정보 조회
@app.get("/meal")
def meal_info(
    education_office_code: str,
    school_code: str,
    meal_date: str
):
    try:
        return get_meal_info(
            education_office_code,
            school_code,
            meal_date
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 급식 정보 텍스트 변환
@app.get("/meal/text")
def meal_text(
    education_office_code: str,
    school_code: str,
    meal_date: str
):
    try:
        result = get_meal_info(
            education_office_code,
            school_code,
            meal_date
        )

        return {
            "answer": format_meal_info(result)
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 학사일정 텍스트 변환
@app.get("/schedule/text")
def schedule_text(
    education_office_code: str,
    school_code: str,
    schedule_date: str
):
    try:
        result = get_school_schedule(
            education_office_code,
            school_code,
            schedule_date,
            schedule_date
        )

        return {
            "answer": format_schedule_info(result)
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# AI 챗봇 및 호감도 기능
@app.get("/chat")
def chat(question: str, session_id: str = "default"):

    # 안전성 검사
    safety_result = check_safety(question)

    if safety_result["blocked"]:
        return {
            "question": question,
            "category": "blocked",
            "answer": safety_result["message"],
            "history": get_history(session_id),
            "affinity": {
                "points_earned": 0,
                "total_score": get_affinity(session_id),
                "reasons": [],
                "unlocked_tips": get_unlocked_tips(
                    get_affinity(session_id)
                )
            }
        }

    # 날짜 계산
    target_date = date.today()

    if "내일" in question:
        target_date += timedelta(days=1)

    elif "모레" in question:
        target_date += timedelta(days=2)

    date_text = target_date.strftime("%Y%m%d")

    education_office_code = "G10"
    school_code = "7430310"

    try:

        # 급식 질문
        if any(word in question for word in ["급식", "밥", "메뉴"]):

            result = get_meal_info(
                education_office_code,
                school_code,
                date_text
            )

            answer = format_meal_info(result)
            category = "meal"

        # 학사일정 질문
        elif any(
            word in question
            for word in ["일정", "학사", "시험", "행사"]
        ):

            result = get_school_schedule(
                education_office_code,
                school_code,
                date_text,
                date_text
            )

            answer = format_schedule_info(result)
            category = "schedule"

        # 분류되지 않은 질문
        else:
            answer = "급식이나 학사일정에 관해 질문해 주세요."
            category = "unknown"

        # 호감도 분석
        engagement = analyze_engagement(question)

        # 호감도 점수 추가
        total_score = add_affinity_points(
            session_id,
            engagement["points_earned"]
        )

        # 공개 가능한 TIP 조회
        unlocked_tips = get_unlocked_tips(total_score)

        # 질문과 답변 저장
        add_history(session_id, question, answer)

        return {
            "question": question,
            "category": category,
            "answer": answer,
            "history": get_history(session_id),
            "affinity": {
                "points_earned": engagement["points_earned"],
                "total_score": total_score,
                "reasons": engagement["reasons"],
                "unlocked_tips": unlocked_tips
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))


# 대화 기록 조회
@app.get("/chat/history")
def chat_history(session_id: str = "default"):
    return {
        "session_id": session_id,
        "history": get_history(session_id)
    }


# 대화 기록 초기화
@app.delete("/chat/history")
def delete_chat_history(session_id: str = "default"):
    clear_history(session_id)

    return {
        "message": "대화 기록이 초기화되었습니다.",
        "session_id": session_id
    }


# 호감도 조회
@app.get("/chat/affinity")
def chat_affinity(session_id: str = "default"):

    total_score = get_affinity(session_id)

    return {
        "session_id": session_id,
        "total_score": total_score,
        "unlocked_tips": get_unlocked_tips(total_score)
    }
