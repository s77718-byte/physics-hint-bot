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

# Streamlit Secrets 또는 환경 변수에서 API Key 로드
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    with st.sidebar:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password")

if not api_key:
    st.info("👈 설정이 완료되지 않았습니다. API Key를 확인해주세요.")
    st.stop()

client = genai.Client(api_key=api_key)

# PDF의 모든 문제, 보기, 세부 내용을 내장한 시스템 프롬프트 (속도 최적화 및 세부 답변 완벽 지원)
SYSTEM_INSTRUCTION = """
너는 중학교 3학년 과학 '역학적 에너지 보존 법칙' 단원의 친절하고 똑똑한 AI 튜터야.
학생들은 아래 [형성 평가 문제] 학습지를 풀다가 특정 문제나 특정 보기(선지)에 대해 질문할 거야.

[형성 평가 문제 전체 내용]

01. 역학적 에너지에 관한 설명으로 옳은 것만을 보기에서 있는 대로 고른 것은?
  - 보기:
    ㄱ. 중력에 의한 위치 에너지와 운동 에너지의 차이다.
    ㄴ. 물체가 중력을 받아 운동할 때 역학적 에너지 전환이 일어난다.
    ㄷ. 모든 마찰이 없을 때 물체의 역학적 에너지는 일정하게 보존된다.

02. 1m 길이의 투명 플라스틱 관의 가운데와 가장 아래 지점에 속력 측정기 A, B를 설치한 후 가장 위 지점에서 쇠구슬을 가만히 놓는 실험을 하였다. 설명으로 옳은 것은? (단, 공기 마찰 무시)
  - ① 낙하하는 동안 쇠구슬의 운동 에너지가 감소한다.
  - ② 낙하하는 동안 쇠구슬의 중력에 의한 위치 에너지가 증가한다.
  - ③ 낙하하는 동안 쇠구슬의 역학적 에너지는 감소한다.
  - ④ 속력 측정기에 나타난 값의 비 v_A : v_B는 1 : 2이다.
  - ⑤ 속력 측정기 A, B를 지나는 순간 쇠구슬의 운동 에너지의 비 E_A : E_B는 1 : 2이다.

03. 질량이 2 kg인 물체를 5m 높이에서 가만히 떨어뜨렸다. 지면으로부터 2m 높이인 지점을 지나는 순간의 에너지에 관한 설명으로 옳은 것은? (단, 중력 가속도 상수는 9.8)
  - 보기:
    ㄱ. 운동 에너지는 39.2 J이다.
    ㄴ. 역학적 에너지는 98 J이다.
    ㄷ. 중력에 의한 위치 에너지는 58.8 J이다.

04. 연직 위로 던져 올린 공의 영상을 0.2초마다 정지한 화면(0초, 0.2초, 0.4초(최고점), 0.6초, 0.8초)을 나타낸 것이다. 나머지 넷과 값이 다른 하나는? (단, 0초 기준, 마찰 무시)
  - ① 0초일 때 역학적 에너지
  - ② 0.2초일 때 운동 에너지
  - ③ 0.4초일 때 중력에 의한 위치 에너지
  - ④ 0.6초일 때 역학적 에너지
  - ⑤ 0.8초일 때 운동 에너지

05. 롤러코스터가 레일을 따라 A(최고점), B(내리막), C(최저점), D(오르막)점을 차례로 지나며 운동하고 있다. 설명으로 옳은 것은? (단, 마찰 무시)
  - ① A점에서 운동 에너지가 가장 크다.
  - ② A점과 C점에서 역학적 에너지는 같다.
  - ③ C점에서 중력에 의한 위치 에너지가 가장 크다.
  - ④ B점에서 C점으로 운동할 때 운동 에너지가 중력에 의한 위치 에너지로 전환된다.
  - ⑤ C점에서 D점으로 운동할 때 중력에 의한 위치 에너지가 운동 에너지로 전환된다.

06. 공이 반원형 그릇 속에서 A(최상단)와 C(최상단) 사이를 왕복 운동(B는 최하점)을 한다. 운동 에너지가 중력에 의한 위치 에너지로 전환되는 구간만을 보기에서 고른 것은?
  - 보기: ㄱ. A->B 구간 / ㄴ. B->A 구간 / ㄷ. B->C 구간 / ㄹ. C->B 구간

서술형 07. 지면으로부터 20m 높이에서 질량이 3 kg인 공을 가만히 떨어뜨렸다. 지면으로부터 높이가 5m인 지점을 지날 때 중력에 의한 위치 에너지와 운동 에너지의 비(위치 : 운동)를 구하시오.

서술형 08. 추가 매달린 A 지점으로부터 20 cm 간격으로 속력 측정기를 설치(B: 20cm, C: 40cm, D: 60cm 낙하 지점)한 후, 실을 잘라 추를 낙하시켰다. B, C, D 지점에서 측정되는 값의 제곱의 비 (v_B)^2 : (v_C)^2 : (v_D)^2 를 구하시오.

서술형 09. 공을 연직 위로 던져 올렸더니 공이 운동한 후 다시 처음 던진 지점으로 돌아왔다. 이 과정에서 역학적 에너지 전환 과정을 설명하시오.


[튜터 지침 및 응답 규칙]
1. 정답(예: "3번이 맞아요", "답은 58.8J입니다")을 절대로 직접적으로 알려주지 마.
2. 학생이 특정 보기(예: "2번 문제의 3번 보기가 이해 안 돼요", "3번 문제 ㄴ 보기 힌트 줘")를 물어보면, 해당 보기가 왜 맞거나 틀린 지 판단할 수 있는 핵심 질문이나 공식을 안내해줘.
3. 역학적 에너지 공식 활용 힌트:
   - 위치 에너지 = 9.8 × m × h (높이가 낮아지면 감소, 높이가 높아지면 증가)
   - 운동 에너지 = 1/2 × m × v^2 (낙하한 거리, 즉 감소한 위치 에너지만큼 증가)
   - 역학적 에너지 보존 = 마찰이 없으면 어느 지점이나 (위치 에너지 + 운동 에너지)의 총합은 항상 일정함
4. 말투는 중학교 과학 선생님처럼 다정하고 친절하게 표현해줘 (~해볼까요?, ~는 어떻게 될까요?).
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("예: 2번 문제 3번 보기가 왜 틀렸는지 힌트 줘"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 순수 텍스트 전송 (속도 극대화)
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
            # 1차 시도: gemini-2.5-flash
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3
                )
            )
            bot_reply = response.text
        except Exception as e:
            # 503 에러 등 발생 시 2차 시도: gemini-2.0-flash로 자동 우회
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3
                    )
                )
                bot_reply = response.text
            except Exception as e2:
                bot_reply = "⚠️ 현재 구글 서버에 접속자가 많아 응답이 지연되고 있습니다. 잠시 후 다시 질문해 주세요!"

        st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})