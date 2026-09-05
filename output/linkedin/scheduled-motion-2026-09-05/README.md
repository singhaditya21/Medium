# Scheduled LinkedIn motion package

Prepared on 5 September 2026. **Not applied to LinkedIn.**

Open `index.html` for all 14 previews. Every card has its scheduled time, MP4, looping GIF, six-scene storyboard and content transcript. The GIF and MP4 contain the same six-scene explanation; the MP4 is the proposed LinkedIn upload, matching the format of the published Shabina-inspired reference.

## Deliverables

- 14 MP4s: H.264, 1080 × 1350, 24 fps, 36 seconds, no audio.
- 14 GIFs: 720 × 900, 10 fps, 36 seconds, infinite loop.
- 14 posters and 14 six-scene storyboards.
- `manifest.json`: exact proposed content and preservation boundary.
- `qa.json`: per-file SHA-256 hashes, frame counts and intra-scene motion checks.
- `visual-review.md`: human-readable visual QA record and remaining live-platform checks.
- Schedule and scope: `editorial/linkedin/motion-upgrade-2026-09-05.md` in the repository.

The visual titles are animation headlines, not proposed changes to scheduled post captions. All numbers are illustrative or attributed, not account performance telemetry. Contracts are explanatory schemas, not deployable authorization code.

## Reproduction

From the repository root, with Python 3, Pillow, ffmpeg, ffprobe and the renderer's configured macOS fonts:

```sh
python3 scripts/test_linkedin_scheduled_motion.py
python3 scripts/build_linkedin_scheduled_motion.py --storyboards-only
python3 scripts/build_linkedin_scheduled_motion.py
python3 scripts/build_linkedin_scheduled_motion.py --validate-only
```

Regeneration overwrites only this generated package. Re-review changed assets and invalidate the old manual QA hash before requesting approval. The renderer makes no API calls and does not access or modify LinkedIn.

## Next approval

Approve the exact S01–S14 MP4 files as media-only additions/replacements. Preserve the existing text, links, native mentions, hashtags, audience, comment permissions and scheduled times. Recheck the current schedule before editing. If any item has changed, published, or requires deletion/recreation, stop for fresh direction.

No upload-preview compatibility or saved LinkedIn replacement has been verified yet. No new posting authority is implied by the local QA results.
