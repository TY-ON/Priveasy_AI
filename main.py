from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
import os

app = Flask(__name__)

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
API_ENDPOINT = os.environ.get("API_ENDPOINT")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")


vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    api_endpoint=API_ENDPOINT
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

    summary = generate_summary(privacy_text)
    # GenerationResponse 객체에서 생성된 텍스트를 추출합니다.
    summary_text = summary.response if hasattr(summary, 'response') else str(summary)
    return jsonify({"summary": summary_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
