1、github下载ffmpeg文件：https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest，
下载win64版本，文件名大概是ffmpeg-XX-latest-win64-lgpl-XX.zip，
如：ffmpeg-n8.0-latest-win64-lgpl-8.0.zip

2、将ffmpeg.exe文件解压缩，放到本程序同一目录下，只要ffmpeg.exe单文件即可。

3、单文件打包命令
pyinstaller -F -w -i .\assets\icon.ico --splash .\assets\load.png -n "视频剪辑工具" .\main.py

依赖：flet==0.80.2

flet build --project "EditVideo" --description "基于FFmpeg的视频剪辑工具" --product "视频剪辑工具" --company "Lix" --copyright "Copyright @2026 By Dodotry" --no-web-splash --no-ios-splash --no-android-splash  --cleanup-app --cleanup-packages windows --module-name main.py
