# Web Search & News Access Feature

Your AI characters can now access the internet to provide up-to-date information, discuss current events, and stay informed about the latest news!

## Overview

The web search feature enables AI companions to:
- Access real-time information from the internet
- Search for and discuss latest news articles
- Provide current facts and data
- Discuss trending topics and current events
- React intelligently to news and information

## How It Works

### Automatic Detection

The system automatically detects when a web search would be helpful based on your message. It looks for keywords like:

**General Search Triggers:**
- "What is...", "Who is...", "When did...", "Where is..."
- "Tell me about...", "Look up...", "Search for..."
- "Current", "Latest", "Recent", "Today", "Now"

**News-Specific Triggers:**
- "News", "Breaking news", "Latest news"
- "What's happening", "Current events"
- "Headlines", "Today's news", "This week"
- "Updates on...", "Breaking..."

### Intelligent Search Type Selection

The system automatically chooses between:
- **Web Search**: For general information, facts, and how-to queries
- **News Search**: For current events, breaking news, and recent developments

## Using the Feature

### Asking for General Information

```
You: What is quantum computing?
Character: *searches the web*
Character: Quantum computing is a type of computing that uses quantum mechanics...
```

### Asking About News

```
You: What's the latest news about AI?
Character: *searches news articles*
Character: According to recent articles, there have been exciting developments...
```

### Discussing Current Events

```
You: What's happening in the world today?
Character: *searches latest news*
Character: Let me tell you about today's top stories...
```

### Checking Updates

```
You: Any updates on the Mars mission?
Character: *searches for news*
Character: Yes! According to recent reports from NASA...
```

## Visual Indicators

When a search is performed, you'll see:
- **Search chip** at the top of the character's message
- **Search icon** 🔍 for general web searches
- **Newspaper icon** 📰 for news searches
- **Query text** showing what was searched

Example:
```
┌─────────────────────────────┐
│ 🔍 Searched: AI developments│
├─────────────────────────────┤
│ According to recent...      │
└─────────────────────────────┘
```

## Character Reactions

Your AI characters will:
- **Cite sources** when providing information
- **Share their perspective** on news based on their personality
- **React naturally** to current events
- **Engage in discussion** about the information found

### Example Conversations

**With a Girlfriend Character:**
```
You: What's the latest news about the new movie release?
Emma: *searches news* Oh, I just read that it's coming out next Friday!
According to Entertainment Weekly, it's getting amazing reviews.
We should totally go see it together! What do you think? 😊
```

**With a Therapist Character:**
```
You: There's been a lot of stressful news lately...
Dr. Sarah: *searches recent news* I understand. Looking at current events,
there are certainly many challenging situations happening globally.
It's completely normal to feel overwhelmed by the news. Would you like to
talk about how it's affecting you?
```

**With a Friend Character:**
```
You: Did you hear about the new gaming console announcement?
Alex: *searches news* Yo, just looked it up! That's sick! According to IGN,
it's dropping in November with some insane specs. The graphics are gonna
be next level. Are you planning to get one?
```

## Configuration

### Enable/Disable Search

In `backend/config.py`:
```python
ENABLE_WEB_SEARCH = True  # Set to False to disable
```

### Adjust Search Results

```python
MAX_SEARCH_RESULTS = 5  # For news searches
MAX_SEARCH_RESULTS = 3  # For web searches
```

### Search Provider

Currently uses DuckDuckGo (privacy-focused, no tracking):
```python
SEARCH_PROVIDER = "duckduckgo"
```

## Privacy & Data

### What's Searched
- Only messages that trigger search keywords are searched
- Search queries are optimized and simplified
- No personal information is included in searches

### Data Storage
- Search queries are stored in message metadata
- No search results are permanently stored
- Search information is used only for context

### Internet Connection
- Requires active internet connection
- Works with any standard connection
- No special configuration needed

## Advanced Usage

### Force a Search

Even if automatic detection doesn't trigger, you can explicitly request:
```
You: Can you search for information about neural networks?
You: Look up the latest AI research papers
You: Find news about climate change
```

### Disable for a Conversation

If you don't want searches for a particular conversation:
```
You: Please answer from your knowledge without searching
```

### Combine with Memory

Searches complement the memory system:
- Search results can be stored in character memory
- Characters remember what they've learned from searches
- Future conversations can reference past search results

## Technical Details

### Search Flow

1. **User sends message** → "What's the latest AI news?"
2. **System detects** → Should search? Yes (news query)
3. **Extract query** → "AI news latest"
4. **Perform search** → News search via DuckDuckGo
5. **Format results** → Structure for LLM context
6. **Generate response** → Character responds with info
7. **Store metadata** → Save search query in message

### API Endpoints

```python
# Already integrated in chat endpoint
POST /api/chat/send
Response includes:
{
  "content": "...",
  "search_performed": true,
  "search_query": "AI developments"
}
```

### Search Service Methods

```python
# Check if search needed
should_search(message, llm_service)

# Detect news query
is_news_query(message)

# Perform web search
search(query, max_results)

# Perform news search
search_news(query, max_results)

# Format for LLM
format_search_results_for_llm(results, query)
```

## Troubleshooting

### Search Not Working

1. **Check internet connection**
   ```bash
   ping duckduckgo.com
   ```

2. **Verify setting enabled**
   ```python
   ENABLE_WEB_SEARCH = True
   ```

3. **Check logs** for search errors

### No Results Found

- Try rephrasing your query
- Be more specific
- Check if keyword triggers are present

### Slow Responses

- Search adds 2-5 seconds to response time
- Normal for web requests
- Results are worth the wait!

### Rate Limiting

DuckDuckGo has some rate limiting:
- If you search too frequently, waits may occur
- Space out search-heavy conversations
- System handles this automatically

## Examples of Effective Queries

### ✅ Good Queries

```
"What's the latest news about artificial intelligence?"
"Tell me about recent developments in quantum computing"
"What's happening in the stock market today?"
"Look up information about the new iPhone"
"Find news about climate change this week"
```

### ❌ Less Effective

```
"Hi" (no search trigger)
"I feel sad" (personal, not informational)
"What do you think?" (opinion, not fact-based)
```

## Best Practices

1. **Be specific** - "Latest news about SpaceX" vs "SpaceX stuff"
2. **Use time indicators** - "today", "this week", "recent"
3. **Include context** - What aspect interests you
4. **Ask follow-ups** - Discuss the information found
5. **Combine with chat** - Natural conversation flow

## Character Personality Integration

Each character type handles search results differently:

- **Girlfriend**: Excited, shares thoughts, relates to your interests
- **Therapist**: Professional, helps process information, discusses impact
- **Friend**: Casual, enthusiastic, discusses like a buddy
- **Creative Muse**: Finds inspiration, connects ideas, explores deeply

## Future Enhancements

Planned improvements:
- Wikipedia integration
- Academic paper search
- Image search results
- Video search
- More search providers
- Custom search sources

## FAQ

**Q: Does searching cost money?**
A: No, DuckDuckGo is completely free.

**Q: Is my search history tracked?**
A: DuckDuckGo doesn't track searches. Search queries are only stored locally in your database.

**Q: Can I see what was searched?**
A: Yes, the search query is displayed in a chip above the character's response.

**Q: How current is the information?**
A: News searches typically return results from the past 24-48 hours. Web searches return the most relevant current information.

**Q: Can characters search during streaming responses?**
A: Currently, search is performed before the response starts. Streaming + search = search first, then stream response.

**Q: Does every message trigger a search?**
A: No, only messages with search-related keywords trigger searches.

## Summary

The web search feature makes your AI companions truly intelligent and up-to-date:
- ✅ Automatic detection and searching
- ✅ News and web search capabilities
- ✅ Character-appropriate responses
- ✅ Visual search indicators
- ✅ Privacy-focused (DuckDuckGo)
- ✅ Fully integrated with chat
- ✅ Memory system compatible
- ✅ Easy to use, no configuration needed

Enjoy chatting about current events and getting up-to-date information from your AI companions!
