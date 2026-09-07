import os
import streamlit as st
from google import genai
from google.genai import types

# 페이지 설정
st.set_page_config(
    page_title="역학적 에너지 보존 힌트 튜터",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 역학적 에너지 보존 법칙 - 힌트 튜터")
st.caption("문제를 풀다 막힐 때 질문하세요! 정답 대신 핵심 힌트를 드릴게요.")

# 1. API Key 불러오기 (Streamlit Secrets 우선 -> 환경변수)
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]

# 만약 API Key가 설정되지 않은 경우 수동 입력창 표시
if not api_key:
    with st.sidebar:
        st.header("⚙️ 설정")
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

if not api_key:
    st.info("👈 시작하려면 사이드바에 Gemini API Key를 입력하거나 Secrets 설정을 완료하세요.")
    st.stop()

# Client 생성
client = genai.Client(api_key=api_key)

# 2. PDF 파일 로드 및 캐싱 (최초 1회만 읽어옴)
@st.cache_resource
def load_pdf_part():
    pdf_path = "형성평가_역학적에너지보존법칙.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        return types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    else:
        st.warning(f"⚠️ '{pdf_path}' 파일을 찾을 수 없습니다. PDF 없이 힌트 기능만 동작합니다.")
        return None

pdf_part = load_pdf_part()

# 3. System Instruction 설정
SYSTEM_INSTRUCTION = """
너는 중학교 3학년 과학 '역학적 에너지 보존 법칙' 단원의 친절하고 똑똑한 AI 튜터야.
함께 첨부된 [형성평가_역학적에너지보존법칙.pdf] 문서를 참조해서 학생들의 질문에 대답해줘.

[핵심 규칙]
1. 절대로 문제의 최종 정답(예: "답은 3번이야", "값은 58.8 J이야")을 직접 알려주지 마.
2. 학생이 특정 문제(예: 1번, 3번, 서술형 7번 등)에 대해 질문하면, 먼저 PDF 상의 해당 문제가 묻고 있는 핵심 개념이나 조건을 확인하고 질문을 던져줘.
3. 위치 에너지 공식($9.8 \\times m \\times h$), 운동 에너지 공식($\\frac{1}{2}mv^2$), 역학적 에너지 보존 법칙($E_{역학} = E_{위치} + E_{운동}$) 등을 이용해 단계적으로 유도해줘.
4. 말투는 친절하고 격려하는 중학교 선생님 어조(~해요, ~해볼까요?)를 사용해.
5. 학생이 잘못된 개념이나 계산 결과를 말하면 어디서 오해가 생겼는지 되짚어줄 수 있는 힌트를 줘.
"""

# 4. 대화 이력 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if prompt := st.chat_input("질문하고 싶은 문제 번호나 내용을 입력하세요 (예: 3번 문제 힌트 줘)"):
    # 사용자 메시지 화면 출력 및 저장
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gemini에 전달할 컨텐츠 생성 (PDF 파일 전달 포함)
    contents = []
    
    # PDF가 있는 경우 첫 요청 컨텐츠에 PDF 포함
    if pdf_part:
        contents.append(pdf_part)

    # 대화 기록 추가
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # 답변 생성 요청
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3
                )
            )
            bot_reply = response.text
            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")