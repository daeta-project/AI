import json
from pathlib import Path

# teachers.json 파일 위치
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "teachers.json"


# 모든 선생님 정보 불러오기
def load_teachers():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("teachers", [])


# 특정 선생님 정보 불러오기
def get_teacher(teacher_id):
    teachers = load_teachers()

    for teacher in teachers:
        if teacher["id"] == teacher_id:
            return teacher

    return None

# 선생님의 인격을 AI 프롬프트로 변환
def create_teacher_prompt(teacher_id):
    teacher = get_teacher(teacher_id)

    if teacher is None:
        return None

    prompt = f"""
너는 {teacher['name']}이다.

담당 과목: {teacher['subject']}
성격: {teacher['personality']}
말투: {teacher['speaking_style']}
설명 방식: {teacher['teaching_style']}
가치관: {', '.join(teacher['values'])}
전문 분야: {', '.join(teacher['specialties'])}

추가 지침:
{teacher['system_prompt']}
"""

    return prompt.strip()

    # 선생님 정보 저장하기
def save_teachers(teachers):
    data = {
        "teachers": teachers
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 새로운 선생님 등록하기
def add_teacher(teacher_data):
    teachers = load_teachers()

    # 이미 등록된 ID인지 확인
    for teacher in teachers:
        if teacher["id"] == teacher_data["id"]:
            raise ValueError("이미 등록된 선생님 ID입니다.")

    teachers.append(teacher_data)
    save_teachers(teachers)

    return teacher_data


# 기존 선생님 정보 수정하기
def update_teacher(teacher_id, updated_data):
    teachers = load_teachers()

    for teacher in teachers:
        if teacher["id"] == teacher_id:

            # 선생님 ID는 수정하지 못하도록 제한
            if "id" in updated_data and updated_data["id"] != teacher_id:
                raise ValueError("선생님 ID는 변경할 수 없습니다.")

            teacher.update(updated_data)
            save_teachers(teachers)

            return teacher

    raise ValueError("해당 선생님을 찾을 수 없습니다.")