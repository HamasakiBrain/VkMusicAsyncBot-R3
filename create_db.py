import sqlite3 

sql = sqlite3.connect("NewVkMusic.sqlite")
cursor = sql.cursor()

cursor.execute("CREATE TABLE audio_downloads (id INTEGER PRIMARY KEY NOT NULL, \
                                              created DATETIME NOT NULL, \
                                              owner_id INTEGER NOT NULL, \
                                              audio_id INTEGER NOT NULL)")

cursor.execute("CREATE TABLE audios (id INTEGER PRIMARY KEY NOT NULL, \
                                     owner_id INTEGER NOT NULL, \
                                     audio_id INTEGER NOT NULL, \
                                     artist TEXT NOT NULL, \
                                     title TEXT NOT NULL, \
                                     duration INTEGER NOT NULL)")

cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL, \
                                    created DATETIME NOT NULL, \
                                    user_id INTEGER NOT NULL, \
                                    last_seen DATETIME NOT NULL, \
                                    ref_link TEXT NOT NULL, \
                                    is_banned TINYINT NOT NULL DEFAULT '0')")

cursor.execute("CREATE TABLE users_audios (id INTEGER PRIMARY KEY NOT NULL, \
                                           user_id INTEGER NOT NULL, \
                                           owner_id INTEGER NOT NULL, \
                                           audio_id INTEGER NOT NULL)")

sql.commit()