from flask import Blueprint, render_template

blog = Blueprint('blog', __name__, template_folder='templates')


@blog.route('/blog/')
def blog_top_bar():
    from app_portfolio import Post

    posts = Post.query.all()
    return render_template('blog/blog-topbar.html', posts=posts)


