import os
import google.generativeai as genai
from dotenv import load_dotenv
import article_parser
from datetime import datetime
import requests
import hashlib
from urllib.parse import urlparse
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
IMAGE_DIR = 'assets/images'
POSTS_DIR = '_posts'
os.chdir('..')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def download_image(image_url, source_domain):
    """Download image and save it with a unique name"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Create unique filename using hash of URL
            file_ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
            filename = f"{hashlib.md5(image_url.encode()).hexdigest()}{file_ext}"
            
            # Ensure assets/images directory exists
            os.makedirs(IMAGE_DIR, exist_ok=True)
            
            # Save the image
            image_path = f'{IMAGE_DIR}/{filename}'
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return image_path
    except Exception as e:
        logger.error(f"Error downloading image from {image_url}: {str(e)}")
    return None

def get_article_summary(title, content):
    """Get article summary using Gemini AI"""
    prompt = f"""
    Summarize the following article in exactly 250 words. Keep it informative and engaging in both Vietnamese and English:
    
    Title: {title}
    Content: {content}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error getting summary from Gemini: {str(e)}")
        return None

def create_markdown_post(title, summary, image_path, source_url):
    website_name = urlparse(source_url).netloc
    """Create markdown file for Jekyll post"""
    today = datetime.now()
    filename = f"{POSTS_DIR}/{today.strftime('%Y-%m-%d')}-{title.lower().replace(' ', '-')[:50]}.md"
    
    content = f"""---
layout: post
title: "{title}"
author: will
categories: [ ai-daily-news, {website_name} ]
image: {image_path}
source: "{source_url}"
---
{summary}

[Read the original article]({source_url})
"""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Error creating markdown file: {str(e)}")
        return False

def process_source(source_url):
    """Process a single news source"""
    try:
        # Parse the article using article_parser
        title, content = article_parser.parse(url=source_url, output='markdown')
        
        # Skip if no title or content
        if not title or not content:
            logger.warning(f"Skipping {source_url}: No title or content")
            return False
            
        # Attempt to download the top image
        image_path = None
        if hasattr(article_parser, 'get_top_image'):
            image_url = article_parser.get_top_image(url=source_url)
            if image_url:
                image_path = download_image(image_url, urlparse(source_url).netloc)
        
        if not image_path:
            logger.info(f"No image found for {source_url}, proceeding without image.")
            
        # Get AI summary
        summary = get_article_summary(title, content)
        if not summary:
            logger.warning(f"Could not generate summary for {source_url}")
            return False
        logger.info(f"Summary: {summary}")
            
        # Create markdown post
        return create_markdown_post(title, summary, image_path, source_url)
        
    except Exception as e:
        logger.error(f"Error processing {source_url}: {str(e)}")
        return False

def main():
    """Main function to process all sources"""
    try:
        # Read sources from file
        with open('script/source.txt', 'r') as f:
            sources = [line.strip() for line in f if line.strip()]
        
        success_count = 0
        for source in sources:
            if process_source(source):
                success_count += 1
                
        logger.info(f"Successfully processed {success_count} out of {len(sources)} sources")
        
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
