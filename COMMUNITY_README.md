# Farming Community Feature

A Twitter-like community platform for farmers to share their thoughts, experiences, and knowledge about farming topics.

## Features

### ✅ Core Functionality
- **User Authentication**: Signup and login system
- **Post Creation**: Farmers can create posts with farming-related content
- **Topic Tagging**: Posts can be tagged with farming topics (Pest Control, Crop Management, etc.)
- **Feed Display**: Chronological feed of all posts
- **Topic Filtering**: Filter posts by specific farming topics
- **Like System**: Users can like posts
- **Comment System**: Users can comment on posts (API ready, UI can be extended)
- **Responsive Design**: Works on desktop and mobile

### 🎯 Farming Topics
- Crop Management
- Pest Control
- Soil Health
- Weather Impact
- Equipment
- Organic Farming
- Market Prices
- Success Stories

## Technical Implementation

### Backend (Flask + SQLite)
- **Database Tables**:
  - `users`: User accounts
  - `posts`: Community posts with topics
  - `likes`: Post likes (many-to-many)
  - `comments`: Post comments
  - `follows`: User following system (ready for future)

- **API Endpoints**:
  - `POST /api/posts` - Create new post
  - `GET /api/posts` - Get posts (with optional topic filter)
  - `POST /api/posts/<id>/like` - Like/unlike a post
  - `GET /api/posts/<id>/comments` - Get comments for a post
  - `POST /api/posts/<id>/comments` - Add comment to a post
  - `GET /api/topics` - Get available topics with post counts

### Frontend (React + Tailwind CSS)
- **Community Page**: Main feed with posting interface
- **Navigation**: Added to both desktop navbar and mobile bottom nav
- **Internationalization**: Full i18n support
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Posts refresh after creation

## How to Use

1. **Start the Backend**:
   ```bash
   python app.py
   ```
   Server runs on http://127.0.0.1:5000

2. **Start the Frontend**:
   ```bash
   cd DTI
   npm run dev
   ```
   App runs on http://localhost:5174

3. **Access the Community**:
   - Navigate to `/community` in the app
   - Or click "Community" in the navigation

4. **Participate**:
   - Sign up or log in
   - Create posts about farming topics
   - Like posts from other farmers
   - Filter by topics of interest

## Database Schema

The community feature adds these tables to the existing SQLite database:

```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    topic TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id),
    UNIQUE(user_id, post_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

CREATE TABLE follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    follower_id INTEGER NOT NULL,
    following_id INTEGER NOT NULL,
    FOREIGN KEY (follower_id) REFERENCES users (id),
    FOREIGN KEY (following_id) REFERENCES users (id),
    UNIQUE(follower_id, following_id)
);
```

## Future Enhancements

- **Comments UI**: Add comment display and creation in the frontend
- **Following System**: Allow users to follow other farmers
- **Notifications**: Real-time notifications for likes/comments
- **Search**: Search posts by content or author
- **Images**: Allow image uploads in posts
- **Moderation**: Admin tools for content moderation
- **Analytics**: Track engagement and popular topics

## Testing

Run the test script to verify API functionality:

```bash
python test_community_api.py
```

This will test all community endpoints and create sample data.