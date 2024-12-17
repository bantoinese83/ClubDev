import logging
import os
import re

import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerationConfig

logging.basicConfig(level=logging.INFO)


def configure_genai():
    api_key = os.getenv("GENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables")
    genai.configure(api_key=api_key)


def create_generation_config() -> GenerationConfig:
    return GenerationConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )


def create_model(model_name: str) -> GenerativeModel:
    return GenerativeModel(model_name)


def generate_text(model: GenerativeModel, config: GenerationConfig, prompt: str) -> str:
    response = model.generate_content(
        contents=prompt,
        generation_config=config,
    )
    if not response or not response.text:
        raise ValueError("Empty response from AI service")

    logging.info(f"Raw AI response: {response.text}")
    return response.text


def generate_metadata_from_code(model: GenerativeModel, config: GenerationConfig, code_script: str) -> dict:
    prompt = (
        f"Generate metadata for the following code script:\n\n{code_script}\n\n"
        f"Metadata should include title (max 100 characters), description (max 200 characters), tags (comma-separated), use cases (max 200 characters), "
        f"grade (A,B,C,D,F based on code quality), instructions (max 200 characters), framework, license, and language. Use the following format:\n\n"
        f"Title: <title>\n"
        f"Description: <description>\n"
        f"Tags: <tag1>, <tag2>, <tag3>\n"
        f"Use Cases: <use_case1>, <use_case2>\n"
        f"Grade: <grade>\n"
        f"Instructions: <instructions>\n"
        f"Framework: <framework>\n"
        f"License: <license>\n"
        f"Language: <language>\n"
        "No markdown formatting is required, just plain text.\n"
    )
    response = generate_text(model, config, prompt)

    # Regex to extract metadata
    metadata = {}

    title_match = re.search(r"Title:\s*(.+)", response)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    description_match = re.search(r"Description:\s*(.+)", response)
    if description_match:
        metadata["description"] = description_match.group(1).strip()

    tags_match = re.search(r"Tags:\s*(.+)", response)
    if tags_match:
        metadata["tags"] = [tag.strip() for tag in tags_match.group(1).split(",")]

    use_cases_match = re.search(r"Use Cases:\s*(.+)", response)
    if use_cases_match:
        metadata["use_cases"] = [use_case.strip() for use_case in use_cases_match.group(1).split(",")]

    grade_match = re.search(r"Grade:\s*(.+)", response)
    if grade_match:
        metadata["grade"] = grade_match.group(1).strip()

    instructions_match = re.search(r"Instructions:\s*(.+)", response)
    if instructions_match:
        metadata["instructions"] = instructions_match.group(1).strip()

    framework_match = re.search(r"Framework:\s*(.+)", response)
    if framework_match:
        metadata["framework"] = framework_match.group(1).strip()

    license_match = re.search(r"License:\s*(.+)", response)
    if license_match:
        metadata["license"] = license_match.group(1).strip()

    language_match = re.search(r"Language:\s*(.+)", response)
    if language_match:
        metadata["language"] = language_match.group(1).strip()

    return metadata


def revise_blog_entry(model: GenerativeModel, config: GenerationConfig, blog_post: str) -> dict:
    prompt = (
        f"Revise and improve the following blog post:\n\n{blog_post}\n\n"
        "The revised version should be:\n"
        "- More engaging and captivating for the reader\n"
        "- Clear and concise, avoiding any ambiguity\n"
        "- Well-structured with a logical flow\n"
        "- Free of grammatical and spelling errors\n"
        "- Enhanced with better vocabulary and varied sentence structures\n"
        "- Consistent in tone and style\n"
        "- Informative and accurate\n"
        "Please provide the revised version below, including a title, tags, and category.\n\n"
        "Title: <title>\n"
        "Tags: <tag1>, <tag2>, <tag3>\n"
        "Category: <category>\n"
        "Revised Blog Post:\n"
        "No markdown formatting is required, just plain text.\n"

    )
    response = generate_text(model, config, prompt)
    logging.info(f"AI response: {response}")

    # Extract title, tags, category, and revised blog post using regex
    revised_content = {}

    title_match = re.search(r"Title:\s*(.+)", response)
    if title_match:
        revised_content["title"] = title_match.group(1).strip()

    tags_match = re.search(r"Tags:\s*(.+)", response)
    if tags_match:
        revised_content["tags"] = [tag.strip() for tag in tags_match.group(1).split(",")]

    category_match = re.search(r"Category:\s*(.+)", response)
    if category_match:
        revised_content["category"] = category_match.group(1).strip()

    blog_post_match = re.search(r"Revised Blog Post:\s*(.+)", response, re.DOTALL)
    if blog_post_match:
        revised_content["content"] = blog_post_match.group(1).strip()

    revised_content["content"] = clean_revised_blog_post(revised_content["content"])

    return revised_content


def clean_revised_blog_post(content: str) -> str:
    return content.replace("**", "").replace("*", "")
