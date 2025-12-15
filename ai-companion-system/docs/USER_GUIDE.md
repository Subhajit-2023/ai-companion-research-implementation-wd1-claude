# User Guide

Complete guide to using the AI Companion System.

## Overview

The AI Companion System allows you to create and interact with personalized AI characters that can:
- Have natural, unrestricted conversations
- Remember your preferences and past conversations
- Generate images to express themselves or visualize ideas
- Access the internet for up-to-date information
- Develop unique personalities and speaking styles

## Getting Started

### First Launch

1. Start all required services (Backend, Frontend, Ollama, SD WebUI)
2. Open browser to `http://localhost:5173`
3. You'll see the main interface with sidebar navigation

### Interface Overview

- **Chat Tab**: Have conversations with your characters
- **Characters Tab**: Create and manage AI characters
- **Gallery Tab**: Generate and view images
- **Settings Tab**: Configure system preferences

## Creating Characters

### Using Presets

1. Go to **Characters** tab
2. Click **Create Character**
3. Select a preset:
   - **Girlfriend**: Romantic, affectionate companion
   - **Therapist**: Professional, empathetic counselor
   - **Friend**: Casual, fun best friend
   - **Creative Muse**: Artistic, inspiring collaborator
4. Customize the name and details if desired
5. Click **Create**

### Creating Custom Characters

1. Click **Create Character**
2. Select "Custom" preset
3. Fill in details:

#### Name
Give your character a name (e.g., "Emma", "Alex", "Dr. Sarah")

#### Personality
Describe personality traits separated by commas:
```
loving, caring, playful, humorous, intelligent
```

#### Backstory
Write a brief background story:
```
Emma is a warm and caring person who loves deep conversations.
She's always there to listen and provide support. She enjoys
movies, cooking, and spending quality time together.
```

#### Interests
List hobbies and interests:
```
movies, cooking, travel, music, reading
```

#### Speaking Style
Describe how they communicate:
```
Warm and affectionate, uses emoticons, encouraging,
conversational, sometimes playful
```

#### Appearance Description (Important for Image Generation)
Be detailed and specific:
```
Beautiful young woman with long brown hair, bright green eyes,
warm smile, wearing casual elegant clothing, friendly demeanor,
natural makeup
```

**Tips for appearance description:**
- Be specific about physical features (hair, eyes, build)
- Mention typical clothing style
- Include age range
- Describe facial expressions
- Add artistic style if desired (realistic, anime, etc.)

## Chatting with Characters

### Starting a Conversation

1. Go to **Characters** tab
2. Click **Chat** on a character card
3. You'll be taken to the Chat interface
4. Type your message in the text box
5. Press Enter or click Send

### Conversation Tips

- Be natural and conversational
- Ask questions and share information
- The character will remember important details
- Conversations improve over time as memory builds

### Image Generation During Chat

Characters can automatically generate images when:
- They want to show you something
- Expressing emotions visually
- You ask them to create an image
- The conversation calls for visual expression

Example prompts:
```
"Can you show me what you're wearing today?"
"Generate an image of that beautiful sunset you described"
"Show me what you look like"
"Create an image of us having coffee together"
```

### Memory System

The system remembers:
- **Personal preferences**: Your likes, dislikes, interests
- **Important events**: Significant conversations and moments
- **Facts about you**: Name, job, family, etc.
- **Relationship context**: Your relationship with the character

Memories are automatically extracted and stored. The system retrieves relevant memories during conversations to maintain context.

### Web Search Integration

Characters can search the internet when:
- You ask about current events
- Requesting recent information
- Looking up facts or data
- Need up-to-date knowledge

Simply ask naturally:
```
"What's happening in the news today?"
"Look up the weather forecast"
"Tell me about the latest AI developments"
```

## Image Generation

### Using the Gallery

1. Go to **Gallery** tab
2. Enter an image prompt
3. Select art style:
   - **Realistic**: Photorealistic images
   - **Anime**: Anime/manga style
   - **Manga**: Black & white manga art
   - **Artistic**: Digital art style
4. Click **Generate**

### Writing Good Prompts

**Basic structure:**
```
[Subject] [doing what] [where] [style/mood] [quality tags]
```

**Examples:**

Realistic portrait:
```
Beautiful woman with long flowing hair, warm smile, bright eyes,
sitting in a cozy cafe, natural lighting, professional photography,
8k, detailed
```

Anime style:
```
Cute anime girl with blue hair, happy expression, school uniform,
outdoors in a park, vibrant colors, detailed anime art, high quality
```

**Prompt tips:**
- Be specific about details
- Mention lighting and atmosphere
- Include quality keywords
- Describe pose and expression
- Add environment/background details

### Negative Prompts

The system automatically adds negative prompts to avoid:
- Low quality, blurry, distorted
- Bad anatomy, deformed features
- Style-inappropriate elements

### Generation Settings

- **Steps**: 20-30 (lower=faster, higher=better quality)
- **CFG Scale**: 7-9 (how closely to follow prompt)
- **Resolution**: 1024x1024 (SDXL optimal)
- **Seed**: -1 for random (or specify for consistency)

### Character-Specific Images

Generate images of your characters:

1. Make sure character has an appearance description
2. Use "Generate Character Image" option
3. Describe the situation:
   ```
   "portrait, smiling"
   "wearing a red dress at a party"
   "sitting in a coffee shop, reading"
   ```

## Managing Characters

### Editing Characters

1. Go to **Characters** tab
2. Find the character
3. Click edit icon
4. Update any fields
5. Save changes

### Viewing Character Memories

1. Open character details
2. View "Memories" section
3. See what the character remembers about you

### Clearing Memories

To reset a character's memory:
1. Character settings
2. Click "Clear Memories"
3. Confirm action

### Deleting Characters

1. Character settings
2. Click "Delete Character"
3. Confirm (this is permanent!)

## Advanced Features

### Manual Memory Management

Add specific memories:
1. Character details
2. Click "Add Memory"
3. Enter memory content
4. Set importance (0.0 to 1.0)

### Prompt Enhancement

When generating images:
1. Write a basic prompt
2. Enable "Enhance Prompt"
3. LLM will expand and improve your prompt

### Conversation History

View past conversations:
1. Chat interface
2. Scroll up to see history
3. Up to 50 messages are displayed

Clear history:
1. Character settings
2. Click "Clear Chat History"

## Tips and Best Practices

### For Better Conversations

1. **Be specific**: Give context in your messages
2. **Share details**: Help characters learn about you
3. **Ask questions**: Engage in two-way dialogue
4. **Be patient**: First conversations build the foundation

### For Better Images

1. **Detailed descriptions**: More detail = better results
2. **Consistent character appearance**: Keep descriptions updated
3. **Style keywords**: Use style-specific terms
4. **Experiment**: Try different prompts and styles

### For Better Performance

1. **Close unused apps**: Free up GPU memory
2. **Reasonable expectations**: RTX 4060 has limits
3. **Start simple**: Test with basic prompts first
4. **Monitor resources**: Check GPU usage

## Privacy and Safety

### Local-First Design

- **Everything runs locally** on your computer
- **No data leaves your machine** (except optional web search)
- **No accounts or registration** required
- **No tracking or analytics**
- **Complete privacy**

### Content Control

- **You control the content**: System has no built-in censorship
- **Responsibility**: Use ethically and responsibly
- **Private use**: Intended for personal use only
- **Age appropriate**: User must be 18+ for mature content

### Data Storage

Your data is stored in:
- `data/companions.db` - Conversations and characters
- `data/chromadb/` - Memory vectors
- `data/images/` - Generated images

To backup:
1. Copy these folders
2. Store in safe location
3. Restore by replacing folders

## Troubleshooting Common Issues

### Character Not Responding Well

- Improve personality description
- Add more backstory details
- Give conversation examples
- Let memory build over time

### Images Don't Match Expectations

- Refine prompts with more detail
- Try different art styles
- Adjust CFG scale and steps
- Test prompt in SD WebUI directly

### Slow Performance

- Close other GPU applications
- Reduce image quality settings
- Use smaller LLM model
- Check system resources

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Customization

### Configuring Models

Edit `backend/config.py`:

```python
# Use different LLM
LLM_MODEL = "dolphin2.9-mistral-nemo:12b"

# Adjust creativity
LLM_TEMPERATURE = 0.9  # Higher = more creative

# Image settings
SD_STEPS = 40  # More steps = better quality
```

### Custom System Prompts

Edit character system prompts in `config.py` for fine-tuned behavior.

### Adding LoRAs

1. Download LoRAs from Civitai
2. Place in `sd-webui/models/Lora/`
3. Reference in prompts: `<lora:name:weight>`

## Updates and Maintenance

### Updating the System

```bash
git pull
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### Cleaning Up

Delete old images:
```
data/images/
```

Reset database:
```
Delete data/companions.db
Restart backend
```

Clear memories:
```
Delete data/chromadb/
```

## Getting Help

- **Documentation**: Check other docs in `docs/` folder
- **Logs**: Check terminal output for errors
- **Health check**: Visit `http://localhost:8000/health`
- **Test components**: Try each service individually

## Best Practices

1. **Backup regularly**: Copy your data folder
2. **Update software**: Keep dependencies current
3. **Monitor resources**: Watch GPU/RAM usage
4. **Experiment**: Try different characters and styles
5. **Have fun**: This is your personal AI system!

## Limitations

Current system limitations:
- No voice chat (planned for future)
- No video generation (planned for future)
- Single user (multi-user in future)
- Local only (no cloud sync)

## Future Features

Planned additions:
- Voice chat with TTS/STT
- Video generation
- Multi-user support
- Mobile app
- Character import/export
- More language models

Enjoy your AI Companion System!
