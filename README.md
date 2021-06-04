# EmbyKodiSync

Basic script to sync Emby and Kodi play count assuming the following
- Both are accessing the videos by the same full path, docker is mapping same internal and external full path name
- Kodi's database is /storage/.kodi/userdata/Database/MyVideos119.db
- Emby is running under docker image called emby
- Emby's database is /storage/.emby/data/library.db
