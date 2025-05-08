from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Playlist Manager (many-to-many relationship table with additional data)
playlist_manager = db.Table('playlist_manager',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), primary_key=True),
    db.Column('permissions', db.Integer, default=1)  # 1: read, 2: read/write, 3: admin
)

# Playlist Songs (many-to-many relationship table)
playlist_songs = db.Table('playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.song_id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Relationships
    ratings = db.relationship('SongRating', backref='user', lazy=True)
    playlists = db.relationship('Playlist', secondary=playlist_manager, backref=db.backref('users', lazy='dynamic'))
    moods = db.relationship('Mood', backref='user', lazy=True)
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Artist(db.Model):
    __tablename__ = 'artist'
    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    songs = db.relationship('Song', backref='artist', lazy=True)

class Album(db.Model):
    __tablename__ = 'album'
    album_id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.String(100), nullable=False)
    
    # Relationships
    songs = db.relationship('Song', backref='album', lazy=True)

class Song(db.Model):
    __tablename__ = 'song'
    song_id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.String(20))
    album_id = db.Column(db.Integer, db.ForeignKey('album.album_id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.artist_id'), nullable=False)
    genre = db.Column(db.String(50))  # Added genre for filtering requirement
    
    # Relationships
    ratings = db.relationship('SongRating', backref='song', lazy=True)
    playlists = db.relationship('Playlist', secondary=playlist_songs, backref=db.backref('songs', lazy='dynamic'))

class Mood(db.Model):
    __tablename__ = 'mood'
    mood_id = db.Column(db.Integer, primary_key=True)
    mood = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # Added for custom moods per user
    
    # Relationships
    ratings = db.relationship('SongRating', backref='mood', lazy=True)

class SongRating(db.Model):
    __tablename__ = 'song_rating'
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    mood_id = db.Column(db.Integer, db.ForeignKey('mood.mood_id'))
    notes = db.Column(db.Text)  # Added for note-taking requirement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Playlist(db.Model):
    __tablename__ = 'playlist'
    playlist_id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to user who created the playlist
    creator = db.relationship('User', foreign_keys=[created_by])