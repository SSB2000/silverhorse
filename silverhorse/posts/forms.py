from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={"placeholder": "Title of your Post"})
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"placeholder": "Content of your Post"})
    submit = SubmitField('Post')
