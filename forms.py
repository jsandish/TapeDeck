from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', 
                                     validators=[EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update Profile')

class SongForm(FlaskForm):
    song_name = StringField('Song Name', validators=[DataRequired()])
    artist_name = StringField('Artist Name', validators=[DataRequired()])
    album_name = StringField('Album Name', validators=[Optional()])
    release_date = StringField('Release Date (YYYY-MM-DD)', validators=[Optional()])
    genre = StringField('Genre', validators=[Optional()])
    submit = SubmitField('Add Song')

class SongRatingForm(FlaskForm):
    rating = FloatField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    mood_id = SelectField('Mood', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Rating')

class PlaylistForm(FlaskForm):
    playlist_name = StringField('Playlist Name', validators=[DataRequired()])
    submit = SubmitField('Create Playlist')

class AddToPlaylistForm(FlaskForm):
    playlist_id = SelectField('Select Playlist', coerce=int, validators=[DataRequired()])
    song_id = HiddenField('Song ID')
    submit = SubmitField('Add to Playlist')

class MoodForm(FlaskForm):
    mood = StringField('Mood Name', validators=[DataRequired()])
    submit = SubmitField('Add Mood')

class PlaylistCollaboratorForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    permissions = SelectField('Permissions', choices=[
        (1, 'Read Only'),
        (2, 'Edit'),
        (3, 'Admin')
    ], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Collaborator')