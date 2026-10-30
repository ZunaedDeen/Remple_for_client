# Rempel Removal website (v7)

A fast static site with 23 pages, built to turn ad clicks into calls. Every photo is Rempel's own (pulled from their current site), and their four YouTube Shorts appear throughout. Nothing is AI-generated.

## What's in the folder

| Path | What it is |
|---|---|
| `preview/` | Open `preview/index.html` in a browser to click through the whole site on your computer |
| `dist/` | The version you put online (clean URLs). Upload this folder. |
| `build.py` | All the content (services, jobs, phone, photos) plus the page templates. Edit it, then rebuild. |
| `assets/` | `site.css` (design), `site.js` (scroll animations, sliders, filters), fonts |

Rebuild after any edit:

```bash
python3 build.py           # updates dist/
python3 build.py --local   # updates preview/
```

## Pages

- **Home**: a quick brand opening screen (REMPEL / REMOVAL / "Gone in a snap.", about 2 seconds, first visit per session only, tap to skip, never shown to visitors who turn off motion), then a split hero: headline lines slide up, and a photo panel crossfades through 5 real Rempel photos with a slow zoom (or plays a muted video loop if you add one). Below: numbers that count up (560 cu ft, 5,000 kg, 17 seasons, 60+ years), a full-width "Gone in a snap." banner that widens as you scroll and opens a YouTube Short in a pop-up player, How it works with a photo per step, Chad's story, Watch us work, before/after sliders, services, recent work, reviews and a call/text band. Cards fade up gently as they come into view. Nothing is pinned, so the page scrolls normally.
- **8 service pages**, each one an ad landing page: `/junk-removal/`, `/furniture-removal/`, `/appliance-removal/`, `/property-cleanouts/`, `/construction-cleanup/`, `/light-demolition/`, `/yard-waste-removal/`, `/snow-removal/`
- **Our Work**: 7 project stories with service filters, plus the video section (`/our-work/#videos`). Each project page swaps real photos as you scroll, and shows the matching YouTube Short where there is one
- **Before/after sliders**: drag to compare, with arrow-key support. The first time one scrolls into view, the handle sweeps across once so people know it moves. They appear on the homepage, Light demolition, Junk removal, and the Tear-outs and Scrap metal project pages. Add more in `SLIDERS` in `build.py`: either one side-by-side photo (`"split": True`) or two photos of the same spot (`"before"` and `"after"`).
- **Videos**: they also appear on the Junk removal, Property cleanouts and Construction cleanup pages, and on About. They only load when someone taps play, so pages stay fast.
- **About** (Chad's story), **Blog**, **Get a price** (photo-upload form), Thanks, 404
- Every page has a tap-to-call link in the header and a sticky **Call / Text a photo** bar on phones

SEO pieces: unique titles and descriptions, LocalBusiness and FAQ schema, `sitemap.xml`, `robots.txt`, and `_redirects` that send the old Wix URLs (`/blank`, `/blank-1`, `/contact`…) to the new pages.

## Put it online (Netlify, free)

1. Go to app.netlify.com/drop and drag the `dist` folder in. You get a live preview link right away.
2. Forms: the quote form already has Netlify Forms set up. In Site settings → Forms, add Carrie's email as the notification address.
3. Domain: in Domain settings, add `rempelremoval.com` and update DNS wherever the domain is registered. **Keep Wix running until the new site is tested.**

## Before launch: fill these in

- [ ] **Phone number.** The current site lists 1 (647) 688-6978, which is an Ontario area code. Confirm it's right. A local 306/639 number (or a Google Ads forwarding number) may get more calls. Change it in `SITE` in `build.py`.
- [ ] **Photos.** These are currently loaded from the Wix media library. Before cancelling Wix, download them into `assets/img/` and change the `IMG` entries to `assets/img/<file>`.
- [ ] **Tracking.** Paste the GA4 ID and Google Ads ID into `SITE["ga4_id"]` / `SITE["gads_id"]`. Phone taps, text taps and form submits already send events (`call_click`, `text_click`, `generate_lead`). Mark them as conversions in Google Ads.
- [ ] **Hours and service-area towns**: add them once Carrie confirms.
- [ ] **Projects**: add neighbourhoods and customer quotes to `PROJECTS` where you have them (only with the customer's permission). Ask Carrie for more same-spot before/after pairs. They make the best hero and project photos.
- [ ] **Chad's photo**: confirm the man with the truck (`chad_truck`) is Chad before launch.
- [ ] **Reviews**: currently screenshots. Swap in real Google review text with names once you have permission.

## Adding a video loop to the hero or banner

Ask Carrie for the original phone videos behind the YouTube Shorts (not downloads from YouTube). Pick 6 to 10 seconds of action, then:

```bash
mkdir -p media
ffmpeg -i clip.mov -t 8 -an -vf "scale=1280:-2,fps=30" -c:v libx264 -crf 26 -preset slow -movflags +faststart media/hero.mp4
ffmpeg -i clip.mov -t 8 -an -vf "scale=1280:-2,fps=30" -c:v libvpx-vp9 -crf 36 -b:v 0 media/hero.webm
```

Then set `HERO_VIDEO = {"mp4": "media/hero.mp4", "webm": "media/hero.webm", "poster": "chad_truck"}` (or `BANNER_VIDEO`) in `build.py` and rebuild. Keep each file under about 2 MB so the page stays fast for ad visitors. To turn off the opening screen, set `INTRO_SCREEN = False`.

## Optional: a Higgsfield animation for a project page

The hero already works with photos alone. If you want the final "after" card to animate, use real before/after photos of the same spot:

1. In Higgsfield, use **FLUX 3 Video** with the real before photo as the start frame and the real after photo as the end frame (5 s, 1080p, audio off). Make a 16:9 version and a 9:16 version.
2. Cut the clips into frames:
   ```bash
   mkdir -p media/hero/desktop media/hero/mobile
   ffmpeg -i hero.mp4 -vf "fps=24,scale=1600:-1" -c:v libwebp -quality 70 media/hero/desktop/%03d.webp
   ffmpeg -i hero-vertical.mp4 -vf "fps=12,scale=720:-1" -c:v libwebp -quality 65 media/hero/mobile/%03d.webp
   ```
3. In `build.py`, set `HERO_FRAMES = {"desktop": "media/hero/desktop/{i}.webp", "count": 120}`. For a project page, add
   `"frames": {"desktop": "media/<project>/desktop/{i}.webp", "count": 120}` to that project.
4. Rebuild. Scrolling now plays the clip forward and back. Visitors who turn off motion get still photos.

Only animate real jobs: the clip should show the clutter leaving, never invent a room or a result.

## Adding a project or video

- **Project**: copy an entry in `PROJECTS`, give it a new `slug` and `service`, and list its beats. Each beat is `{"img": key, "tag": "before" | "done" | "any label"}`. Add the photo to `IMG` first. Use `"note"` when the photos come from more than one job.
- **Video**: add `{"id": "<YouTube id>", "title": ..., "line": ...}` to `VIDEOS`. Link it to a service or project with `"video": "<id>"`.

## Blog posts

All 4 posts from the old Wix blog are on this site: `/blog/` and `/blog/<post>/`. Old links (`/post/<post>`) redirect to the new pages. To add a post, create `content/blog/<url-slug>.txt`:

```
title: Your post title
date: 2026-11-15
author: Rempel Removal
description: One or two sentences for Google and the blog list.
cover: d0f614_xxxxxxxx~mv2.jpg        (a Wix media id, an IMG key from build.py, or assets/img/file.jpg)
hero: chad_truck                      (optional: a different photo for the top of the post page)
hero_alt: What the hero photo shows    (optional)

First paragraph (shown larger).

## A heading

A normal paragraph. Write {phone} to insert the phone number as a tap-to-call link.

> A highlighted line

!img d0f614_xxxxxxxx~mv2.jpg | Optional caption
```

Blank lines separate blocks. Every post page automatically gets the reading time, share buttons (Facebook, text, copy link), an author box and a "Text us a photo" box at the end. Push to GitHub and Netlify rebuilds the site with the new post, sitemap included.
