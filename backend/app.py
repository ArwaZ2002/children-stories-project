from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import os
import uuid
import re
from datetime import datetime
from urllib.parse import quote

load_dotenv()

frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend_html')
images_dir = os.path.join(os.path.dirname(__file__), 'generated_images')
os.makedirs(images_dir, exist_ok=True)

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
POLLINATIONS_IMAGE_API = "https://image.pollinations.ai/prompt"

stories = []
story_id_counter = 1

CHARACTER_PRONOUNS = {
    "animal": {"subject": "they", "object": "them", "possessive": "their", "reflexive": "themselves"},
    "princess": {"subject": "she", "object": "her", "possessive": "her", "reflexive": "herself"},
    "prince": {"subject": "he", "object": "him", "possessive": "his", "reflexive": "himself"},
    "superhero": {"subject": "they", "object": "them", "possessive": "their", "reflexive": "themselves"},
    "dragon": {"subject": "they", "object": "them", "possessive": "their", "reflexive": "themselves"},
    "robot": {"subject": "they", "object": "them", "possessive": "their", "reflexive": "themselves"},
    "fairy": {"subject": "she", "object": "her", "possessive": "her", "reflexive": "herself"},
    "knight": {"subject": "he", "object": "him", "possessive": "his", "reflexive": "himself"},
    "mermaid": {"subject": "she", "object": "her", "possessive": "her", "reflexive": "herself"},
    "pirate": {"subject": "he", "object": "him", "possessive": "his", "reflexive": "himself"},
    "wizard": {"subject": "he", "object": "him", "possessive": "his", "reflexive": "himself"},
}

CHARACTER_NAMES = {
    "animal": "a curious little animal",
    "princess": "a kind princess",
    "prince": "a brave prince",
    "superhero": "a mighty superhero",
    "dragon": "a friendly dragon",
    "robot": "a clever robot",
    "fairy": "a magical fairy",
    "knight": "a noble knight",
    "mermaid": "a beautiful mermaid",
    "pirate": "an adventurous pirate",
    "wizard": "a wise wizard",
}


def get_pronouns(character, gender):
    if character in ("princess", "fairy", "mermaid"):
        return CHARACTER_PRONOUNS[character]
    if character in ("prince", "knight", "pirate", "wizard"):
        return CHARACTER_PRONOUNS[character]
    if gender == "female":
        return {"subject": "she", "object": "her", "possessive": "her", "reflexive": "herself"}
    elif gender == "male":
        return {"subject": "he", "object": "him", "possessive": "his", "reflexive": "himself"}
    return CHARACTER_PRONOUNS.get(character, CHARACTER_PRONOUNS["animal"])


def generate_story_prompt(age, moral_lesson, character, gender):
    age_ranges = {"4": "4-5", "5-6": "5-6", "7-8": "7-8"}
    age_group = age_ranges.get(age, "4-5")
    pronouns = get_pronouns(character, gender)
    char_name = CHARACTER_NAMES.get(character, "a curious character")

    return f"""
You are a talented children's author who creates warm, imaginative, emotionally engaging stories for young children.

Write ONE original children's story using the following details:

AGE: {age_group}
MAIN CHARACTER: {char_name}
PRONOUNS: {pronouns['subject']} / {pronouns['object']} / {pronouns['possessive']} / {pronouns['reflexive']}
MORAL LESSON: {moral_lesson}

Your goal is not simply to explain the moral lesson. Create a story that makes the child experience the lesson through the character's actions, feelings, choices, and consequences.

LANGUAGE AND AGE APPROPRIATENESS:

For ages 4-5:
- Use very simple vocabulary and short sentences.
- Use familiar everyday words.
- Keep ideas concrete and easy to understand.
- Use repetition naturally when it makes the story fun.
- Focus on clear emotions and actions.
- Avoid abstract explanations and complicated reasoning.
- Make dialogue short, playful, and easy to follow.

For ages 5-6:
- Use simple but slightly richer vocabulary.
- Allow somewhat longer sentences and more descriptive details.
- Introduce simple cause-and-effect relationships.
- Let the character experience a small dilemma or mistake.
- Use dialogue to show emotions and personality.

For ages 7-8:
- Use richer vocabulary while remaining child-friendly.
- Allow longer and more varied sentences.
- Give the character a meaningful challenge or dilemma.
- Develop emotions, motivations, and consequences more deeply.
- Include more descriptive settings and natural dialogue.
- Encourage reflection without becoming overly instructional.

STORY QUALITY:

- Begin with an interesting situation that immediately gives the child a reason to keep reading.
- Give the main character a clear personality, desire, or goal.
- Create one central problem related naturally to the moral lesson.
- Create one central conflict and develop it throughout the story. Do not introduce unrelated events, characters, or problems merely to make the story longer. Every major event should contribute to the character's journey and the moral lesson.
- Let the character make a believable mistake, face a challenge, or make a difficult choice.
- Show what happens because of the character's choice.
- Give the character an opportunity to understand and make a better choice.
- Resolve the conflict in a satisfying and positive way.
- End with a warm, memorable moment.

MORAL LESSON:

The moral lesson is:

"{moral_lesson}"

Do not repeatedly state or explain the moral.
Do not make the story sound like a lesson or lecture.
Instead, let the child understand the lesson by watching what happens to the character.

WRITING STYLE:

- Warm
- Imaginative
- Gentle
- Natural
- Engaging
- Emotionally positive
- Age-appropriate

Use vivid but simple descriptions that help children imagine the world.

Include natural dialogue between characters.

Make the characters feel like real personalities rather than teaching devices.

Avoid:
- Preachy language
- Adult vocabulary
- Long explanations
- Repeated moral statements
- Unnecessary complexity
- Dark or frightening scenes
- Violence or graphic content
- Sudden unrealistic changes in character behavior
- Generic endings such as "and they lived happily ever after" unless it feels natural

The story should feel like a real children's story written by a caring, creative author.

LENGTH:

Write approximately 300-400 words.
Prioritize story quality, coherence, and age appropriateness over filling the word count.

OUTPUT:

Return a JSON object containing exactly:
- "title"
- "story"

The story should contain natural paragraph breaks using \\n\\n.
"""


def generate_image_prompts(character, moral_lesson, gender):
    char_name = CHARACTER_NAMES.get(character, "a child")

    character_description = (
        f"{char_name}, a {gender} child, "
        "friendly and expressive face, cute cartoon appearance"
    )

    style = (
        "children's storybook illustration, colorful 2D cartoon style, "
        "soft lighting, warm atmosphere, clean shapes, "
        "detailed background, high quality, charming and playful"
    )

    return [
        (
            f"{character_description} in a magical colorful forest, "
            f"surrounded by glowing flowers, friendly animals and "
            f"tiny sparkling lights, looking curious and excited. "
            f"{style}, wide composition, full body"
        ),

        (
            f"{character_description} experiencing a moment that teaches "
            f"the lesson of {moral_lesson}, showing a clear positive action "
            f"and an expressive facial expression. "
            f"{style}, storytelling scene, medium shot"
        ),

        (
            f"{character_description} happily smiling after learning "
            f"the importance of {moral_lesson}, surrounded by friends "
            f"in a bright cheerful environment. "
            f"{style}, joyful atmosphere, warm lighting, full body"
        ),
    ]


def query_openrouter_story(prompt):
    if not OPENROUTER_API_KEY:
        return None
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        if response.status_code == 200:
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()
            if text:
                return text
        return None
    except Exception as e:
        print(f"Story generation error: {e}")
        return None


def query_pollinations_image(prompt):
    for attempt in range(3):
        try:
            encoded_prompt = quote(prompt)
            url = f"{POLLINATIONS_IMAGE_API}/{encoded_prompt}?width=512&height=512&nologo=true&seed={uuid.uuid4().hex[:8]}"
            response = requests.get(url, timeout=60)
            if response.status_code == 200 and response.content:
                return response.content
        except Exception as e:
            print(f"Image generation attempt {attempt + 1} error: {e}")
    return None


def parse_story_response(text):
    if not text:
        return None, None

    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            import json
            data = json.loads(json_match.group())
            title = data.get("title", "").strip()
            story = data.get("story", "").strip()
            if title and story:
                return title, story
        except json.JSONDecodeError:
            pass

    lines = text.strip().split("\n", 1)
    if len(lines) >= 2:
        title = lines[0].strip().strip('"').strip()
        story = lines[1].strip()
        return title, story

    return "A Magical Story", text.strip()


def save_image(image_data, story_id, index):
    filename = f"story_{story_id}_img_{index}.png"
    filepath = os.path.join(images_dir, filename)
    with open(filepath, "wb") as f:
        f.write(image_data)
    return f"/generated_images/{filename}"


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Story API is running"})


@app.route("/api/generate", methods=["POST"])
def generate():
    global story_id_counter

    data = request.get_json()
    age = data.get("age", "")
    moral_lesson = data.get("moralLesson", "")
    character = data.get("character", "")
    gender = data.get("gender", "")

    if not all([age, moral_lesson, character]):
        return jsonify({
            "error": "Missing required fields: age, moralLesson, character"
        }), 400

    story_prompt = generate_story_prompt(age, moral_lesson, character, gender)
    story_text = query_openrouter_story(story_prompt)

    if story_text:
        title, story_body = parse_story_response(story_text)
    else:
        title = f"The {character.replace('_', ' ').title()} Story"
        story_body = f"Once upon a time, there was a wonderful character who learned about {moral_lesson}. Through their journey, they discovered that {moral_lesson} makes the world a better place. And they lived happily ever after."

    image_prompts = generate_image_prompts(character, moral_lesson, gender)
    image_urls = []

    for i, img_prompt in enumerate(image_prompts):
        img_data = query_pollinations_image(img_prompt)
        if img_data:
            img_url = save_image(img_data, story_id_counter, i)
            image_urls.append(img_url)
        else:
            image_urls.append(f"https://via.placeholder.com/512x512?text=Story+Illustration+{i+1}")

    story = {
        "id": f"story-{story_id_counter}",
        "title": title,
        "age": age,
        "moralLesson": moral_lesson,
        "character": character,
        "gender": gender,
        "storyText": story_body,
        "imageUrls": image_urls,
        "createdAt": datetime.now().isoformat(),
        "favorite": False,
    }

    story_id_counter += 1
    stories.append(story)

    return jsonify({"success": True, "story": story})


@app.route("/api/gallery", methods=["GET"])
def gallery():
    return jsonify({"stories": stories})


@app.route("/api/favorites/<story_id>", methods=["POST"])
def toggle_favorite(story_id):
    story = next((s for s in stories if s["id"] == story_id), None)

    if not story:
        return jsonify({"error": "Story not found"}), 404

    story["favorite"] = not story["favorite"]
    return jsonify({"story": story})


@app.route("/generated_images/<path:filename>")
def serve_image(filename):
    return send_from_directory(images_dir, filename)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_html(path):
    if path != "" and os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    else:
        return send_from_directory(frontend_dir, 'index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
