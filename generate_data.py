import csv
import random
from datetime import datetime, timedelta

# Realistic data pools
usernames = [
    "john_tech", "sara_fitness", "alex_sports", "priya_travel", "mike_foodie",
    "emma_music", "raj_politics", "lisa_fashion", "david_gaming", "neha_movies",
    "chris_crypto", "ananya_books", "tom_science", "zara_beauty", "arjun_cars",
    "olivia_art", "rahul_cricket", "nina_yoga", "james_news", "kavya_dance",
    "max_photography", "sanya_health", "leo_startup", "meera_nature", "ryan_comedy",
    "deepika_food", "ethan_music", "pooja_lifestyle", "noah_sports", "riya_tech",
    "lucas_travel", "shreya_movies", "mason_gaming", "tanvi_fashion", "benjamin_finance",
    "aisha_wellness", "henry_politics", "divya_art", "sebastian_cars", "nisha_books"
]

hashtag_pool = {
    "tech": ["#tech", "#AI", "#coding", "#python", "#javascript", "#startup", "#innovation", "#gadgets", "#software", "#devlife"],
    "sports": ["#cricket", "#football", "#NBA", "#fitness", "#IPL", "#worldcup", "#sports", "#running", "#gym", "#athlete"],
    "entertainment": ["#bollywood", "#hollywood", "#netflix", "#movies", "#music", "#oscars", "#trending", "#viral", "#celebs", "#concert"],
    "food": ["#foodie", "#cooking", "#recipe", "#foodporn", "#healthyfood", "#vegan", "#dessert", "#coffee", "#restaurant", "#homemade"],
    "travel": ["#travel", "#wanderlust", "#vacation", "#beach", "#mountains", "#adventure", "#explore", "#tourism", "#roadtrip", "#nature"],
    "politics": ["#election", "#politics", "#democracy", "#vote", "#government", "#policy", "#news", "#breaking", "#debate", "#leadership"],
    "lifestyle": ["#lifestyle", "#motivation", "#success", "#mindfulness", "#selfcare", "#wellness", "#goals", "#inspiration", "#positivity", "#growth"],
    "finance": ["#crypto", "#bitcoin", "#stocks", "#investment", "#trading", "#finance", "#money", "#wealth", "#economy", "#markets"]
}

text_templates = {
    "tech": [
        "Just discovered an amazing {} feature! Game changer for developers",
        "The new {} update is incredible! Productivity through the roof",
        "Learning {} has been the best decision of my career",
        "Can't believe how powerful {} has become. The future is here!",
        "Hot take: {} will dominate the industry in 2024",
        "Finally solved that bug using {}. What a relief!",
        "This {} tool saved me hours of work today",
        "Excited to announce our new {} project launch!",
        "Anyone else amazed by the {} capabilities?",
        "The {} community is absolutely incredible"
    ],
    "sports": [
        "What an incredible match! {} for the win!",
        "Training hard for the upcoming {} season",
        "That {} performance was absolutely legendary!",
        "Can't wait for the {} finals this weekend",
        "The {} team showed amazing spirit today",
        "Personal best at the gym today! {} motivation",
        "What a comeback by {}! Never count them out",
        "The {} rivalry is heating up",
        "Match day vibes! Ready for {} action",
        "That {} goal will be remembered forever"
    ],
    "entertainment": [
        "Just watched {} and I'm absolutely blown away!",
        "The {} soundtrack is on repeat all day",
        "Can't stop thinking about that {} plot twist",
        "{} deserves all the awards honestly",
        "Binge watching {} this weekend. No regrets!",
        "The {} concert was an unforgettable experience",
        "Hot take: {} is the best movie of the year",
        "Finally caught up on {} and wow!",
        "This {} performance gave me chills",
        "The {} trailer just dropped and I'm hyped!"
    ],
    "food": [
        "Made the most delicious {} today! Recipe coming soon",
        "This {} restaurant is seriously underrated",
        "Sunday {} brunch hits different",
        "Trying {} for the first time and I'm obsessed!",
        "That {} recipe was a total success",
        "Food coma after amazing {} meal",
        "The secret to perfect {} is patience",
        "Cooking {} from scratch is so rewarding",
        "This {} spot has the best vibes",
        "Can't go wrong with classic {} comfort food"
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
        "That {} view was worth the hike"
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
        "Democracy in action at the {} event"
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
        "Embracing the {} lifestyle fully now"
    ],
    "finance": [
        "Interesting {} market movements today",
        "The {} trend is showing strong signals",
        "Smart {} strategy for long-term growth",
        "Analyzing the {} patterns this week",
        "The {} update everyone's been waiting for",
        "Building {} portfolio one day at a time",
        "This {} opportunity looks promising",
        "Keep calm and {} on during volatility",
        "The {} fundamentals remain strong",
        "Diversifying {} investments wisely"
    ]
}

sentiments = {
    "positive": ["love", "amazing", "incredible", "fantastic", "great", "best", "wonderful", "excellent", "awesome", "brilliant"],
    "negative": ["hate", "terrible", "worst", "disappointing", "bad", "awful", "horrible", "poor", "frustrating", "annoying"],
    "neutral": ["interesting", "okay", "normal", "regular", "typical", "standard", "usual", "common", "ordinary", "average"]
}

# Keywords for each category
keywords = {
    "tech": ["AI", "Python", "JavaScript", "React", "cloud", "API", "machine learning", "automation", "DevOps", "blockchain"],
    "sports": ["team", "match", "player", "score", "championship", "finals", "training", "victory", "tournament", "league"],
    "entertainment": ["movie", "show", "album", "artist", "performance", "episode", "series", "premiere", "release", "star"],
    "food": ["pasta", "pizza", "sushi", "curry", "dessert", "brunch", "coffee", "salad", "burger", "tacos"],
    "travel": ["Bali", "Paris", "Tokyo", "Goa", "Dubai", "Maldives", "Switzerland", "Thailand", "London", "New York"],
    "politics": ["policy", "reform", "election", "government", "parliament", "legislation", "bill", "vote", "campaign", "debate"],
    "lifestyle": ["meditation", "fitness", "wellness", "productivity", "growth", "mindfulness", "balance", "health", "routine", "gratitude"],
    "finance": ["Bitcoin", "stocks", "trading", "portfolio", "investment", "ETF", "crypto", "market", "returns", "dividends"]
}

def generate_posts(num_posts=1200):
    posts = []
    categories = list(hashtag_pool.keys())
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(1, num_posts + 1):
        category = random.choice(categories)
        
        # Generate text
        template = random.choice(text_templates[category])
        keyword = random.choice(keywords[category])
        text = template.format(keyword)
        
        # Add sentiment word occasionally
        if random.random() < 0.4:
            sentiment_type = random.choices(["positive", "negative", "neutral"], weights=[0.5, 0.2, 0.3])[0]
            sentiment_word = random.choice(sentiments[sentiment_type])
            text = text.replace("!", f"! Absolutely {sentiment_word}!")
        
        # Generate hashtags (1-4 per post)
        num_hashtags = random.randint(1, 4)
        selected_hashtags = random.sample(hashtag_pool[category], min(num_hashtags, len(hashtag_pool[category])))
        hashtags_str = "|".join([h.replace("#", "") for h in selected_hashtags])
        
        # Generate engagement (realistic distribution)
        base_likes = random.randint(10, 500)
        viral_multiplier = random.choices([1, 5, 20, 50], weights=[0.7, 0.2, 0.08, 0.02])[0]
        likes = base_likes * viral_multiplier
        retweets = int(likes * random.uniform(0.2, 0.6))
        
        # Generate timestamp
        random_days = random.randint(0, (end_date - start_date).days)
        random_hours = random.randint(6, 23)
        random_minutes = random.randint(0, 59)
        timestamp = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        
        # User
        user_id = random.randint(100, 999)
        username = random.choice(usernames)
        
        posts.append({
            "post_id": i,
            "user_id": user_id,
            "username": username,
            "text": text,
            "hashtags": hashtags_str,
            "likes": likes,
            "retweets": retweets,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return posts

# Generate and save
posts = generate_posts(1200)

with open("data/social_media_posts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["post_id", "user_id", "username", "text", "hashtags", "likes", "retweets", "timestamp"])
    writer.writeheader()
    writer.writerows(posts)

print(f"✅ Generated {len(posts)} social media posts")
print(f"📁 Saved to data/social_media_posts.csv")

# Show sample
print("\n📊 Sample data:")
for post in posts[:5]:
    print(f"  {post['username']}: {post['text'][:60]}... | #{post['hashtags']} | ❤️{post['likes']}")
