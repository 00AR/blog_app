
def test_create_blog(client):
    r = client.post(
        "/blogs",
        json={
            "title": "Test Blog",
            "content": "Test blog content",
        }
    )

    # TEST: Create blog
    assert r.status_code == 200
    
    blog_id = r.json()["_id"]

    # TEST: Get all blogs
    r = client.get("/blogs")
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["title"] == "Test Blog"
    
    # TEST: Get a single blogs
    r = client.get(f"/blogs/{blog_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Test Blog"
    assert data["content"] == "Test blog content"

    # TEST: Update a blog
    client.put(
        f"/blogs/{blog_id}",
        json={
            "title": "Updated title",
            "content": "Updated blog content"
        }
    )
    
    updated_blog = client.get(f"/blogs/{blog_id}")
    data = updated_blog.json()
    assert data["title"] == "Updated title"
    assert data["content"] == "Updated blog content"


    # TEST: Delete a blog
    r = client.delete(f"/blogs/{blog_id}")
    assert r.status_code == 204
    blogs = client.get("/blogs")
    data = blogs.json()["data"]
    assert len(data) == 0



def test_user_reactions(client):
    r = client.post(
        "/blogs",
        json={
            "title": "Test Blog",
            "content": "Test blog content",
        }
    )

    blog_id = r.json()["_id"]

    # TEST: Reacting with Like
    r = client.post(
        f"/blogs/{blog_id}/likes"
    )

    assert r.status_code == 200

    blog = client.get(f"/blogs/{blog_id}")
    data = blog.json()
    assert data["likes"] == 1

    # TEST: Undo the Like
    r = client.delete(
        f"/blogs/{blog_id}/likes"
    )

    assert r.status_code == 204

    blog = client.get(f"/blogs/{blog_id}")
    data = blog.json()
    assert data["likes"] == 0

    # TEST: Reacting with Dislike
    r = client.post(
        f"/blogs/{blog_id}/dislikes"
    )

    assert r.status_code == 200

    blog = client.get(f"/blogs/{blog_id}")
    data = blog.json()
    assert data["dislikes"] == 1

    # TEST: Undo the Dislike
    r = client.delete(
        f"/blogs/{blog_id}/dislikes"
    )

    assert r.status_code == 204

    blog = client.get(f"/blogs/{blog_id}")
    data = blog.json()
    assert data["dislikes"] == 0


def test_user_comments(client):
    r = client.post(
        "/blogs",
        json={
            "title": "Test Blog",
            "content": "Test blog content",
        }
    )

    blog_id = r.json()["_id"]

    # TEST: Add a comment
    r = client.post(
        f"/blogs/{blog_id}/comments",
        json={
            "comment": "test comment"
        }
    )
    assert r.status_code == 200
    
    all_comments = client.get(f"/blogs/{blog_id}/comments")
    data = all_comments.json()
    assert len(data) == 1
    assert data[0]["comment"] == "test comment"

    comment_id = data[0]["_id"]  
    # TEST: Update a comment
    client.put(
        f"/blogs/{blog_id}/comments/{comment_id}",
        json={
            "comment": "updated comment"
        }
    )
    all_comments = client.get(f"/blogs/{blog_id}/comments")
    data = all_comments.json()
    assert data[0]["comment"] == "updated comment"

    # TEST: Delete a comment
    r = client.delete(f"/blogs/{blog_id}/comments/{comment_id}")
    
    assert r.status_code == 204
    all_comments = client.get(f"/blogs/{blog_id}/comments")
    data = all_comments.json()
    assert len(data) == 0