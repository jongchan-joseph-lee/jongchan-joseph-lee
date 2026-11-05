"""README.template.md → README.md
만 나이와 실무 경력(X년 Y개월)을 한국 시간 기준 오늘 날짜로 계산해 채웁니다.
GitHub Actions(.github/workflows/update-readme.yml)가 매일 실행합니다.
"""
from datetime import date, datetime, timedelta, timezone
import re
from pathlib import Path

BIRTH = date(1993, 11, 26)        # 생년월일
CAREER_START = date(2022, 5, 1)   # 실무 경력 시작 (㈜지오시스템리서치 입사, 2022.05)

ROOT = Path(__file__).resolve().parents[1]


def today_kst() -> date:
    return datetime.now(timezone(timedelta(hours=9))).date()


def full_age(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def career(start: date, today: date) -> str:
    months = (today.year - start.year) * 12 + (today.month - start.month)
    if today.day < start.day:
        months -= 1
    y, m = divmod(max(months, 0), 12)
    return f"{y}년 {m}개월" if m else f"{y}년"


WJ = "\u2060"  # word joiner: 한글 단어 중간에서 줄이 바뀌지 않게 함
HANGUL = re.compile(r"(?<=[\uac00-\ud7a3])(?=[\uac00-\ud7a3])")


def keep_words(text: str) -> str:
    """태그 밖의 글자에서 한글 음절 사이에 word joiner를 넣어, 줄바꿈이 띄어쓰기에서만 일어나게 합니다."""
    parts = re.split(r"(<[^>]*>)", text)
    # " · " 구분점이 줄 맨 앞에 오지 않도록 앞 단어에 붙임
    return "".join(s if s.startswith("<") else HANGUL.sub(WJ, s).replace(" · ", "\u00a0· ") for s in parts)


def main():
    t = today_kst()
    text = (ROOT / "README.template.md").read_text(encoding="utf-8")
    text = text.replace("{{AGE}}", str(full_age(BIRTH, t))).replace("{{CAREER}}", career(CAREER_START, t))
    text = keep_words(text)
    out = ROOT / "README.md"
    if not out.exists() or out.read_text(encoding="utf-8") != text:
        out.write_text(text, encoding="utf-8")
        print("README.md updated", t)
    else:
        print("no change", t)


if __name__ == "__main__":
    main()
