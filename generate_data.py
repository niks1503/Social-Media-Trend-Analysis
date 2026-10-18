"""
generate_data.py
----------------
Generates a realistic synthetic social media dataset.

Improvements over original:
  - Modular functions for each generation step
  - New fields: platform, location, follower_count, shares, comments, category
  - Configurable post count via CLI (default 2000)
  - Proper argparse entry-point
  - Python 3.11+ compatible type hints
  - Anonymised – no real user secrets or internal data
"""

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Data pools
# ---------------------------------------------------------------------------

USERNAMES: list[str] = [
    "john_tech", "sara_fitness", "alex_sports", "priya_travel", "mike_foodie",
    "emma_music", "raj_politics", "lisa_fashion", "david_gaming", "neha_movies",
    "chris_crypto", "ananya_books", "tom_science", "zara_beauty", "arjun_cars",
    "olivia_art", "rahul_cricket", "nina_yoga", "james_news", "kavya_dance",
    "max_photography", "sanya_health", "leo_startup", "meera_nature", "ryan_comedy",
    "deepika_food", "ethan_music", "pooja_lifestyle", "noah_sports", "riya_tech",
    "lucas_travel", "shreya_movies", "mason_gaming", "tanvi_fashion", "benjamin_finance",
    "aisha_wellness", "henry_politics", "divya_art", "sebastian_cars", "nisha_books",
    "carlos_fitness", "fatima_cooking", "yuki_anime", "ali_news", "sofia_travel",
    "liam_tech", "amara_art", "owen_sports", "chloe_books", "felix_music",
]

PLATFORMS: list[str] = ["Twitter", "Instagram", "LinkedIn", "Reddit", "TikTok"]

LOCATIONS: list[str] = [
    "New York", "Mumbai", "London", "Tokyo", "Sydney", "Dubai", "Toronto",
    "Berlin", "Sao Paulo", "Singapore", "Cape Town", "Paris", "Bangalore",
    "Los Angeles", "Seoul", "Mexico City", "Amsterdam", "Lagos", "Chicago", "Jakarta",
]

HASHTAG_POOL: dict[str, list[str]] = {
    "tech": ["#tech", "#AI", "#coding", "#python", "#javascript", "#startup",
              "#innovation", "#gadgets", "#software", "#devlife"],
    "sports": ["#cricket", "#football", "#NBA", "#fitness", "#IPL",
                "#worldcup", "#sports", "#running", "#gym", "#athlete"],
    "entertainment": ["#bollywood", "#hollywood", "#netflix", "#movies", "#music",
                       "#oscars", "#trending", "#viral", "#celebs", "#concert"],
    "food": ["#foodie", "#cooking", "#recipe", "#foodporn", "#healthyfood",
              "#vegan", "#dessert", "#coffee", "#restaurant", "#homemade"],
    "travel": ["#travel", "#wanderlust", "#vacation", "#beach", "#mountains",
                "#adventure", "#explore", "#tourism", "#roadtrip", "#nature"],
    "politics": ["#election", "#politics", "#democracy", "#vote", "#government",
                  "#policy", "#news", "#breaking", "#debate", "#leadership"],
    "lifestyle": ["#lifestyle", "#motivation", "#success", "#mindfulness", "#selfcare",
                   "#wellness", "#goals", "#inspiration", "#positivity", "#growth"],
    "finance": ["#crypto", "#bitcoin", "#stocks", "#investment", "#trading",
                 "#finance", "#money", "#wealth", "#economy", "#markets"],
}

TEXT_TEMPLATES: dict[str, list[str]] = {
    "tech": [
        "Just discovered an amazing {} feature! Game changer for developers",
        "The new {} update is incredible! Productivity through the roof",
        "Learning {} has been the best decision of my career",
        "Cant believe how powerful {} has become. The future is here!",
        "Hot take: {} will dominate the industry in 2025",
        "Finally solved that bug using {}. What a relief!",
        "This {} tool saved me hours of work today",
        "Excited to announce our new {} project launch!",
        "Anyone else amazed by the {} capabilities?",
        "The {} community is absolutely incredible",
    ],
    "sports": [
        "What an incredible match! {} for the win!",
        "Training hard for the upcoming {} season",
        "That {} performance was absolutely legendary!",
        "Cant wait for the {} finals this weekend",
        "The {} team showed amazing spirit today",
        "Personal best at the gym today! {} motivation",
        "What a comeback by {}! Never count them out",
        "The {} rivalry is heating up",
        "Match day vibes! Ready for {} action",
        "That {} goal will be remembered forever",
    ],
    "entertainment": [
        "Just watched {} and Im absolutely blown away!",
        "The {} soundtrack is on repeat all day",
        "Cant stop thinking about that {} plot twist",
        "{} deserves all the awards honestly",
        "Binge watching {} this weekend. No regrets!",
        "The {} concert was an unforgettable experience",
        "Hot take: {} is the best movie of the year",
        "Finally caught up on {} and wow!",
        "This {} performance gave me chills",
        "The {} trailer just dropped and Im hyped!",
    ],
    "food": [
        "Made the most delicious {} today! Recipe coming soon",
        "This {} restaurant is seriously underrated",
        "Sunday {} brunch hits different",
        "Trying {} for the first time and Im obsessed!",
        "That {} recipe was a total success",
        "Food coma after amazing {} meal",
        "The secret to perfect {} is patience",
        "Cooking {} from scratch is so rewarding",
        "This {} spot has the best vibes",
        "Cant go wrong with classic {} comfort food",
    ],
    "travel": [
        "The {} sunrise was absolutely magical",
        "Found a hidden gem in {}! Must visit",
        "{} is even more beautiful in person",
        "Road trip to {} was the best decision ever",
        "The {} adventure continues! Day 3 update",
        "Missing {} already. Take me back!",
        "Pro tip: Visit {} during off-season",
        "The {} culture is so fascinating",
        "Paradise found at {}!",
        "That {} view was worth the hike",
    ],
    "politics": [
        "Important {} developments we need to discuss",
        "The {} debate raised some valid points",
        "What are your thoughts on the {} policy?",
        "This {} decision will impact millions",
        "We need more accountability in {}",
        "The {} announcement changes everything",
        "Impressed by the {} leadership today",
        "Critical analysis of the {} situation",
        "The {} reforms are long overdue",
        "Democracy in action at the {} event",
    ],
    "lifestyle": [
        "Morning {} routine is keeping me grounded",
        "This {} mindset shift changed my life",
        "Working on {} goals every single day",
        "The {} journey is more important than destination",
        "Self-care Sunday with some {} time",
        "Grateful for this {} moment of peace",
        "Small {} habits lead to big changes",
        "The {} practice has been transformational",
        "Focus on {} and everything else follows",
        "Embracing the {} lifestyle fully now",
    ],
    "finance": [
        "Interesting {} market movements today",
        "The {} trend is showing strong signals",
        "Smart {} strategy for long-term growth",
        "Analyzing the {} patterns this week",
        "The {} update everyones been waiting for",
        "Building {} portfolio one day at a time",
        "This {} opportunity looks promising",
        "Keep calm and {} on during volatility",
        "The {} fundamentals remain strong",
        "Diversifying {} investments wisely",
    ],
}

SENTIMENTS: dict[str, list[str]] = {
    "positive": ["love", "amazing", "incredible", "fantastic", "great",
                  "best", "wonderful", "excellent", "awesome", "brilliant"],
    "negative": ["hate", "terrible", "worst", "disappointing", "bad",
                  "awful", "horrible", "poor", "frustrating", "annoying"],
    "neutral":  ["interesting", "okay", "normal", "regular", "typical",
                  "standard", "usual", "common", "ordinary", "average"],
}

KEYWORDS: dict[str, list[str]] = {
    "tech":          ["AI", "Python", "JavaScript", "React", "cloud", "API",
                       "machine learning", "automation", "DevOps", "blockchain"],
    "sports":        ["team", "match", "player", "score", "championship", "finals",
                       "training", "victory", "tournament", "league"],
    "entertainment": ["movie", "show", "album", "artist", "performance", "episode",
                       "series", "premiere", "release", "star"],
    "food":          ["pasta", "pizza", "sushi", "curry", "dessert", "brunch",
                       "coffee", "salad", "burger", "tacos"],
    "travel":        ["Bali", "Paris", "Tokyo", "Goa", "Dubai", "Maldives",
                       "Switzerland", "Thailand", "London", "New York"],
    "politics":      ["policy", "reform", "election", "government", "parliament",
                       "legislation", "bill", "vote", "campaign", "debate"],
    "lifestyle":     ["meditation", "fitness", "wellness", "productivity", "growth",
                       "mindfulness", "balance", "health", "routine", "gratitude"],
    "finance":       ["Bitcoin", "stocks", "trading", "portfolio", "investment",
                       "ETF", "crypto", "market", "returns", "dividends"],
}


# ---------------------------------------------------------------------------
# Modular generation helpers
# ---------------------------------------------------------------------------

def generate_text(category: str) -> str:
    """Build post text from a template + keyword, optionally append a sentiment word."""
    template = random.choice(TEXT_TEMPLATES[category])
    keyword = random.choice(KEYWORDS[category])
    text = template.format(keyword)

    if random.random() < 0.4:
        sentiment_type = random.choices(
            ["positive", "negative", "neutral"], weights=[0.5, 0.2, 0.3]
        )[0]
        sentiment_word = random.choice(SENTIMENTS[sentiment_type])
        text = text.replace("!", f"! Absolutely {sentiment_word}!")

    return text


def generate_hashtags(category: str) -> str:
    """Return a pipe-separated hashtag string (without leading #)."""
    num_hashtags = random.randint(1, 4)
    selected = random.sample(
        HASHTAG_POOL[category],
        min(num_hashtags, len(HASHTAG_POOL[category]))
    )
    return "|".join(h.replace("#", "") for h in selected)


def generate_engagement(platform: str) -> tuple[int, int, int]:
    """
    Return (likes, shares, comments) with platform-specific multipliers.

    Platform engagement benchmarks (relative):
        TikTok     2.5x  (highest virality)
        Instagram  1.8x
        Reddit     1.2x
        Twitter    1.0x  (baseline)
        LinkedIn   0.6x  (lower consumer engagement)
    """
    platform_multipliers: dict[str, float] = {
        "Twitter":   1.0,
        "Instagram": 1.8,
        "LinkedIn":  0.6,
        "Reddit":    1.2,
        "TikTok":    2.5,
    }
    base_likes = random.randint(10, 500)
    viral_multiplier = random.choices([1, 5, 20, 50], weights=[0.70, 0.20, 0.08, 0.02])[0]
    p_mult = platform_multipliers.get(platform, 1.0)
    likes = int(base_likes * viral_multiplier * p_mult)
    shares = int(likes * random.uniform(0.15, 0.55))
    comments = int(likes * random.uniform(0.05, 0.30))
    return likes, shares, comments


def generate_timestamp(start: datetime, end: datetime) -> datetime:
    """Return a uniformly random datetime between start and end."""
    random_days    = random.randint(0, (end - start).days)
    random_hours   = random.randint(6, 23)
    random_minutes = random.randint(0, 59)
    return start + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)


def generate_follower_count() -> int:
    """
    Return a realistic follower count using a power-law-inspired tier distribution.

    Tiers   | Range
    --------|---------------------
    nano    | 100 – 1 K
    micro   | 1 K – 10 K
    mid     | 10 K – 100 K
    macro   | 100 K – 1 M
    mega    | 1 M – 10 M
    """
    tier = random.choices(
        ["nano", "micro", "mid", "macro", "mega"],
        weights=[0.40, 0.30, 0.18, 0.10, 0.02],
    )[0]
    ranges: dict[str, tuple[int, int]] = {
        "nano":  (100,       1_000),
        "micro": (1_000,    10_000),
        "mid":   (10_000,  100_000),
        "macro": (100_000, 1_000_000),
        "mega":  (1_000_000, 10_000_000),
    }
    lo, hi = ranges[tier]
    return random.randint(lo, hi)


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------

def generate_posts(num_posts: int = 2000) -> list[dict]:
    """
    Generate a list of synthetic social media post records.

    Parameters
    ----------
    num_posts : int
        Number of posts to generate (default 2000).

    Returns
    -------
    list[dict]
        Fields: post_id, user_id, username, platform, location,
        follower_count, text, hashtags, category, likes, shares, comments, timestamp.
    """
    posts: list[dict] = []
    categories = list(HASHTAG_POOL.keys())
    start_date = datetime(2024, 1, 1)
    end_date   = datetime(2024, 12, 31)

    for i in range(1, num_posts + 1):
        category       = random.choice(categories)
        platform       = random.choice(PLATFORMS)
        username       = random.choice(USERNAMES)
        location       = random.choice(LOCATIONS)
        follower_count = generate_follower_count()

        text     = generate_text(category)
        hashtags = generate_hashtags(category)
        likes, shares, comments = generate_engagement(platform)
        timestamp = generate_timestamp(start_date, end_date)

        posts.append({
            "post_id":        i,
            "user_id":        random.randint(100, 9999),
            "username":       username,
            "platform":       platform,
            "location":       location,
            "follower_count": follower_count,
            "text":           text,
            "hashtags":       hashtags,
            "category":       category,
            "likes":          likes,
            "shares":         shares,
            "comments":       comments,
            "timestamp":      timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return posts


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a synthetic social media posts dataset."
    )
    parser.add_argument(
        "--num-posts", type=int, default=2000,
        help="Number of posts to generate (default: 2000)"
    )
    parser.add_argument(
        "--output", type=str, default="data/social_media_posts.csv",
        help="Output CSV path (default: data/social_media_posts.csv)"
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.num_posts} posts ...")
    posts = generate_posts(args.num_posts)

    fieldnames = [
        "post_id", "user_id", "username", "platform", "location",
        "follower_count", "text", "hashtags", "category",
        "likes", "shares", "comments", "timestamp",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(posts)

    print(f"Generated {len(posts):,} social media posts")
    print(f"Saved to {output_path}")
    print("\nSample data:")
    for post in posts[:5]:
        print(
            f"  [{post['platform']:10}] {post['username']}: "
            f"{post['text'][:55]}... | Likes:{post['likes']} Shares:{post['shares']} Comments:{post['comments']}"
        )


if __name__ == "__main__":
    main()
