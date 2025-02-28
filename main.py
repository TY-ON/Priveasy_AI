from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import os
from google.oauth2 import service_account
from vertex_config import PROJECT_ID, LOCATION, API_ENDPOINT, ENDPOINT_ID
import json

app = Flask(__name__)

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
    model = GenerativeModel(
        f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}",
        system_instruction=[prompt]
    )
    chat = model.start_chat()
    response = chat.send_message(
        [privacy_text],
        generation_config=GENERATION_CONFIG,
        safety_settings=SAFETY_SETTINGS
    )
    return response

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    data = request.get_json()
    privacy_text = data.get("privacyText")
    
    if not privacy_text:
        return jsonify({"error": "No privacyText provided"}), 400

    summary = generate_summary(privacy_text)
    
    try:
        # GenerationResponse 객체에서 실제 텍스트를 추출합니다.
        summary_text = summary.text
        # 첫번째 JSON 파싱: 최상위 JSON 객체 추출
        outer_json = json.loads(summary_text)
        # "response" 키에 해당하는 값은 내부 JSON 문자열입니다.
        inner_json_string = outer_json.get("response", "{}")
        # 두번째 JSON 파싱: 내부 JSON 문자열을 파싱하여 최종 JSON 객체 생성
        parsed_response = json.loads(inner_json_string)
    except Exception as e:
        # 파싱 실패 시, 원본 텍스트와 에러 메시지를 포함하여 반환합니다.
        parsed_response = {
            "error": "Failed to parse JSON",
            "details": str(e),
            "raw": summary.text
        }
    
    return jsonify(parsed_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
