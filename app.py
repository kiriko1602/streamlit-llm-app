# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# --- 初期設定 ---
st.set_page_config(page_title="LLM専門家チャット", page_icon="🤖", layout="centered")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- 安全チェック ---
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY が見つかりません。.env に設定してから再実行してください。")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# --- 専門家（ロール）定義 ---
EXPERT_PROMPTS = {
    "Pythonメンター": (
        "あなたは初学者にやさしいPython講師です。"
        "短く、具体的なサンプルコードを交えて説明してください。"
    ),
    "AI活用プランナー": (
        "あなたは業務課題をAIで解決するプランナーです。"
        "現実的な導入手順とユースケース、注意点を簡潔に提案してください。"
    ),
    "業務自動化コンサルタント": (
        "あなたは企業の業務効率化コンサルタントです。"
        "Excel/メール/定型処理の自動化を、Pythonサンプルと手順で提案してください。"
    ),
}

# --- サイドバー ---
st.sidebar.title("設定")
expert = st.sidebar.selectbox("専門家を選択", list(EXPERT_PROMPTS.keys()))
model = st.sidebar.selectbox("モデル", ["gpt-4o-mini", "gpt-4o"], index=0)
temperature = st.sidebar.slider("Temperature（創造性）", 0.0, 1.0, 0.7, 0.1)

if st.sidebar.button("会話をリセット"):
    st.session_state.messages = []
    st.rerun()

# --- 履歴初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 画面ヘッダ ---
st.title("🤖 LLM専門家チャット")
st.caption(f"現在の専門家：{expert}")

# --- これまでの会話を表示 ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 入力欄 ---
user_input = st.chat_input("質問を入力してください（例：Excel作業を自動化するには？）")

if user_input:
    # ユーザ発話を保存＆表示
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # APIへ送るメッセージ（systemに専門家プロンプトを適用）
    messages_for_api = [{"role": "system", "content": EXPERT_PROMPTS[expert]}] + st.session_state.messages

    # ストリーミングで回答生成
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        stream = client.chat.completions.create(
            model=model,
            messages=messages_for_api,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_text += delta
            placeholder.markdown(full_text)

        # 履歴に保存
        st.session_state.messages.append({"role": "assistant", "content": full_text})
