import sqlite3
import time

def migrate_database(source_db: str, target_db: str):
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    # Wipe relevant tables in the target database
    target_cursor.executescript("""
        DELETE FROM album;
        DELETE FROM artist;
        DELETE FROM song;
        DELETE FROM event;
        DELETE FROM playlist;
        DELETE FROM search_history;
        DELETE FROM playlist_song_map;
        DELETE FROM song_album_map;
        DELETE FROM song_artist_map;
    """)
    
    # Migrate Albums
    source_cursor.execute("SELECT id, title, year, thumbnailUrl, bookmarkedAt FROM Album WHERE title IS NOT NULL")
    albums = source_cursor.fetchall()
    target_cursor.executemany("""
        INSERT INTO album (id, title, year, thumbnailUrl, bookmarkedAt, songCount, duration, lastUpdateTime)
        VALUES (?, ?, ?, ?, ?, -1, -1, ?)
    """, [(a[0], a[1], a[2], a[3], a[4], int(time.time())) for a in albums])
    
    # Migrate Artists
    source_cursor.execute("SELECT id, name, thumbnailUrl, bookmarkedAt FROM Artist")
    artists = source_cursor.fetchall()
    target_cursor.executemany("""
        INSERT INTO artist (id, name, thumbnailUrl, bookmarkedAt, lastUpdateTime)
        VALUES (?, ?, ?, ?, ?)
    """, [(a[0], a[1], a[2], a[3], int(time.time())) for a in artists])
    
    # Fetch Song-Album mappings from the source
    source_cursor.execute("SELECT songId, albumId FROM SongAlbumMap")
    song_album_map = dict(source_cursor.fetchall())

    # Migrate Songs
    source_cursor.execute("SELECT id, title, durationText, thumbnailUrl, likedAt, totalPlayTimeMs FROM Song")
    songs = source_cursor.fetchall()
    processed_songs = [
        (
            s[0],  # id
            s[1],  # title
            -1,    # duration
            s[3],  # thumbnailUrl
            song_album_map.get(s[0], None),  # albumId from SongAlbumMap
            None,  # albumName (left as None)
            s[4] or 0,  # liked
            s[5],  # totalPlayTime
            1  # inLibrary
        ) 
        for s in songs
    ]
    
    target_cursor.executemany("""
        INSERT INTO song (id, title, duration, thumbnailUrl, albumId, albumName, liked, totalPlayTime, inLibrary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, processed_songs)
    
    # Migrate Events
    source_cursor.execute("SELECT id, songId, timestamp, playTime FROM Event")
    events = source_cursor.fetchall()
    target_cursor.executemany("INSERT INTO event (id, songId, timestamp, playTime) VALUES (?, ?, ?, ?)" , events)

    # Migrate Playlists
    source_cursor.execute("SELECT id, name, browseId FROM Playlist")
    playlists = [(str(p[0]), p[1], p[2], int(time.time()), int(time.time())) for p in source_cursor.fetchall()]
    target_cursor.executemany("""
        INSERT INTO playlist (id, name, browseId, createdAt, lastUpdateTime)
        VALUES (?, ?, ?, ?, ?)
    """, playlists)
    
    # Migrate Playlist-Song mappings
    source_cursor.execute("SELECT playlistId, songId, position FROM SongPlaylistMap")
    playlist_song_map = source_cursor.fetchall()
    target_cursor.executemany("""
        INSERT INTO playlist_song_map (playlistId, songId, position)
        VALUES (?, ?, ?)
    """, playlist_song_map)

    # Migrate Album-Song mappings
    source_cursor.execute("SELECT songId, albumId, position FROM SongAlbumMap")
    #song_album_map = source_cursor.fetchall()
    song_album_map = [(str(p[0]), str(p[1]), p[2] if p[2] is not None else -1) for p in source_cursor.fetchall()]
    target_cursor.executemany("""
        INSERT INTO song_album_map (songId, albumId, 'index')
        VALUES (?, ?, ?)
    """, song_album_map)

    # Migrate Artist-Song mappings
    source_cursor.execute("SELECT songId, artistId FROM SongArtistMap")
    song_artist_map = source_cursor.fetchall()
    target_cursor.executemany("""
        INSERT INTO song_artist_map (songId, artistId, position)
        VALUES (?, ?, -1)
    """, song_artist_map)
    
    # Migrate Search History
    source_cursor.execute("SELECT id, query FROM SearchQuery")
    search_queries = source_cursor.fetchall()
    target_cursor.executemany("INSERT INTO search_history (id, query) VALUES (?, ?)" , search_queries)
    
    # Commit and close connections
    target_conn.commit()
    source_conn.close()
    target_conn.close()
    
if __name__ == "__main__":
    migrate_database("source.db", "target.db")
