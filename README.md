## ytdownloader

A modern desktop YouTube downloader built with PySide6 and yt-dlp. Clean UI, fast extraction, and sensible defaults.

### What it can do

- Download videos in any available quality (or select a specific format)
- Extract audio only (MP3 via FFmpeg)
- Fetch subtitles, choose languages, and optionally embed them into the video
- Remove SponsorBlock segments (configurable categories)
- Save thumbnails and video descriptions
- View rich video metadata (title, channel, views, upload date, duration, thumbnail)
- Show progress with speed and ETA; spinners while analyzing/starting downloads
- Configure speed limit, concurrent fragment downloads, cookies file, user agent
- Apply extra yt-dlp options (limit-rate, proxy, cookies, user agent)
- Update yt-dlp in-app (background pip upgrade)

### Requirements

- Python 3.8+
- Windows/macOS/Linux
- FFmpeg (needed for audio extraction, merging video+audio formats, and embedding subtitles)

Notes about FFmpeg:

- The app automatically looks for FFmpeg in several places (in order):
  - `FFMPEG_LOCATION` environment variable (its `bin` directory is prepended to PATH)
  - System PATH
  - Windows: `%LOCALAPPDATA%/ffmpeg/ffmpeg-7.1-full_build/bin` (same default as YTSage)
  - App-local: `ytdownloader/.ffmpeg/bin` (used by the auto-installer)
- If FFmpeg is not found, the app falls back to single-file downloads (no merging), disables embed-subtitles and audio extraction, and shows a one-time notice. You can set FFmpeg from File → Set FFmpeg… or install it (Windows) via File → Install FFmpeg (auto).

### Install

```bash
pip install -r requirementcs.txt
```

Optional but recommended:

- Create and activate a virtual environment (`python -m venv .venv` then `.
.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux) before installing dependencies.

### Run

```bash
python main.py
```

### Using the app

1. Paste a YouTube URL and click Analyze. The app shows a spinner while extracting info.
2. Review metadata and formats.
   - Double-click a row to select a specific format (video-only rows auto-pair with bestaudio when FFmpeg is available).
   - Toggle Video / Audio Only to filter the format list.
3. Options strip:
   - Merge Subtitles: Enable to embed selected subtitles into the output (requires FFmpeg and available subtitles).
   - Remove Sponsor Segments: Uses SponsorBlock. Categories are configurable in Download Settings.
   - Save Thumbnail: Writes the video thumbnail alongside the output.
   - Save Description: Saves the video description to a file.
   - Select Subtitles…: Choose one or more languages to download; the selection appears on the button.
4. Output: Defaults to `~/Downloads/<title>/<title>.<ext>`. Use Output… to change the base directory; each video will still be placed in a subfolder named after its title.
5. Click Download. The progress bar will show a spinner until yt-dlp reports progress, then switches to percent with speed and ETA.

### Custom Command

Click Custom Command to set common yt-dlp options:

- Limit rate → `--limit-rate`
- Proxy → `--proxy`
- Cookies → `--cookies`
- User agent → `--user-agent`

These are applied when the download starts. They are kept for the session.

### Download Settings

Click Download Settings to configure:

- Speed limit (string, e.g. `5M`)
- Concurrent fragment downloads (1–16)
- Cookies file path
- User agent
- SponsorBlock categories (choose which to remove)

Settings are applied to subsequent downloads in the current session.

### Update yt-dlp

Click Update yt-dlp to run a background upgrade via pip. The app shows a spinner and a completion message when done.

### Subtitles

- After Analyze, the app shows if subtitles are available and enables the selection button.
- Embedding subtitles requires FFmpeg. If FFmpeg is missing or no subtitles are available, the Merge Subtitles option is disabled.

### SponsorBlock

- When enabled, the app removes the selected SponsorBlock categories during post-processing. You can adjust categories in Download Settings.

### Troubleshooting

- “ffprobe and ffmpeg not found”:
  - Use File → Set FFmpeg… and point to your ffmpeg executable; or on Windows use File → Install FFmpeg (auto).
  - Or set the environment variable `FFMPEG_LOCATION` to the directory that contains `ffmpeg(.exe)` and `ffprobe(.exe)`.
- Format merging fails: ensure FFmpeg is present; otherwise pick a single-file format or let the app fall back to `best`.
- No subtitles appear: not all videos provide subtitles; try another video or language.

### License

MIT
