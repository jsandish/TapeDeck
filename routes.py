from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from models import db, User, Song, Artist, Album, SongRating, Playlist, Mood, playlist_manager
from forms import (RegistrationForm, LoginForm, ProfileForm, SongForm, SongRatingForm,
                  PlaylistForm, AddToPlaylistForm, MoodForm, PlaylistCollaboratorForm)
from helpers import get_user_by_email

bp = Blueprint('routes', __name__)

# ------------------------
# Authentication Routes
# ------------------------

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email or username already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        
        # Add default moods for the user
        from config import Config
        for mood_name in Config.DEFAULT_MOODS:
            mood = Mood(mood=mood_name, user_id=user.user_id)
            db.session.add(mood)
        
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('routes.home'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('routes.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return render_template('profile.html', form=form)
        
        # Check if new username or email already exists (for other users)
        username_exists = User.query.filter(
            User.username == form.username.data,
            User.user_id != current_user.user_id
        ).first()
        
        email_exists = User.query.filter(
            User.email == form.email.data,
            User.user_id != current_user.user_id
        ).first()
        
        if username_exists:
            flash('Username already taken', 'danger')
            return render_template('profile.html', form=form)
        
        if email_exists:
            flash('Email already registered', 'danger')
            return render_template('profile.html', form=form)
        
        # Update user information
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        # Update password if provided
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('routes.profile'))
    
    return render_template('profile.html', form=form)

# ------------------------
# Main Application Routes
# ------------------------

@bp.route('/')
@login_required
def home():
    # Get user's recently rated songs
    recent_ratings = SongRating.query.filter_by(user_id=current_user.user_id).order_by(SongRating.updated_at.desc()).limit(5).all()
    
    # Get user's playlists
    playlists = Playlist.query.join(playlist_manager).filter(
        playlist_manager.c.user_id == current_user.user_id
    ).all()
    
    return render_template('home.html', recent_ratings=recent_ratings, playlists=playlists)

# ------------------------
# Song Routes
# ------------------------

@bp.route('/songs')
@login_required
def songs():
    # Filter parameters
    rating_filter = request.args.get('rating')
    mood_filter = request.args.get('mood_id')
    genre_filter = request.args.get('genre')
    artist_filter = request.args.get('artist_id')
    
    # Base query - get all songs with user's ratings if they exist
    query = db.session.query(Song, SongRating).\
        outerjoin(SongRating, (Song.song_id == SongRating.song_id) & 
                 (SongRating.user_id == current_user.user_id)).\
        join(Artist)
    
    # Apply filters if provided
    if rating_filter:
        rating_value = float(rating_filter)
        query = query.filter(SongRating.rating >= rating_value)
    
    if mood_filter:
        query = query.filter(SongRating.mood_id == int(mood_filter))
    
    if genre_filter:
        query = query.filter(Song.genre.ilike(f'%{genre_filter}%'))
    
    if artist_filter:
        query = query.filter(Song.artist_id == int(artist_filter))
    
    # Execute query
    results = query.all()
    
    # Get all moods for the filter dropdown
    moods = Mood.query.filter_by(user_id=current_user.user_id).all()
    
    # Get all artists for the filter dropdown
    artists = Artist.query.all()
    
    # Get all genres for the filter dropdown (unique values)
    genres = db.session.query(Song.genre).distinct().filter(Song.genre.isnot(None)).all()
    
    # Prepare a form for adding songs to playlists
    add_to_playlist_form = AddToPlaylistForm()
    add_to_playlist_form.playlist_id.choices = [
        (p.playlist_id, p.playlist_name) 
        for p in Playlist.query.join(playlist_manager).filter(
            playlist_manager.c.user_id == current_user.user_id,
            playlist_manager.c.permissions >= 2  # User can edit
        ).all()
    ]
    
    return render_template(
        'songs.html', 
        results=results,
        moods=moods,
        artists=artists,
        genres=genres,
        add_to_playlist_form=add_to_playlist_form
    )

@bp.route('/songs/add', methods=['GET', 'POST'])
@login_required
def add_song():
    form = SongForm()
    
    if form.validate_on_submit():
        # Check if artist exists, create if not
        artist = Artist.query.filter_by(artist_name=form.artist_name.data).first()
        if not artist:
            artist = Artist(artist_name=form.artist_name.data)
            db.session.add(artist)
            db.session.flush()  # Get the ID without committing
        
        # Check if album exists, create if not (and if provided)
        album_id = None
        if form.album_name.data:
            album = Album.query.filter_by(album_name=form.album_name.data).first()
            if not album:
                album = Album(album_name=form.album_name.data)
                db.session.add(album)
                db.session.flush()  # Get the ID without committing
            album_id = album.album_id
        
        # Create the song
        song = Song(
            song_name=form.song_name.data,
            artist_id=artist.artist_id,
            album_id=album_id,
            release_date=form.release_date.data,
            genre=form.genre.data
        )
        
        db.session.add(song)
        db.session.commit()
        
        flash(f'Song "{form.song_name.data}" added successfully', 'success')
        return redirect(url_for('routes.songs'))
    
    return render_template('add_song.html', form=form)

@bp.route('/songs/<int:song_id>/rate', methods=['GET', 'POST'])
@login_required
def rate_song(song_id):
    song = Song.query.get_or_404(song_id)
    rating = SongRating.query.filter_by(user_id=current_user.user_id, song_id=song_id).first()
    
    form = SongRatingForm()
    form.mood_id.choices = [(m.mood_id, m.mood) for m in Mood.query.filter_by(user_id=current_user.user_id).all()]
    # Using '0' instead of None for "No Mood" option
    form.mood_id.choices.insert(0, (0, 'No Mood'))
    
    if request.method == 'GET':
        if rating:
            form.rating.data = rating.rating
            form.mood_id.data = rating.mood_id if rating.mood_id else 0  # Default to 0 if no mood
            form.notes.data = rating.notes
    
    if form.validate_on_submit():
        if rating:
            # Update existing rating
            rating.rating = form.rating.data
            rating.mood_id = form.mood_id.data if form.mood_id.data > 0 else None  # Convert 0 back to None
            rating.notes = form.notes.data
        else:
            # Create new rating
            rating = SongRating(
                user_id=current_user.user_id,
                song_id=song_id,
                rating=form.rating.data,
                mood_id=form.mood_id.data if form.mood_id.data > 0 else None,  # Convert 0 back to None
                notes=form.notes.data
            )
            db.session.add(rating)
        
        db.session.commit()
        flash(f'Rating for "{song.song_name}" saved', 'success')
        return redirect(url_for('routes.songs'))
    
    return render_template('rate_song.html', form=form, song=song)

@bp.route('/songs/add_to_playlist', methods=['POST'])
@login_required
def add_to_playlist():
    form = AddToPlaylistForm()
    
    # Set the choices for the playlist_id field before validating
    form.playlist_id.choices = [
        (p.playlist_id, p.playlist_name) 
        for p in Playlist.query.join(playlist_manager).filter(
            playlist_manager.c.user_id == current_user.user_id,
            playlist_manager.c.permissions >= 2  # User can edit
        ).all()
    ]
    
    if form.validate_on_submit():
        playlist = Playlist.query.get_or_404(form.playlist_id.data)
        song = Song.query.get_or_404(form.song_id.data)
        
        # Check if user has permission to edit this playlist
        permission = db.session.query(playlist_manager.c.permissions).filter(
            playlist_manager.c.playlist_id == playlist.playlist_id,
            playlist_manager.c.user_id == current_user.user_id
        ).scalar()
        
        if not permission or permission < 2:  # Read-only access
            flash('You do not have permission to edit this playlist', 'danger')
            return redirect(url_for('routes.songs'))
        
        # Check if song is already in the playlist
        if playlist.songs.filter_by(song_id=song.song_id).first():
            flash(f'"{song.song_name}" is already in "{playlist.playlist_name}"', 'info')
        else:
            playlist.songs.append(song)
            db.session.commit()
            flash(f'Added "{song.song_name}" to "{playlist.playlist_name}"', 'success')
    
    return redirect(url_for('routes.songs'))

# ------------------------
# Playlist Routes
# ------------------------

@bp.route('/playlists')
@login_required
def playlists():
    # Get all playlists the user has access to
    user_playlists = Playlist.query.join(playlist_manager).filter(
        playlist_manager.c.user_id == current_user.user_id
    ).all()
    
    return render_template('playlists.html', playlists=user_playlists)

@bp.route('/playlists/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    
    if form.validate_on_submit():
        # Create new playlist
        playlist = Playlist(
            playlist_name=form.playlist_name.data,
            created_by=current_user.user_id
        )
        db.session.add(playlist)
        db.session.flush()  # Get the ID without committing
        
        # Add creator with admin permissions
        stmt = playlist_manager.insert().values(
            playlist_id=playlist.playlist_id,
            user_id=current_user.user_id,
            permissions=3  # Admin
        )
        db.session.execute(stmt)
        db.session.commit()
        
        flash(f'Playlist "{form.playlist_name.data}" created', 'success')
        return redirect(url_for('routes.playlists'))
    
    return render_template('create_playlist.html', form=form)

@bp.route('/playlists/<int:playlist_id>')
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check if user has access to this playlist
    access = db.session.query(playlist_manager).filter(
        playlist_manager.c.playlist_id == playlist_id,
        playlist_manager.c.user_id == current_user.user_id
    ).first()
    
    if not access:
        abort(403)
    
    # Get all songs in this playlist
    songs = playlist.songs.all()
    
    # Get all collaborators
    collaborators = db.session.query(User, playlist_manager.c.permissions).join(
        playlist_manager, User.user_id == playlist_manager.c.user_id
    ).filter(
        playlist_manager.c.playlist_id == playlist_id
    ).all()
    
    # Check user's permission level
    permission_level = access.permissions
    
    collaborator_form = PlaylistCollaboratorForm() if permission_level >= 3 else None
    
    return render_template(
        'playlist_detail.html',
        playlist=playlist,
        songs=songs,
        collaborators=collaborators,
        permission_level=permission_level,
        collaborator_form=collaborator_form
    )

@bp.route('/playlists/<int:playlist_id>/add_collaborator', methods=['POST'])
@login_required
def add_collaborator(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check if user is admin of this playlist
    access = db.session.query(playlist_manager.c.permissions).filter(
        playlist_manager.c.playlist_id == playlist_id,
        playlist_manager.c.user_id == current_user.user_id
    ).scalar()
    
    if not access or access < 3:  # Not admin
        abort(403)
    
    form = PlaylistCollaboratorForm()
    
    if form.validate_on_submit():
        user_to_add = get_user_by_email(form.user_email.data)
        
        if not user_to_add:
            flash(f'User with email {form.user_email.data} not found', 'danger')
            return redirect(url_for('routes.view_playlist', playlist_id=playlist_id))
        
        # Check if user is already a collaborator
        existing = db.session.query(playlist_manager).filter(
            playlist_manager.c.playlist_id == playlist_id,
            playlist_manager.c.user_id == user_to_add.user_id
        ).first()
        
        if existing:
            # Update permissions
            stmt = playlist_manager.update().where(
                (playlist_manager.c.playlist_id == playlist_id) &
                (playlist_manager.c.user_id == user_to_add.user_id)
            ).values(permissions=form.permissions.data)
            db.session.execute(stmt)
            flash(f'Updated permissions for {user_to_add.username}', 'success')
        else:
            # Add new collaborator
            stmt = playlist_manager.insert().values(
                playlist_id=playlist_id,
                user_id=user_to_add.user_id,
                permissions=form.permissions.data
            )
            db.session.execute(stmt)
            flash(f'Added {user_to_add.username} as collaborator', 'success')
        
        db.session.commit()
    
    return redirect(url_for('routes.view_playlist', playlist_id=playlist_id))

@bp.route('/playlists/<int:playlist_id>/remove_song/<int:song_id>', methods=['POST'])
@login_required
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.get_or_404(song_id)
    
    # Check if user has permission to edit this playlist
    permission = db.session.query(playlist_manager.c.permissions).filter(
        playlist_manager.c.playlist_id == playlist_id,
        playlist_manager.c.user_id == current_user.user_id
    ).scalar()
    
    if not permission or permission < 2:  # Read-only access
        flash('You do not have permission to edit this playlist', 'danger')
        return redirect(url_for('routes.view_playlist', playlist_id=playlist_id))
    
    # Remove song from playlist
    playlist.songs.remove(song)
    db.session.commit()
    
    flash(f'Removed "{song.song_name}" from playlist', 'success')
    return redirect(url_for('routes.view_playlist', playlist_id=playlist_id))

# ------------------------
# Mood Routes
# ------------------------

@bp.route('/moods')
@login_required
def moods():
    user_moods = Mood.query.filter_by(user_id=current_user.user_id).all()
    form = MoodForm()
    return render_template('moods.html', moods=user_moods, form=form)

@bp.route('/moods/add', methods=['POST'])
@login_required
def add_mood():
    form = MoodForm()
    
    if form.validate_on_submit():
        # Check if mood already exists for this user
        existing_mood = Mood.query.filter_by(
            user_id=current_user.user_id,
            mood=form.mood.data
        ).first()
        
        if existing_mood:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'error': f'Mood "{form.mood.data}" already exists'
                })
            flash(f'Mood "{form.mood.data}" already exists', 'warning')
        else:
            mood = Mood(mood=form.mood.data, user_id=current_user.user_id)
            db.session.add(mood)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'mood_id': mood.mood_id,
                    'mood_name': mood.mood
                })
            flash(f'Mood "{form.mood.data}" added successfully', 'success')
    
    return redirect(url_for('routes.moods'))

@bp.route('/moods/<int:mood_id>/delete', methods=['POST'])
@login_required
def delete_mood(mood_id):
    mood = Mood.query.get_or_404(mood_id)
    
    # Ensure user owns this mood
    if mood.user_id != current_user.user_id:
        abort(403)
    
    # Check if mood is being used in any ratings
    in_use = SongRating.query.filter_by(mood_id=mood_id).first()
    
    if in_use:
        flash('Cannot delete mood that is being used in ratings', 'danger')
    else:
        db.session.delete(mood)
        db.session.commit()
        flash('Mood deleted successfully', 'success')
    
    return redirect(url_for('routes.moods'))