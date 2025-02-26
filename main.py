from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from vertex_config import PROJECT_ID, LOCATION, API_ENDPOINT, ENDPOINT_ID

app = Flask(__name__)

# 서비스 계정 키 경로 설정
load_dotenv()

GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
# Vertex AI 초기화 설정

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    api_endpoint=API_ENDPOINT,
    credentials = credentials
    
)

# 기본 프롬프트 및 생성 설정
DEFAULT_PROMPT = (
    "개인정보처리방침을 6가지 항목이 있는 json 형식으로 내보낼거야. 항목은 다음과 같다 : "
    "개인정보 처리 목적, 개인정보 수집 항목, 개인정보 보유 기간, 개인정보의 제3자 제공(제공 대상, 제공 목적, 제공 항목), "
    "개인정보 처리위탁(수탁업체, 업무), 개인정보 파기"
)

GENERATION_CONFIG = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "OBJECT",
        "properties": {
            "response": {"type": "STRING"}
        }
    },
}

SAFETY_SETTINGS = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

def generate_summary(privacy_text, prompt=DEFAULT_PROMPT):
    """
    입력된 개인정보 텍스트를 바탕으로 Vertex AI를 이용해 JSON 형식의 응답을 생성합니다.
    """
    # Vertex AI Generative Model 생성 (system_instruction에 프롬프트를 전달)
    model = GenerativeModel(
        f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}",
        system_instruction=[prompt]
    )
    # 대화 세션 시작
    chat = model.start_chat()
    # 메시지를 전송하여 응답 생성
    response = chat.send_message(
        [privacy_text],
        generation_config=GENERATION_CONFIG,
        safety_settings=SAFETY_SETTINGS
    )
    return response

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    privacy_text = data.get("privacyText")
    
    if not privacy_text:
        return jsonify({"error": "No privacyText provided"}), 400

    # Vertex AI를 통해 요약(또는 지정한 JSON 형식) 생성
    summary = generate_summary(privacy_text)

    summary_text = summary.response if hasattr(summary, 'response') else str(summary)
    return jsonify({"summary": summary_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
