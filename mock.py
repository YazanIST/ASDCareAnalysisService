from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List
import base64

load_dotenv()
app = FastAPI()

OPENAI_MODEL = "gpt-4o"

TESTING_IMAGE_PATH = "sun_simple_drawing.jpg"
IMAGE_BASE64 = base64.b64encode(open(TESTING_IMAGE_PATH, "rb").read()).decode("utf-8")

class GenerateSubjectRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    previous_generated_games_subjects: List[str]

get_subject_prompt = "Subject prompt content"
get_bg_image_prompt = "Background image prompt content"
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
    # Mocked response for testing
    subject = "Mocked Subject"
    image = "MockedBase64ImageString"
    return {"subject": subject, "image": IMAGE_BASE64}

class GetFeedbackRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    drawing_subject: str
    drawing: str  # Assuming base64 encoded image

get_feedback_prompt = "Feedback prompt content"
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
    # Mocked response for testing
    feedback = "Mocked Feedback"
    return {"feedback": feedback}

class FinishGameRequest(BaseModel):
    child_age: int
    parent_instructions: List[str]
    doctor_instructions: List[str]
    drawing_subject: str
    drawing: str  # Assuming base64 encoded image
    old_ml_feedback_on_child_level: str

get_summary_prompt = "Summary prompt content"
get_summary_prompt_template = "Child age: {}\nParent instructions:\n{}\nDoctor instructions:\n{}\nDrawing subject: {}"

def fill_get_summary_prompt_template(request: FinishGameRequest):
    return get_summary_prompt_template.format(
        request.child_age,
        '\n'.join(f'- {instruction}' for instruction in request.parent_instructions),
        '\n'.join(f'- {instruction}' for instruction in request.doctor_instructions),
        request.drawing_subject
    )

get_encouraging_feedback_prompt = "Encouraging feedback prompt content"
get_encouraging_feedback_template = "Child age: {}\nDrawing subject: {}"

def fill_get_encouraging_feedback_template(request: FinishGameRequest):
    return get_encouraging_feedback_template.format(
        request.child_age,
        request.drawing_subject
    )

@app.post("/finish_game")
def finish_game(request: FinishGameRequest):
    # Mocked responses for testing
    summary = "Mocked Summary"
    encouraging_feedback = "Mocked Encouraging Feedback"
    return {"summary": summary, "encouraging_feedback": encouraging_feedback, "new_ml_feedback_on_child_level": "Mocked New ML Feedback"}
