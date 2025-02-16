import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_embedding(text, model="text-embedding-ada-002"):
    """
    Get vector embedding for a text using OpenAI's API.
    """
    try:
        response = openai.Embedding.create(
            input=text,
            model=model
        )
        embedding = response['data'][0]['embedding']
        return embedding
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")


def extract_structured_data(text, role="resume"):
    """
    Use ChatCompletion with gpt-3.5-turbo to parse text into structured JSON.
    """
    if role == "resume":
        system_prompt = (
            "You are an AI assistant that can parse resumes into structured JSON. "
            "Required fields: summary, experience, skills, education, projects, certifications. "
            "Output valid JSON only."
        )
    else:
        system_prompt = (
            "You are an AI assistant that can parse job descriptions into structured JSON. "
            "Required fields: about_company, role_overview, qualifications, location, job_type, benefits. "
            "Output valid JSON only."
        )
    
    user_prompt = f"Extract and summarize the following text in JSON format:\n\n{text}\n\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
    )
    structured_response = response["choices"][0]["message"]["content"]
    return structured_response