
import os
import requests

from dotenv import load_dotenv

load_dotenv()

NEIS_API_KEY = os.getenv("NEIS_API_KEY")

BASE_URL = "https://open.neis.go.kr/hub"


def request_neis(api_name: str, params: dict):
    if not NEIS_API_KEY:
        raise ValueError("NEIS API 인증키가 설정되지 않았습니다.")

    request_params = {
        **params,
        "KEY": NEIS_API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100
    }

    response = requests.get(
        f"{BASE_URL}/{api_name}",
        params=request_params,
        timeout=10
    )

    print("NEIS 요청 URL:", response.url.replace(NEIS_API_KEY, "HIDDEN"))
    print("NEIS 응답:", response.text)

    response.raise_for_status()

    return response.json()


# 학교 기본정보
def get_school_info(school_name: str):
    return request_neis("schoolInfo", {
        "SCHUL_NM": school_name
    })


# 학교 코드 조회
def get_school_codes(school_name: str):
    result = get_school_info(school_name)

    rows = result.get("schoolInfo", [])

    if len(rows) < 2:
        return None

    school_list = rows[1].get("row", [])

    if not school_list:
        return None

    school = school_list[0]

    return {
        "school_name": school["SCHUL_NM"],
        "education_office_code": school["ATPT_OFCDC_SC_CODE"],
        "school_code": school["SD_SCHUL_CODE"]
    }


# 학사일정
def get_school_schedule(
    education_office_code: str,
    school_code: str,
    start_date: str,
    end_date: str
):
    return request_neis("SchoolSchedule", {
        "ATPT_OFCDC_SC_CODE": education_office_code,
        "SD_SCHUL_CODE": school_code,
        "AA_YMD": start_date
    })


# 급식정보
def get_meal_info(
    education_office_code: str,
    school_code: str,
    meal_date: str
):
    return request_neis("mealServiceDietInfo", {
        "ATPT_OFCDC_SC_CODE": education_office_code,
        "SD_SCHUL_CODE": school_code,
        "MLSV_YMD": meal_date
    })

# NEIS 응답에서 실제 데이터 목록 가져오기
def extract_rows(result: dict, api_name: str):
    data = result.get(api_name, [])

    if len(data) < 2:
        return []

    return data[1].get("row", [])


# 급식 데이터를 문장으로 변환
def format_meal_info(result: dict):
    rows = extract_rows(result, "mealServiceDietInfo")

    if not rows:
        return "해당 날짜에는 등록된 급식 정보가 없습니다."

    messages = []

    for meal in rows:
        date = meal.get("MLSV_YMD", "")
        meal_name = meal.get("MMEAL_SC_NM", "급식")
        menu = meal.get("DDISH_NM", "메뉴 정보 없음")
        calories = meal.get("CAL_INFO", "")

        # 메뉴 구분 기호를 쉼표로 변경
        menu = menu.replace("<br/>", ", ")

        message = (
            f"{date} {meal_name}은 "
            f"{menu}입니다."
        )

        if calories:
            message += f" 열량은 {calories}입니다."

        messages.append(message)

    return "\n".join(messages)


# 학사일정 데이터를 문장으로 변환
def format_schedule_info(result: dict):
    rows = extract_rows(result, "SchoolSchedule")

    if not rows:
        return "해당 날짜에는 등록된 학사일정 정보가 없습니다."

    messages = []

    for event in rows:
        date = event.get("AA_YMD", "")
        name = event.get("EVENT_NM", "일정")
        content = event.get("EVENT_CNTNT", "")

        message = f"{date} 학사일정은 {name}입니다."

        if content:
            message += f" 상세 내용은 {content}입니다."

        messages.append(message)

    return "\n".join(messages)
