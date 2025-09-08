from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

key = "8f4734b50cf72c253f04d1a55f079956"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class UpdateForm(FlaskForm):
    rate = StringField('Your rating out of 10', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    done = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    add = SubmitField('Add')




# CREATE DB
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)


class Movies(db.Model):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String,unique=True,nullable=False)
    year: Mapped[int] = mapped_column(String,nullable=False)
    description: Mapped[str] = mapped_column(String,nullable=False)
    rating: Mapped[float] = mapped_column(Float,nullable=False)
    ranking: Mapped[int] = mapped_column(Integer,nullable=False)
    reviews: Mapped[str] = mapped_column(String,nullable=False)
    img_url: Mapped[str] = mapped_column(String,nullable=False)


class Shows(db.Model):
    __tablename__ = 'shows'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String,unique=True,nullable=False)
    year: Mapped[int] = mapped_column(String,nullable=False)
    description: Mapped[str] = mapped_column(String,nullable=False)
    rating: Mapped[float] = mapped_column(Float,nullable=False)
    ranking: Mapped[int] = mapped_column(Integer,nullable=False)
    reviews: Mapped[str] = mapped_column(String,nullable=False)
    img_url: Mapped[str] = mapped_column(String,nullable=False)



# CREATE TABLE
with app.app_context():
    db.create_all()

# with app.app_context():
#     new_movie = Movies(
#         title="Phone Booth",
#         year="2002",
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         reviews = "My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/top_10_movies")
def top_10_movies():
    movie = Movies.query.order_by(Movies.rating.desc()).limit(10).all()
    rank = 1
    for mov in movie:
        mov.ranking = rank
        rank += 1
    db.session.commit()
    return render_template("index.html",movie=movie)

@app.route("/top_10_shows")
def top_10_shows():
    movie = Shows.query.order_by(Shows.rating.desc()).limit(10).all()
    rank = 1
    for mov in movie:
        mov.ranking = rank
        rank += 1
    db.session.commit()
    return render_template("index2.html",movie=movie,show=True)


@app.route("/update/movie/<int:movie_id>",methods=["GET","POST"])
def update(movie_id):
    form = UpdateForm()
    movie = Movies.query.get_or_404(movie_id)
    if form.validate_on_submit():
        movie.rating = form.rate.data
        movie.reviews = form.review.data
        db.session.commit()
        return redirect(url_for('top_10_movies'))
    return render_template('edit.html',form=form,movie=movie)

@app.route("/update/show/<int:movie_id>",methods=["GET","POST"])
def update_show(movie_id):
    form = UpdateForm()
    movie = Shows.query.get_or_404(movie_id)
    if form.validate_on_submit():
        movie.rating = form.rate.data
        movie.reviews = form.review.data
        db.session.commit()
        return redirect(url_for('top_10_shows'))
    return render_template('edit_show.html',form=form,movie=movie)


@app.route("/delete/movie/<int:movie_id>",methods=["GET","POST"])
def delete(movie_id):
    movie = Movies.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('top_10_movies'))


@app.route("/delete/show/<int:movie_id>",methods=["GET","POST"])
def delete_show(movie_id):
    movie = Shows.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('top_10_shows'))


@app.route("/add/movie",methods = ["GET","POST"])
def add_movie():
    form = AddForm()
    if form.validate_on_submit():
        parameter = {
            "query": form.title.data,
        }
        headers = {
            "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZjQ3MzRiNTBjZjcyYzI1M2YwNGQxYTU1ZjA3OTk1NiIsIm5iZiI6MTc1NzEwMzAwMS44MzAwMDAyLCJzdWIiOiI2OGJiNDM5OWNkMjllNjQ4NzIwNjkzZDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WtpgGiYbhynfIjTnnELXAI71YyXZ2v1FyBl3Fso3L2Q",
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameter, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = data["results"]
        return render_template("select.html",result=result)
    return render_template("add.html",form=form)


@app.route("/add/show",methods = ["GET","POST"])
def add_show():
    form = AddForm()
    if form.validate_on_submit():
        print(form.title.data)
        parameter = {
            "query": form.title.data,
        }
        headers = {
            "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZjQ3MzRiNTBjZjcyYzI1M2YwNGQxYTU1ZjA3OTk1NiIsIm5iZiI6MTc1NzEwMzAwMS44MzAwMDAyLCJzdWIiOiI2OGJiNDM5OWNkMjllNjQ4NzIwNjkzZDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WtpgGiYbhynfIjTnnELXAI71YyXZ2v1FyBl3Fso3L2Q",
        }
        response = requests.get("https://api.themoviedb.org/3/search/tv", params=parameter, headers=headers)
        response.raise_for_status()
        data = response.json()
        result = data["results"]
        return render_template("select.html",result=result,show = True)
    return render_template("add_show.html",form=form)



@app.route("/add_to/movie/<int:movie_id>")
def add_to(movie_id):
    headers = {
        "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZjQ3MzRiNTBjZjcyYzI1M2YwNGQxYTU1ZjA3OTk1NiIsIm5iZiI6MTc1NzEwMzAwMS44MzAwMDAyLCJzdWIiOiI2OGJiNDM5OWNkMjllNjQ4NzIwNjkzZDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WtpgGiYbhynfIjTnnELXAI71YyXZ2v1FyBl3Fso3L2Q",
    }
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}",headers=headers)
    response.raise_for_status()
    data = response.json()
    existing_movie = Movies.query.filter_by(title=data["original_title"]).first()
    if existing_movie:
        return redirect(url_for("update", movie_id=existing_movie.id))
    add_to_db = Movies(
        title=data["original_title"],
        year=data["release_date"].split("-")[0],
        description=data["overview"],
        rating=round(data["vote_average"],1),
        ranking=1,
        reviews="",
        img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
    )
    db.session.add(add_to_db)
    db.session.commit()
    return redirect(url_for("update",movie_id=add_to_db.id))


@app.route("/add_to/show/<int:movie_id>")
def add_to_show(movie_id):
    headers = {
        "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4ZjQ3MzRiNTBjZjcyYzI1M2YwNGQxYTU1ZjA3OTk1NiIsIm5iZiI6MTc1NzEwMzAwMS44MzAwMDAyLCJzdWIiOiI2OGJiNDM5OWNkMjllNjQ4NzIwNjkzZDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.WtpgGiYbhynfIjTnnELXAI71YyXZ2v1FyBl3Fso3L2Q",
    }
    response = requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}",headers=headers)
    response.raise_for_status()
    data = response.json()
    existing_movie = Shows.query.filter_by(title=data["original_name"]).first()
    if existing_movie:
        return redirect(url_for("update_show", movie_id=existing_movie.id))
    add_to_db = Shows(
        title=data["original_name"],
        year=data["first_air_date"].split("-")[0],
        description=data["overview"],
        rating=round(data["vote_average"],1),
        ranking=1,
        reviews="",
        img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
    )
    db.session.add(add_to_db)
    db.session.commit()
    return redirect(url_for("update_show",movie_id=add_to_db.id))




if __name__ == '__main__':
    app.run(debug=True)
