#!/usr/bin/env python3
"""
Test script for the community API endpoints.
Run this to test the community features.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        if response.ok:
            print(json.dumps(response.json(), indent=2))
        return response.ok
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_signup():
    """Test user signup"""
    data = {
        "name": "Test Farmer",
        "email": "farmer@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
        print(f"Signup: {response.status_code}")
        if response.ok:
            print(json.dumps(response.json(), indent=2))
        else:
            print(response.json())
        return response.ok
    except Exception as e:
        print(f"Signup failed: {e}")
        return False

def test_login():
    """Test user login"""
    data = {
        "email": "farmer@example.com",
        "password": "password123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"Login: {response.status_code}")
        if response.ok:
            result = response.json()
            print(json.dumps(result, indent=2))
            return result.get("user", {}).get("id")
        else:
            print(response.json())
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_create_post(user_id):
    """Test creating a post"""
    data = {
        "userId": user_id,
        "content": "Hello farmers! Just tried a new organic pest control method on my tomato plants. The neem oil spray seems to be working great! What are your experiences with organic pest control?",
        "topic": "Pest Control"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/posts", json=data)
        print(f"Create post: {response.status_code}")
        if response.ok:
            result = response.json()
            print(json.dumps(result, indent=2))
            return result.get("postId")
        else:
            print(response.json())
        return None
    except Exception as e:
        print(f"Create post failed: {e}")
        return None

def test_get_posts():
    """Test getting posts"""
    try:
        response = requests.get(f"{BASE_URL}/api/posts")
        print(f"Get posts: {response.status_code}")
        if response.ok:
            posts = response.json()
            print(f"Found {len(posts)} posts")
            for post in posts[:2]:  # Show first 2 posts
                print(f"- {post['author']['name']}: {post['content'][:50]}...")
        return response.ok
    except Exception as e:
        print(f"Get posts failed: {e}")
        return False

def test_get_topics():
    """Test getting topics"""
    try:
        response = requests.get(f"{BASE_URL}/api/topics")
        print(f"Get topics: {response.status_code}")
        if response.ok:
            topics = response.json()
            print(f"Found {len(topics)} topics")
            for topic in topics[:3]:  # Show first 3 topics
                print(f"- {topic['name']}: {topic['postCount']} posts")
        return response.ok
    except Exception as e:
        print(f"Get topics failed: {e}")
        return False

def main():
    print("Testing Community API Endpoints")
    print("=" * 40)

    # Test health
    if not test_health():
        print("Backend not running. Please start the Flask app first.")
        return

    print()

    # Test signup
    if not test_signup():
        print("Signup failed, but continuing with existing user...")

    print()

    # Test login
    user_id = test_login()
    if not user_id:
        print("Login failed. Cannot test post creation.")
        return

    print()

    # Test create post
    post_id = test_create_post(user_id)
    if post_id:
        print(f"Created post with ID: {post_id}")

    print()

    # Test get posts
    test_get_posts()

    print()

    # Test get topics
    test_get_topics()

    print()
    print("API testing complete!")

if __name__ == "__main__":
    main()