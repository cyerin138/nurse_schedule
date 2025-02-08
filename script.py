import pandas as pd
import numpy as np
import calendar

# 2월의 날짜 범위 설정
year = 2025
month = 2
num_days = calendar.monthrange(year, month)[1]

# 간호사 명단
nurses = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]

# 간호사 직급 분류
senior_nurses = {"B", "C", "D", "Q", "R", "S"}
mid_nurses = {"E", "F", "T"}
junior_nurses = {"G", "H", "I", "J", "K", "L", "M", "N", "O", "P"}

# 스케줄 데이터프레임 생성
schedule = pd.DataFrame(index=nurses, columns=range(1, num_days + 1))

# 요청된 휴무(W), 연차(V), 교육(ED) 반영
requests = {
    "B": {1: "W", 2: "W", 3: "W", 4: "V", 5: "V", 6: "V"},
    "C": {6: "ED", 19: "W", 20: "W", 21: "V", 22: "V"},
    "D": {8: "W", 9: "W", 10: "W", 13: "V", 14: "V", 15: "V", 16: "V"},
    "F": {1: "W", 2: "W", 15: "W", 16: "N", 22: "V"},
    "G": {6: "W", 7: "W", 8: "W", 9: "W"},
    "H": {21: "W"},
    "J": {10: "W", 18: "W"},
    "O": {10: "W"},
    "P": {21: "W", 23: "V", 24: "V", 25: "V"},
    "Q": {3: "W", 9: "W", 10: "W", 17: "W", 23: "W", 24: "W", 28: "V"},
    "R": {26: "V", 27: "V", 28: "V"},
    "S": {3: "ED"}
}

# 요청사항 적용
for nurse, days in requests.items():
    for day, duty in days.items():
        schedule.at[nurse, day] = duty

# 간호사별 W 횟수를 기록하기 위한 딕셔너리 (제한 초과 방지)
max_w_days = {nurse: 14 if nurse in {"Q", "R", "S", "T"} else 8 for nurse in nurses}
current_w_days = {nurse: sum(1 for v in schedule.loc[nurse] if v == "W") for nurse in nurses}

# 하루 단위로 근무 배치
for day in range(1, num_days + 1):
    available_nurses = schedule.index[schedule[day].isna()].tolist()

    # 야간(N) 근무 배치 (최소 고급 1, 중급 1, 신입 1, 최대 4명)
    night_nurses = list(senior_nurses & set(available_nurses))[:1] + \
                   list(mid_nurses & set(available_nurses))[:1] + \
                   list(junior_nurses & set(available_nurses))[:1]
    if len(night_nurses) < 3:
        night_nurses += list(set(available_nurses) - set(night_nurses))[:(3 - len(night_nurses))]
    for nurse in night_nurses[:4]:
        schedule.at[nurse, day] = "N"

    # 오전(D) 근무 배치 (최소 고급 1, 중급 1, 신입 1, 최대 7명)
    remaining_nurses = list(set(available_nurses) - set(night_nurses))
    morning_nurses = list(senior_nurses & set(remaining_nurses))[:1] + \
                     list(mid_nurses & set(remaining_nurses))[:1] + \
                     list(junior_nurses & set(remaining_nurses))[:1]
    morning_nurses += list(set(remaining_nurses) - set(morning_nurses))[:(7 - len(morning_nurses))]
    for nurse in morning_nurses[:7]:
        schedule.at[nurse, day] = "D"

    # 오후(E) 근무 배치 (최소 고급 1, 중급 1, 신입 1, 최대 5명)
    remaining_nurses = list(set(remaining_nurses) - set(morning_nurses))
    evening_nurses = list(senior_nurses & set(remaining_nurses))[:1] + \
                     list(mid_nurses & set(remaining_nurses))[:1] + \
                     list(junior_nurses & set(remaining_nurses))[:1]
    evening_nurses += list(set(remaining_nurses) - set(evening_nurses))[:(5 - len(evening_nurses))]
    for nurse in evening_nurses[:5]:
        schedule.at[nurse, day] = "E"

    # 미드데이(M) 근무 배치 (최대 3명)
    remaining_nurses = list(set(remaining_nurses) - set(evening_nurses))
    midday_nurses = remaining_nurses[:min(len(remaining_nurses), 3)]
    for nurse in midday_nurses:
        schedule.at[nurse, day] = "M"

    # 남은 간호사에게 W 배정 (W 초과 제한 준수)
    for nurse in remaining_nurses[len(midday_nurses):]:
        if current_w_days[nurse] < max_w_days[nurse]:
            schedule.at[nurse, day] = "W"
            current_w_days[nurse] += 1
        else:
            schedule.at[nurse, day] = "D"  # 초과할 경우 오전 근무 배정

# 재조정된 스케줄 출력
# import ace_tools as tools
# tools.display_dataframe_to_user(name="재조정된 2월 간호사 근무표", dataframe=schedule)
print(schedule)