# Nexulabs photo library

Free Unsplash photos chosen for the Nexulabs posts. File names: `<photographer>--<description>.<unsplash-id>.jpg`.

- The scheduled runs use one roughly every third post, add the Nexulabs type and logo, and credit the photographer.
- **No photo is ever used twice.** After use it moves to `photos/used/` and its id is added to `used-ids.txt`; `photo.py` refuses any id on that list.
- `topics.json` tags every photo by topic so each post can find a fitting one: `python3 photo.py list --topic hosting`, or `python3 photo.py topics` for counts.
- Only engaging photos go in: no blank rooms or generic laptop shots, no other companies' logos, no AI-generated images. Dull ones live in `not-engaging/` and can't be used.
- To top up the library, ask Claude in a chat ("top up the Nexulabs photo library") and it'll pick more in your browser.
