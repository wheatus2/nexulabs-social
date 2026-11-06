# nexulabs-social

Daily Instagram posts for [Nexulabs](https://nexulabs.co.uk), designed and published automatically.

- `PLAYBOOK.md`: brand, content pillars, accuracy rules and the daily routine
- `render.py`: turns `posts/<id>/post.json` into 1080×1350 slides
- `posts/<id>/`: each post's spec, caption and images (served to Instagram from raw.githubusercontent.com)
- `log.json`: what's been posted, so topics don't repeat
