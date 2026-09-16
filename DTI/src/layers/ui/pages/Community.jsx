import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useTranslation } from "react-i18next";
import Card from "../components/Card";

function Community() {
  const { t } = useTranslation();
  const [posts, setPosts] = useState([]);
  const [topics, setTopics] = useState([]);
  const [newPost, setNewPost] = useState("");
  const [selectedTopic, setSelectedTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [expandedComments, setExpandedComments] = useState({});
  const [postComments, setPostComments] = useState({});
  const [commentInputs, setCommentInputs] = useState({});

  useEffect(() => {
    loadPosts();
    loadTopics();
    // Check if user is logged in (you might want to implement proper auth state management)
    const storedUser = localStorage.getItem("plantvision-user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const loadPosts = async (topic = "") => {
    try {
      const url = topic ? `/api/posts?topic=${encodeURIComponent(topic)}` : "/api/posts";
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setPosts(data);
      }
    } catch (error) {
      console.error("Failed to load posts:", error);
    }
  };

  const loadTopics = async () => {
    try {
      const response = await fetch("/api/topics");
      if (response.ok) {
        const data = await response.json();
        setTopics(data);
      }
    } catch (error) {
      console.error("Failed to load topics:", error);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newPost.trim() || !user) return;

    setLoading(true);
    try {
      const response = await fetch("/api/posts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: user.id,
          content: newPost.trim(),
          topic: selectedTopic || null,
        }),
      });

      if (response.ok) {
        setNewPost("");
        setSelectedTopic("");
        loadPosts();
        loadTopics();
      } else {
        const error = await response.json();
        alert(error.error || "Failed to create post");
      }
    } catch (error) {
      console.error("Failed to create post:", error);
      alert("Failed to create post");
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId) => {
    if (!user) {
      alert("Please login to like posts");
      return;
    }

    try {
      const response = await fetch(`/api/posts/${postId}/like`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: user.id,
        }),
      });

      if (response.ok) {
        loadPosts();
      }
    } catch (error) {
      console.error("Failed to like post:", error);
    }
  };

  const toggleComments = async (postId) => {
    setExpandedComments((prev) => ({
      ...prev,
      [postId]: !prev[postId],
    }));

    if (!postComments[postId]) {
      try {
        const response = await fetch(`/api/posts/${postId}/comments`);
        if (response.ok) {
          const data = await response.json();
          setPostComments((prev) => ({ ...prev, [postId]: data }));
        }
      } catch (error) {
        console.error("Failed to load comments:", error);
      }
    }
  };

  const handleCommentSubmit = async (e, postId) => {
    e.preventDefault();
    if (!user) {
      alert("Please login to comment.");
      return;
    }
    const content = commentInputs[postId]?.trim();
    if (!content) return;

    try {
      const response = await fetch(`/api/posts/${postId}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user.id, content }),
      });

      if (response.ok) {
        setCommentInputs((prev) => ({ ...prev, [postId]: "" }));
        const commentsRes = await fetch(`/api/posts/${postId}/comments`);
        if (commentsRes.ok) {
          const data = await commentsRes.json();
          setPostComments((prev) => ({ ...prev, [postId]: data }));
        }
        setPosts((prevPosts) =>
          prevPosts.map((p) =>
            p.id === postId ? { ...p, commentsCount: (p.commentsCount || 0) + 1 } : p
          )
        );
      } else {
        const error = await response.json();
        alert(error.error || "Failed to post comment");
      }
    } catch (error) {
      console.error("Failed to submit comment:", error);
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm("Are you sure you want to delete this thread?")) return;
    
    try {
      const response = await fetch(`/api/posts/${postId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user.id }),
      });
      if (response.ok) {
        setPosts((prev) => prev.filter((p) => p.id !== postId));
      } else {
        const error = await response.json();
        alert(error.error || "Failed to delete post");
      }
    } catch (error) {
      console.error("Failed to delete post:", error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <section className="page-shell space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">{t("community_title")}</h2>
        <div className="text-sm text-slate-400">
          {t("community_subtitle")}
        </div>
      </div>

      {/* Create Post Form */}
      {user && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="premium-card"
        >
          <h3 className="text-lg font-semibold mb-4">{t("community_share_thoughts")}</h3>
          <form onSubmit={handleCreatePost} className="space-y-4">
            <textarea
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              placeholder={t("community_post_placeholder")}
              className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500"
              rows="3"
              maxLength="500"
            />
            <div className="flex items-center justify-between">
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">{t("community_select_topic")}</option>
                <option value="Crop Management">Crop Management</option>
                <option value="Pest Control">Pest Control</option>
                <option value="Soil Health">Soil Health</option>
                <option value="Weather Impact">Weather Impact</option>
                <option value="Equipment">Equipment</option>
                <option value="Organic Farming">Organic Farming</option>
                <option value="Market Prices">Market Prices</option>
                <option value="Success Stories">Success Stories</option>
              </select>
              <button
                type="submit"
                disabled={loading || !newPost.trim()}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
              >
                {loading ? t("community_posting") : t("community_post_button")}
              </button>
            </div>
          </form>
        </motion.div>
      )}

      {!user && (
        <div className="premium-card text-center py-8">
          <p className="text-slate-400 mb-4">{t("community_login_prompt")}</p>
          <a
            href="/login"
            className="inline-block px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
          >
            {t("community_login_button")}
          </a>
        </div>
      )}

      {/* Topics Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => loadPosts()}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            !selectedTopic ? "bg-green-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"
          }`}
        >
          {t("community_all_topics")}
        </button>
        {topics.slice(0, 8).map((topic) => (
          <button
            key={topic.name}
            onClick={() => loadPosts(topic.name)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedTopic === topic.name ? "bg-green-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"
            }`}
          >
            {topic.name} ({topic.postCount})
          </button>
        ))}
      </div>

      {/* Posts Feed */}
      <div className="space-y-4">
        {posts.length === 0 ? (
          <div className="premium-card text-center py-8">
            <p className="text-slate-400">{t("community_no_posts")}</p>
          </div>
        ) : (
          posts.map((post) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="premium-card"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-green-400">{post.author.name}</h4>
                  <p className="text-xs text-slate-400">{formatDate(post.createdAt)}</p>
                </div>
                <div className="flex items-center gap-2">
                  {post.topic && (
                    <span className="px-2 py-1 bg-slate-700 text-xs rounded-full text-slate-300">
                      {post.topic}
                    </span>
                  )}
                  {user && (user.id === post.author?.id || user.name === post.author?.name) && (
                    <button
                      onClick={() => handleDeletePost(post.id)}
                      className="text-slate-500 hover:text-red-400 transition-colors p-1"
                      title="Delete Thread"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  )}
                </div>
              </div>
              <p className="text-slate-200 mb-4 whitespace-pre-wrap">{post.content}</p>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => handleLike(post.id)}
                  className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm transition-colors ${
                    user ? "hover:bg-slate-700" : "cursor-not-allowed opacity-50"
                  }`}
                  disabled={!user}
                >
                  {t("community_like_button")} {post.likesCount}
                </button>
                <button
                  onClick={() => toggleComments(post.id)}
                  className="flex items-center gap-1 px-3 py-1 rounded-lg text-sm transition-colors hover:bg-slate-700 text-slate-300"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                  {t("community_comment_button")} {post.commentsCount}
                </button>
              </div>

              {/* Nested Comments Section */}
              {expandedComments[post.id] && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-4 pt-4 border-t border-slate-700/50"
                  style={{ overflow: "hidden" }}
                >
                  <div className="space-y-3 mb-4 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                    {postComments[post.id] ? (
                      postComments[post.id].length > 0 ? (
                        postComments[post.id].map(comment => (
                          <div key={comment.id} className="bg-slate-800/50 rounded-lg p-3 text-sm border border-slate-700/30">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-green-400">{comment.author.name}</span>
                              <span className="text-xs text-slate-500">{formatDate(comment.createdAt)}</span>
                            </div>
                            <p className="text-slate-300">{comment.content}</p>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-slate-500 italic">No comments yet. Be the first to advise!</p>
                      )
                    ) : (
                      <div className="flex space-x-2 justify-center items-center py-2 h-10">
                        <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce"></span>
                        <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                        <span className="w-2 h-2 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                      </div>
                    )}
                  </div>
                  
                  {user ? (
                    <form onSubmit={(e) => handleCommentSubmit(e, post.id)} className="flex gap-2">
                      <input
                        type="text"
                        value={commentInputs[post.id] || ""}
                        onChange={(e) => setCommentInputs(prev => ({ ...prev, [post.id]: e.target.value }))}
                        placeholder="Write a comment..."
                        className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-green-500"
                        maxLength="200"
                      />
                      <button
                        type="submit"
                        disabled={!commentInputs[post.id]?.trim()}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-slate-700 disabled:text-slate-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                      >
                        Post
                      </button>
                    </form>
                  ) : (
                    <div className="text-sm text-center text-slate-500 mt-2">
                      <a href="/login" className="text-green-400 hover:underline inline-block px-2">Log in</a> 
                      to join the conversation.
                    </div>
                  )}
                </motion.div>
              )}
            </motion.div>
          ))
        )}
      </div>
    </section>
  );
}

export default Community;