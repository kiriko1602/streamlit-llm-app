# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# --- 初期設定 ---
st.set_page_config(page_title="LLM専門家チャット", page_icon="🤖", layout="centered")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY が見つかりません。.env または Secrets を設定してから再実行してください。")
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

# -----------------------------
# 1) 要件対応：関数定義
#    入力テキストとラジオ選択値（専門家）を受け取り、戻り値でLLM回答を返す
# -----------------------------
def ask_llm(input_text: str, expert_choice: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """ラジオで選んだ専門家プロンプトと入力テキストを使ってLLM回答を返す"""
    messages = [
        {"role": "system", "content": EXPERT_PROMPTS[expert_choice]},
        {"role": "user", "content": input_text},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=False,  # 関数は戻り値で返す要件に合わせて非ストリーミング
    )
    return resp.choices[0].message.content.strip()

# --- サイドバー ---
st.sidebar.title("設定")
# 2) 要件対応：ラジオボタンで専門家選択
expert = st.sidebar.radio("専門家を選択（※要件のラジオ）", list(EXPERT_PROMPTS.keys()), index=0)
model = st.sidebar.selectbox("モデル", ["gpt-4o-mini", "gpt-4o"], index=0)
temperature = st.sidebar.slider("Temperature（創造性）", 0.0, 1.0, 0.7, 0.1)

if st.sidebar.button("会話をリセット"):
    st.session_state.clear()
    st.rerun()

# --- 画面ヘッダ＆要件2：概要と操作方法の表示 ---
st.title("🤖 LLM専門家チャット")
st.markdown(
    """
**＜アプリ概要＞**  
複数の「専門家」ロール（Pythonメンター／AI活用プランナー／業務自動化コンサルタント）を切り替えて、  
質問に最適化された回答を生成するWebアプリです。

**＜使い方＞**  
1. 右サイドバーの **「専門家を選択」**（ラジオボタン）で役割を選ぶ  
2. 必要に応じて **モデル** と **Temperature** を調整  
3. 下の入力欄に質問を入れて **送信**  
4. 生成された回答を確認（再質問も歓迎）
"""
)

# --- 入力欄＆実行 ---
user_input = st.text_input("質問を入力してください（例：Excelの月次レポート作業をPythonで自動化するには？）")
run = st.button("送信")

# --- 結果表示 ---
if run:
    if not user_input.strip():
        st.warning("質問を入力してください。")
    else:
        with st.spinner("回答を生成中..."):
            answer = ask_llm(user_input, expert, model=model, temperature=temperature)  # ←要件1：関数を利用
        st.subheader("回答")
        st.write(answer)
