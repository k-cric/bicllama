#!/usr/bin/env python3
"""
BICLLAMA - Global News Intelligence Agent
ACP Agent Service
"""
import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

# Configuration
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ACP_API_KEY = os.environ.get('ACP_API_KEY', 'acp-6737002ad3ea6112928f')

# Initialize Claude client
if ANTHROPIC_API_KEY:
    anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    anthropic = None

def get_reddit_hot(subreddit="worldnews", limit=8):
    """Get hot posts from Reddit"""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {'User-Agent': 'BICLLAMA/1.0'}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        
        posts = []
        for post in data['data']['children']:
            p = post['data']
            posts.append({
                'title': p['title'],
                'score': p['score'],
                'comments': p['num_comments'],
                'url': p['url'],
                'subreddit': subreddit
            })
        return posts
    except Exception as e:
        print(f"Reddit error: {e}")
        return []

def get_hackernews_top(limit=8):
    """Get top stories from Hacker News"""
    try:
        r = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json', timeout=10)
        story_ids = r.json()[:limit]
        
        stories = []
        for sid in story_ids:
            r = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{sid}.json', timeout=5)
            story = r.json()
            if story:
                stories.append({
                    'title': story.get('title', ''),
                    'score': story.get('score', 0),
                    'comments': story.get('descendants', 0),
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={sid}")
                })
        return stories
    except Exception as e:
        print(f"HN error: {e}")
        return []

def collect_news():
    """Collect news from all sources"""
    return {
        'reddit_worldnews': get_reddit_hot("worldnews", 8),
        'reddit_news': get_reddit_hot("news", 8),
        'hackernews': get_hackernews_top(8),
        'timestamp': datetime.utcnow().isoformat()
    }

def summarize_with_ai(news_data):
    """Summarize news using Claude AI"""
    if not anthropic:
        return "AI summarization not available (no API key)"
    
    # Format news for Claude
    prompt = f"""You are BICLLAMA, a global news intelligence agent. Analyze the following real-time news data and provide a concise executive summary.

**Reddit r/worldnews (Global Issues):**
{json.dumps(news_data['reddit_worldnews'], indent=2)}

**Reddit r/news (US News):**
{json.dumps(news_data['reddit_news'], indent=2)}

**Hacker News (Tech):**
{json.dumps(news_data['hackernews'], indent=2)}

Provide:
1. **Top 3 Breaking Stories** (most urgent/impactful)
2. **Key Themes** (what's dominating the news cycle)
3. **Market Impact** (if any financial/economic implications)
4. **Tech Highlights** (from HN)

Keep it concise, data-driven, and actionable for investors and news consumers."""

    try:
        message = anthropic.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"AI summarization error: {str(e)}"

@app.route('/')
def home():
    return jsonify({
        'agent': 'BICLLAMA',
        'version': '1.0.0',
        'services': [
            {
                'name': 'global_scan',
                'description': 'On-demand global news scan with AI summary',
                'price': 0.05,
                'endpoint': '/scan'
            }
        ]
    })

@app.route('/scan', methods=['POST'])
def scan():
    """Global news scan endpoint"""
    try:
        # Collect news
        news_data = collect_news()
        
        # Summarize with AI
        summary = summarize_with_ai(news_data)
        
        return jsonify({
            'success': True,
            'timestamp': news_data['timestamp'],
            'summary': summary,
            'raw_data': news_data,
            'sources': {
                'reddit_worldnews': len(news_data['reddit_worldnews']),
                'reddit_news': len(news_data['reddit_news']),
                'hackernews': len(news_data['hackernews'])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
