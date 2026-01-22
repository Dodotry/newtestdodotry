- github下载ffmpeg文件：https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest，
下载win64版本，文件名大概是ffmpeg-XX-latest-win64-lgpl-XX.zip，
如：ffmpeg-n8.0-latest-win64-lgpl-8.0.zip

- 将ffmpeg.exe文件解压缩，放到本程序同一目录下，只要ffmpeg.exe单文件即可。
依赖：flet==0.80.2

- 单文件打包命令
```shell
pyinstaller -F -w -i .\assets\icon.ico --splash .\assets\load.png -n "视频剪辑工具" .\main.py

```
```shell
flet pack -i .\assets\icon.ico -n "视频剪辑工具" --product-name "视频剪辑工具" --file-description "基于FFmpeg的视频剪辑工具" --file-version "1.0.2" --copyright "Copyright @2026 By Dodotry" -y ./main.py

flet build --project "EditVideo" --description "基于FFmpeg的视频剪辑工具" --product "EditVideo" --company "Lix" --copyright "Copyright @2026 By Dodotry" --no-web-splash --no-ios-splash --no-android-splash  --cleanup-app --cleanup-packages --clear-cache --build-version "1.0.2" windows --module-name ./main.py
```
flet build的时候，--project、-product不支持中文，需要英文，不然报找不到main

- 打包体积：pyinstaller < flet pack < 
```shell
python -m nuitka --mode=onefile `
 --mingw64 --windows-icon-from-ico="D:/uvtest/src/editvedio/assets/icon.ico" `
--onefile-windows-splash-screen-image="D:/uvtest/src/editvedio/assets/icon_windows.png" `
--output-filename="视频裁剪工具1.0.1.exe" `
--lto=yes --noinclude-default-mode=warning `
--windows-console-mode=disable `
--product-version="1.0.1" `
--file-version="1.0.1" `
--windows-company-name="dodotry" `
--windows-product-name="视频裁剪工具" `
--windows-file-description="基于ffmpeg的视频裁剪工具" `
--assume-yes-for-downloads --show-progress main.py

```
```shell
python -m nuitka --mode=standalone `
 --windows-icon-from-ico="D:/uvtest/src/editvedio/assets/icon.ico" `
--output-filename="视频裁剪工具0.4.exe" `
--lto=yes --noinclude-default-mode=warning `
--windows-console-mode=disable `
--product-version="1.0.1" `
--file-version="1.0.1" `
--windows-company-name="dodotry" `
--windows-product-name="视频裁剪工具" `
--windows-file-description="基于ffmpeg的视频裁剪工具" `
--include-windows-runtime-dlls=yes `
--assume-yes-for-downloads --show-progress main.py
```
