from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI
from openai import OpenAI
from typing import List
import requests
import base64

load_dotenv()
app = FastAPI()
client = OpenAI()

OPENAI_MODEL = "gpt-4o"

class GenerateSubjectRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    previous_generated_games_subjects: List[str]

get_subject_prompt = open('prompts/generate_subject/get_subject.txt').read()
get_bg_image_prompt = open('prompts/generate_subject/get_bg_image.txt').read()
generate_subject_request_template = "Child age: {}\nParent instructions:\n{}\nDoctor instructions:\n{}\nPrevious generated games subjects:\n{}"
def fill_generate_subject_request_template(request: GenerateSubjectRequest):
    return generate_subject_request_template.format(
        request.child_age,
        '\n'.join(f'- {instruction}' for instruction in request.parent_instructions),
        '\n'.join(f'- {instruction}' for instruction in request.doctor_instructions),
        '\n'.join(f'- {subject}' for subject in request.previous_generated_games_subjects)
    )

@app.post("/generate_subject")
def generate_subject(request: GenerateSubjectRequest):
    subject = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": get_subject_prompt},
            {
                "role": "user",
                "content": fill_generate_subject_request_template(request)
            }
        ]
    ).choices[0].message.content
    image_url = client.images.generate(
        model="dall-e-3",
        prompt=get_bg_image_prompt + "\nDrawing subject: " + subject,
        size="1024x1792",
        quality="standard",
        n=1,
    ).data[0].url
    image = base64.b64encode(requests.get(image_url).content).decode('utf-8')
    return {"subject": subject, "image": image}

class GetFeedbackRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    drawing_subject: str
    drawing: str  # Assuming base64 encoded image

get_feedback_prompt = open('prompts/get_feedback/get_feedback.txt').read()
get_feedback_request_template = "Child age: {}\nParent instructions:\n{}\nDoctor instructions:\n{}\nDrawing subject: {}"
def fill_get_feedback_request_template(request: GetFeedbackRequest):
    return get_feedback_request_template.format(
        request.child_age,
        '\n'.join(f'- {instruction}' for instruction in request.parent_instructions),
        '\n'.join(f'- {instruction}' for instruction in request.doctor_instructions),
        request.drawing_subject
    )

@app.post("/get_feedback")
def get_feedback(request: GetFeedbackRequest):
    feedback = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": get_feedback_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": fill_get_feedback_request_template(request)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{request.drawing}"}},
                ]
            }
        ]
    ).choices[0].message.content
    return {"feedback": feedback}

class FinishGameRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    drawing_subject: str
    drawing: str  # Assuming base64 encoded image

get_summary_prompt = open('prompts/finish_game/get_summary.txt').read()
get_summary_prompt_template = "Child age: {}\nParent instructions:\n{}\nDoctor instructions:\n{}\nDrawing subject: {}"
def fill_get_summary_prompt_template(request: FinishGameRequest):
    return get_summary_prompt_template.format(
        request.child_age,
        '\n'.join(f'- {instruction}' for instruction in request.parent_instructions),
        '\n'.join(f'- {instruction}' for instruction in request.doctor_instructions),
        request.drawing_subject
    )

get_encouraging_feedback_prompt = open('prompts/finish_game/get_encouraging_feedback.txt').read()
get_encouraging_feedback_template = "Child age: {}\nDrawing subject: {}"
def fill_get_encouraging_feedback_template(request: FinishGameRequest):
    return get_encouraging_feedback_template.format(
        request.child_age,
        request.drawing_subject
    )

@app.post("/finish_game")
def finish_game(request: FinishGameRequest):
    summary = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": get_summary_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": fill_get_summary_prompt_template(request)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{request.drawing}"}},
                ]
            }
        ]
    ).choices[0].message.content

    encouraging_feedback = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": get_encouraging_feedback_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": fill_get_encouraging_feedback_template(request)},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{request.drawing}"}},
                ]
            }
        ]
    ).choices[0].message.content

    return {"summary": summary, "encouraging_feedback": encouraging_feedback}
