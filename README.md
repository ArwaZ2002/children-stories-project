# StoryWeaver — AI-Powered Children's Story Generator

Generate unique, illustrated children's stories with moral lessons using AI.

## Features

- AI story generation with customizable age group, character, and moral lesson
- AI-generated story illustrations
- Save favorites to a personal library
- Export stories as PDF
- Responsive, professional UI

## Tech Stack

- **Backend:** Python, Flask
- **AI:** OpenRouter API (story generation), Pollinations AI (image generation)
- **Frontend:** HTML, CSS, JavaScript

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Set your OpenRouter API key in `backend/.env`:
   ```
   OPENROUTER_API_KEY=sk-or-your-key-here
   ```
4. Run the backend: `python backend/app.py`
5. Open `http://localhost:5000` in your browser

## API Endpoints

- `POST /api/generate` — Generate a new story
- `GET /api/gallery` — List all stories
- `POST /api/favorites/<story_id>` — Toggle favorite status
