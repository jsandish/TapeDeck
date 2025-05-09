# TapeDeck

TapeDeck is a web application that allows users to catalog, rate, and organize their music in personalized playlists. It provides a platform for music enthusiasts to keep track of their favorite songs, rate them, and share playlists with friends.

## Features

- **User Authentication**: Register, login, and profile management
- **Song Management**: Add songs with artist, album, and genre information
- **Rating System**: Rate songs on a 5-star scale with personalized notes
- **Mood Tagging**: Tag songs with moods to organize your music by feeling
- **Playlists**: Create and manage playlists of your favorite songs
- **Collaboration**: Share playlists with other users with various permission levels
- **Filtering & Sorting**: Find songs by rating, mood, genre, or artist
- **Responsive Design**: Works great on both desktop and mobile devices

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation Steps

1. **Install dependencies**

   ```bash
   pip install flask flask-sqlalchemy flask-login flask-wtf
   ```

2. **Run the application**

   ```bash
   python app.py
   ```

3. **Access the application**
   
   Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
tapedeck/
│
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── models.py           # Database models
├── forms.py            # Form definitions
├── routes.py           # Application routes
├── helpers.py          # Helper functions
│
├── static/             # Static files
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── main.js     # JavaScript functionality
│
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── home.html       # Home dashboard
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   └── ...             # Other templates
│
└── tapedeck.db         # SQLite database file (created on first run)
```

## Database Schema

- **User**: User account information and authentication
- **Artist**: Music artists
- **Album**: Music albums
- **Song**: Song information linked to artists and albums
- **Mood**: Custom moods defined by users
- **SongRating**: User ratings for songs with mood and notes
- **Playlist**: User-created playlists
- **playlist_manager**: Junction table for playlist collaborators with permissions
- **playlist_songs**: Junction table linking songs to playlists

## Usage

1. Register for an account
2. Add songs to your collection
3. Rate songs and assign moods
4. Create playlists and add songs to them
5. Share playlists with other users by adding them as collaborators

## Acknowledgements

- Built with [Flask](https://flask.palletsprojects.com/)
- UI components from [Bootstrap](https://getbootstrap.com/)
- Icons from [Font Awesome](https://fontawesome.com/)
- Inspired by music platforms like Spotify and Last.fm
