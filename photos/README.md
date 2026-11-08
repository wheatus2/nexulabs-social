# Nexulabs photo library

Free Unsplash photos chosen for the Nexulabs posts. File names: `<photographer>--<description>.<unsplash-id>.jpg`.

- The scheduled runs use one roughly every third post, add the Nexulabs type and logo, and credit the photographer.
- **No photo is ever used twice.** After use it moves to `photos/used/` and its id is added to `used-ids.txt`; `photo.py` refuses any id on that list.
- To top up the library, ask Claude in a chat ("top up the Nexulabs photo library") and it'll pick more in your browser.
