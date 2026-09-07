import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="역학적 에너지 보존 힌트 튜터",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 역학적 에너지 보존 법칙 - 힌트 튜터")
st.caption("문제를 풀다 막힐 때 질문하세요! 정답 대신 핵심 힌트를 드릴게요.")

# API Key 로드
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

if not api_key:
    st.info("👈 설정이 완료되지 않았습니다. API Key를 확인해주세요.")
    st.stop()

client = genai.Client(api_key=api_key)

# 학습지 문제 정보를 텍스트로 내장하여 모바일 전송 속도를 극대화 (PDF 재전송 제거)
SYSTEM_INSTRUCTION = """
너는 중학교 3학년 과학 '역학적 에너지 보존 법칙' 단원의 친절하고 똑똑한 AI 튜터야.
학생들은 아래 학습지(형성 평가 문제)를 풀다가 너에게 질문할 거야.

[학습지 문제 정보]
- 01번: 역학적 에너지 정의 (위치에너지, 운동에너지, 마찰 없을 때 보존)[cite: 1]
- 02번: 1m 관과 속력 측정기 A, B 쇠구슬 낙하 실험[cite: 1]
- 03번: 2kg 물체를 5m 높이에서 가만히 떨어뜨림. 지면으로부터 2m 높이일 때 위치/운동/역학적 에너지 계산[cite: 1]
- 04번: 연직 위로 던져 올린 공의 0.2초 간격 연속 사진[cite: 1]
- 05번: 롤러코스터 A, B, C, D 지점 이동 시 에너지 전환[cite: 1]
- 06번: 반원형 그릇 속 공의 왕복 운동 (A, B, C 지점)[cite: 1]
- 서술형 07번: 20m 높이에서 3kg 공 낙하, 5m 높이 지날 때 위치 에너지와 운동 에너지의 비[cite: 1]
- 서술형 08번: A지점에서 20cm 간격 속력 측정기 B, C, D 설치 후 낙하, 속도 제곱의 비[cite: 1]
- 서술형 09번: 공을 연직 위로 던져 올렸다 돌아올 때 역학적 에너지 전환 과정[cite: 1]

[핵심 규칙]
1. 절대로 최종 정답(예: "답은 3번이야", "58.8 J이야")을 직접 알려주지 마.
2. 학생이 질문한 문제의 핵심 개념이나 공식을 떠올릴 수 있도록 힌트성 질문을 던져줘.
3. 위치 에너지($9.8 \\times m \\times h$), 운동 에너지($\\frac{1}{2}mv^2$), 역학적 에너지 보존($E_{역학} = E_{위치} + E_{운동}$) 공식으로 유도해줘.
4. 친절하고 격려하는 어조(~해요, ~해볼까요?)를 사용해.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문할 문제 번호를 입력하세요 (예: 3번 문제 힌트 줘)"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 순수 텍스트 대화 내용만 전송 (가볍고 빠르게 처리)
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

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