#!/usr/bin/env python3
"""
BICLLAMA - On-Demand Global News Scan
Sources: Reddit, Hacker News
"""
import requests
import json
from datetime import datetime

def get_reddit_hot(subreddit="worldnews", limit=10):
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
        print(f"❌ Reddit r/{subreddit} error: {e}")
        return []

def get_hackernews_top(limit=10):
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
        print(f"❌ HackerNews error: {e}")
        return []

def generate_digest():
    """Generate comprehensive news digest"""
    print("🌍 BICLLAMA - Global News Scan")
    print("=" * 70)
    print(f"📅 Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    all_data = {}
    
    # Reddit WorldNews
    print("📰 Reddit r/worldnews (Hot Topics)")
    print("-" * 70)
    reddit_world = get_reddit_hot("worldnews", 8)
    all_data['reddit_worldnews'] = reddit_world
    for i, post in enumerate(reddit_world, 1):
        print(f"{i}. {post['title']}")
        print(f"   👍 {post['score']:,} upvotes | 💬 {post['comments']:,} comments")
        print()
    
    # Reddit News (US-focused)
    print("\n📰 Reddit r/news (US News)")
    print("-" * 70)
    reddit_news = get_reddit_hot("news", 8)
    all_data['reddit_news'] = reddit_news
    for i, post in enumerate(reddit_news, 1):
        print(f"{i}. {post['title']}")
        print(f"   👍 {post['score']:,} upvotes | 💬 {post['comments']:,} comments")
        print()
    
    # Hacker News
    print("\n💻 Hacker News (Top Stories - Tech Focus)")
    print("-" * 70)
    hn = get_hackernews_top(8)
    all_data['hackernews'] = hn
    for i, story in enumerate(hn, 1):
        print(f"{i}. {story['title']}")
        print(f"   👍 {story['score']:,} points | 💬 {story['comments']:,} comments")
        print()
    
    print("\n" + "=" * 70)
    print("✅ Scan complete - Ready for AI summarization")
    
    return all_data

if __name__ == "__main__":
    data = generate_digest()
    
    # Save to JSON for later processing
    output_file = f"news_digest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Raw data saved to: {output_file}")
