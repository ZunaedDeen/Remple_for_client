#!/usr/bin/env python3
"""Rempel Removal static site generator (v2).

    python3 build.py           -> dist/    (clean URLs, for Netlify or any static host)
    python3 build.py --local   -> preview/ (relative links: open preview/index.html directly)

All content lives in this file: edit SITE, IMG, SERVICES, PROJECTS, VIDEOS, POSTS, then rebuild.
Every photo is Rempel's own (from their current site); nothing is AI-generated.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

LOCAL = "--local" in sys.argv
ROOT = Path(__file__).parent
OUT = ROOT / ("preview" if LOCAL else "dist")

# ---------------------------------------------------------------- business
SITE = {
    "name": "Rempel Removal",
    "domain": "https://www.rempelremoval.com",
    "phone_display": "1 (647) 688-6978",  # TODO confirm: a local 306/639 number may convert better
    "phone_e164": "+16476886978",
    "email": "chad@rempelremoval.com",
    "instagram": "https://www.instagram.com/rempelremoval/",
    "facebook": "https://www.facebook.com/Rempelremoval/",
    "youtube": "https://www.youtube.com/@RempelRemoval",
    "review_link": "https://g.page/r/CXKBRemMK6UCEBM/review",
    "area": "Saskatoon and surrounding communities",
    "truck_cuft": 560,
    "truck_kg": "5,000",
    "ga4_id": "",   # e.g. G-XXXXXXX
    "gads_id": "",  # e.g. AW-XXXXXXXXX
}

# Optional short, muted video loops cut from Rempel's own footage (see README).
# Leave as None to use the photo slideshow / still photo.
HERO_VIDEO = None    # e.g. {"mp4": "media/hero.mp4", "webm": "media/hero.webm", "poster": "chad_truck"}
BANNER_VIDEO = None  # e.g. {"mp4": "media/banner.mp4", "poster": "truck_debris"}
HERO_FRAMES = None   # legacy: Higgsfield frame sequence, unused on the current homepage

# Homepage hero slideshow: (image key, caption). Real Rempel photos only.
HERO_SLIDES = [
    ("chad_truck", "Locally owned"),
    ("appliances_truck", "Appliance pickup"),
    ("scrap_driveway", "Scrap and junk"),
    ("studs", "Tear-outs to the studs"),
    ("snow_truck", "Commercial snow hauling"),
]
INTRO_SCREEN = True  # brand opening screen on the homepage, first visit per session

# ---------------------------------------------------------------- images
# Rempel's own photos, served from their Wix media library for now.
# Before cancelling Wix, download them to assets/img/ and set the value to "assets/img/<file>".
WIX = "https://static.wixstatic.com/media/d0f614_"
IMG = {
    "logo": "6768bf0607e34e22b98938fb2aa7bfc9~mv2.png",
    "truck": "fa4273c50143479ca4cce17dcf438a04~mv2.png",
    "chad_truck": "257801e56cc24bfe95a28a068794464e~mv2.jpg",
    "football_a": "2f04ebcd2bdf45c386cd8d75f6f5bbca~mv2.jpg",
    "football_b": "cdda29ccccc540ec9f24c9db59f49061~mv2.png",
    "scrap_driveway": "aa3343b1467b4819896eba7de09e3e9a~mv2.jpg",
    "scrap_before": "fe273cc5fcb44219bd8759b01e22227e~mv2.jpg",
    "scrap_after": "85500f078e5444d992dcdb9c92bc4559~mv2.jpg",
    "washer_red": "2dc79097c2c146509889249ffa46da6a~mv2.jpg",
    "studs": "ab4c0313f6d8442d85b4c139b5a2b8dd~mv2.jpg",
    "trailer_debris": "881000d458614059959c6b4d9061ed55~mv2.jpg",
    "trailer_branches": "dc54e2d9b0bb49c48f3570521cfbe649~mv2.jpg",
    "basement_empty": "7ca275a67ffc4ad7bfb1f59c4333383b~mv2.jpg",
    "tearout_debris": "35931e4a64324e52872ebac39524cbff~mv2.jpg",
    "gutted_room": "b52155780ead487dafb5c391a4bff54f~mv2.jpg",
    "baseboard": "7f6eedc7959644f298e2d348b4711889~mv2.jpg",
    "wall_tearout": "6d3cf4a1d0c34bf2a237db807d3e0a6c~mv2.jpg",
    "debris_brick": "7f386e0419cc4381a116561346a6987b~mv2.jpg",
    "night_load": "4ce5665482ae440d9a7a2867dcfc4690~mv2.jpg",
    "trailer_branches_b": "79a2c49d37fc40fa90f3904a15910a58~mv2.jpg",
    "brush_fence": "9b88006eed7e4c078a147babfcfe783d~mv2.jpg",
    "carry_board": "73df6ce2fe70450d87cd0dc9d8687e96~mv2.jpg",
    "skidsteer": "4bb533b79cba40fb88e40dd112e3a93f~mv2.jpg",
    "site_debris": "b4839407614445a7ac302d8b278c9a30~mv2.jpg",
    "truck_debris": "7e066e1e2c0e44dfb1f20576e05a97b2~mv2.jpg",
    "appliances_truck": "fa6f7659e76a4a9d9d7e06bb6915568f~mv2.jpg",
    "fridge_old": "bc018c23841240ceb8974420e14fccd5~mv2.png",
    "truck_load": "538894bebac34af79dfa8517fc88ba02~mv2.jpg",
    "truck_couch": "9d0fadeb06df4ca18e1d37899d07e862~mv2.jpg",
    "flooring": "919ab2afe236404e86ddfaeba8c528b8~mv2.jpg",
    "shed_empty": "bfaba7f99a714da2b22971f21dca0be3~mv2.jpg",
    "snow_truck": "b85c588f9011491baf0a6b18295d444a~mv2.png",
    "basement": "b235f95018b2465e91aee5199d139446~mv2.jpg",
    "shelves": "d4ec901992e64547ad2656f3c30e30f6~mv2.jpg",
    "crew": "6c971e5ad19e47098dd0631df665ed6c~mv2.jpeg",
    "carpet_ba": "98dda572fc354958a24a29e49cf9b6d5~mv2.jpg",  # one image: left half before, right half after
    "brush_review": "d5fb5bd9a2b548eebe0d5449606466c3~mv2.jpg",
    "fishtank_review": "331140623b9843ce91f3266ecedf6297~mv2.jpg",
}

# Rempel's YouTube Shorts (@RempelRemoval)
VIDEOS = [
    {"id": "7cFFCD0C6kk", "title": "Steel removal", "line": "A pile of scrap steel, gone in a snap."},
    {"id": "tubzVwC8faI", "title": "Property cleanout", "line": "A whole property cleared out."},
    {"id": "S3vcLNdFKqE", "title": "Construction site cleanup", "line": "Site debris hauled away, done with care."},
    {"id": "4VdWQjVnMAo", "title": "Household junk", "line": "Time to let it go."},
]
VID = {v["id"]: v for v in VIDEOS}


def asset(path):
    return ("/" if not LOCAL else "../" * CURRENT_DEPTH) + path


def img(key):
    v = IMG[key]
    if v.startswith("http"):
        return v
    if v.startswith(("assets/", "media/")):
        return asset(v)
    return WIX + v


# ---------------------------------------------------------------- services
COMMON_FAQ = [
    ("How do I get a price?", "Text a photo of what needs to go to {phone}, or send photos through the quote form. We'll reply with straightforward pricing."),
    ("How much can you take in one trip?", "Our truck holds up to {cuft} cubic feet and {kg} kg, so most jobs are done in a single trip."),
    ("What happens to the things you take?", "Items in good condition are donated, materials are recycled where possible, and the rest is disposed of properly."),
    ("Where do you work?", "Saskatoon and surrounding communities. Not sure if you're in range? Text us your address with the photo."),
]

SERVICES = [
    {
        "slug": "junk-removal", "name": "Junk removal", "img": "scrap_driveway", "video": "4VdWQjVnMAo",
        "h1": "Junk removal in Saskatoon",
        "title": "Junk Removal Saskatoon | Rempel Removal",
        "meta": "Residential and commercial junk removal in Saskatoon. Text a photo for a fast price. One big truck: up to 560 cu ft per trip.",
        "short": "Single items to full loads, from anywhere on your property.",
        "intro": "From single-item pickups to full room cleanouts, we do the heavy lifting, load everything up and dispose of it responsibly.",
        "takes": ["Furniture", "Appliances", "Mattresses", "Garage junk", "Household junk", "Mixed boxes", "Office clutter", "Renovation scraps", "Yard waste", "Commercial junk"],
        "points": [
            ("You point, we load", "Leave it where it is. The crew carries it out, loads the truck and sweeps up after."),
            ("Bigger truck, fewer trips", "Up to 560 cubic feet and 5,000 kg in one load, so you're not paying for a second run."),
            ("Price from a photo", "Text us a picture and get a price without waiting for someone to come out and look."),
        ],
        "jobs": ["household-junk", "scrap-metal-pickup", "property-cleanouts"],
    },
    {
        "slug": "furniture-removal", "name": "Couch & furniture removal", "img": "truck_couch",
        "h1": "Couch and furniture removal in Saskatoon",
        "title": "Couch & Furniture Removal Saskatoon | Rempel Removal",
        "meta": "Couch, mattress and furniture removal in Saskatoon. We carry it out, haul it away and clean up. Text a photo for a price.",
        "short": "Couches, mattresses and old cabinetry, carried out for you.",
        "intro": "Heavy lifting made easy. We remove couches, mattresses and old cabinetry from any room so you can reclaim your home.",
        "takes": ["Couches and sectionals", "Mattresses and box springs", "Beds and dressers", "Tables and chairs", "Old cabinetry", "Office furniture"],
        "points": [
            ("Out of any room", "Basement, upstairs or garage. We do the heavy lifting."),
            ("Donated when it can be", "Pieces in good shape go to donation instead of the landfill."),
            ("One item or a houseful", "Single couch pickups and full furniture clear-outs."),
        ],
        "jobs": ["household-junk", "property-cleanouts", "appliance-pickups"],
    },
    {
        "slug": "appliance-removal", "name": "Appliance removal", "img": "appliances_truck",
        "h1": "Appliance removal in Saskatoon",
        "title": "Appliance Removal Saskatoon | Rempel Removal",
        "meta": "Fridge, stove, washer and dryer removal in Saskatoon with responsible recycling. Text a photo for a price.",
        "short": "Fridges, stoves and washers, recycled responsibly.",
        "intro": "Fast removal of old fridges, stoves and washers. We make sure the electronic components are recycled responsibly.",
        "takes": ["Fridges and freezers", "Stoves and ovens", "Washers and dryers", "Dishwashers", "Microwaves", "Electronics"],
        "points": [
            ("Carried out for you", "We do the heavy lifting and get it out of the house."),
            ("Recycled properly", "Appliances and electronics go to recycling, not the ditch."),
            ("Add the rest of the load", "Clearing out more than one thing? It all fits in the same truck."),
        ],
        "jobs": ["appliance-pickups", "household-junk", "property-cleanouts"],
    },
    {
        "slug": "property-cleanouts", "name": "Property & estate cleanouts", "img": "basement", "video": "tubzVwC8faI",
        "h1": "Property and estate cleanouts in Saskatoon",
        "title": "Estate & Property Cleanouts Saskatoon | Rempel Removal",
        "meta": "Estate, foreclosure and hoarding cleanouts in Saskatoon. Discreet, fast and thorough, with a tidy finish. Text a photo for a quote.",
        "short": "Estates, foreclosures and hoarding cleanouts, handled with care.",
        "intro": "Thoughtful clearing for homes, estates and foreclosures. We handle the sorting and hauling, with care and discretion.",
        "takes": ["Furniture", "Appliances", "Electronics", "Mattresses", "Shed contents", "Garage junk", "Household junk", "Renovation debris"],
        "process": [
            ("Full assessment", "We walk through the property to identify salvageable items, recycling opportunities and junk for removal."),
            ("Fast loading", "The team clears the property with our high-capacity truck for a quick turnaround on large volumes."),
            ("Tidy finish", "A final sweep-up leaves the property clean, clear and ready for what's next."),
        ],
        "points": [
            ("Licensed and insured", "A fully covered team on every cleanout."),
            ("Discreet service", "Sensitive estate and foreclosure situations handled with confidentiality and tact."),
            ("Pricing by volume", "Based on volume and complexity, with no hidden fees."),
        ],
        "faq": [
            ("What is included in a property cleanout?", "Removal of all unwanted items, including furniture, appliances, trash and debris, from every room, attic, basement and garage."),
            ("How long does a full estate cleanout take?", "Most cleanouts are done in a single day. Larger estates or commercial properties may take longer, and you'll get a clear timeline with your quote."),
            ("Do you handle foreclosures and evictions?", "Yes. We do fast-turnaround cleanouts for property managers, realtors and banks to get vacated properties ready for the market."),
            ("What happens to the items you remove?", "Items in good condition are donated, materials are recycled where possible, and the rest is disposed of properly."),
        ],
        "jobs": ["property-cleanouts", "household-junk", "appliance-pickups"],
    },
    {
        "slug": "construction-cleanup", "name": "Construction cleanup", "img": "skidsteer", "video": "S3vcLNdFKqE",
        "h1": "Construction cleanup in Saskatoon",
        "title": "Construction Cleanup & Debris Removal Saskatoon | Rempel Removal",
        "meta": "Construction and renovation debris removal in Saskatoon. One call keeps your job site safe and clear, no bin required.",
        "short": "Renovation debris and new-build scrap, cleared from your site.",
        "intro": "From renovation debris to new-build scrap, we keep your job site safe and clear. One call for all your hauling.",
        "takes": ["Lumber and framing scrap", "Drywall offcuts", "Flooring and tile", "Fixtures and cabinets", "Packaging and pallets", "General site debris"],
        "points": [
            ("No bin on the lot", "We load and haul straight off site, so there's no bin taking up space."),
            ("One call for all your hauling", "Renovation debris, new-build scrap and everything in between."),
            ("A clean, safe site", "Debris gone means fewer trip hazards for your crew."),
        ],
        "jobs": ["construction-cleanup", "tear-outs", "scrap-metal-pickup"],
    },
    {
        "slug": "light-demolition", "name": "Light demolition & tear-outs", "img": "wall_tearout",
        "h1": "Light demolition and tear-outs in Saskatoon",
        "title": "Light Demolition & Tear-outs Saskatoon | Rempel Removal",
        "meta": "Flood and fire tear-outs, carpet and drywall removal, sheds, decks, fences and hot tubs. We tear it out and haul it the same day, no bin needed.",
        "short": "Flood tear-outs, sheds, decks, fences and hot tubs.",
        "intro": "We remove damaged drywall, carpet and underlay, and take your space down to the studs so it's ready to rebuild. Then we haul it away in our own truck, so you don't need a bin.",
        "takes": ["Old sheds", "Wood decks", "Fences", "Hot tubs", "Flooring and underlay", "Interior walls", "Damaged drywall"],
        "process": [
            ("Tear out", "We strip fire- or water-damaged materials, down to the studs if needed, and keep structural elements intact."),
            ("Haul it away, no bin", "Debris goes straight into our high-capacity truck and off site, leaving your property clear at the end of each day."),
            ("Sweep-clean finish", "Every last piece goes, and the space is left ready for the next trade."),
        ],
        "points": [
            ("Flood restoration", "Basement flooded? Wet carpet, underlay and drywall need to come out fast."),
            ("Fire restoration", "Damaged materials removed safely, ready for rebuild."),
            ("Renovations", "Clear the old space before the new one goes in."),
        ],
        "faq": [
            ("How is demolition priced?", "Tear-outs vary with the size and complexity of the job and how much volume needs to be hauled. Send photos and we'll give you a custom quote."),
            ("Do I need to rent a bin?", "No. We tear it out and move it out the same day in our own truck."),
        ] + COMMON_FAQ[3:],
        "jobs": ["tear-outs", "construction-cleanup", "property-cleanouts"],
    },
    {
        "slug": "yard-waste-removal", "name": "Yard waste removal", "img": "brush_fence",
        "h1": "Yard waste removal in Saskatoon",
        "title": "Yard Waste Removal Saskatoon | Rempel Removal",
        "meta": "Branches, brush, clippings and seasonal yard debris removed in Saskatoon. Text a photo for a price.",
        "short": "Branches, clippings and seasonal debris.",
        "intro": "Clear your property of branches, clippings and seasonal debris, from one pile to the whole yard.",
        "takes": ["Branches and brush", "Tree trimmings", "Leaves and clippings", "Old fencing", "Seasonal debris"],
        "points": [
            ("Big piles welcome", "Brush is bulky. Our truck takes far more per trip than a pickup."),
            ("Spring and fall cleanups", "Book us when the snow melts or before it falls."),
            ("Gone in a snap", "We load it, clean up and haul it all away."),
        ],
        "jobs": ["yard-cleanups", "construction-cleanup", "household-junk"],
    },
    {
        "slug": "snow-removal", "name": "Commercial snow hauling", "img": "snow_truck",
        "h1": "Commercial snow hauling in Saskatoon",
        "title": "Commercial Snow Hauling Saskatoon | Rempel Removal",
        "meta": "Snow piles taking up parking? Rempel Removal hauls snow off commercial lots, plazas and industrial yards across Saskatoon.",
        "short": "Snow piles hauled off commercial lots.",
        "intro": "When snow piles up in commercial parking lots, it takes up parking and blocks access to your property. We haul it off site to keep your business moving.",
        "takes_title": "Who we work with",
        "takes": ["Commercial property managers", "Snow-removal contractors", "Shopping centres", "Industrial facilities", "Businesses", "General contractors"],
        "points": [
            ("Parking lot snow hauling", "Accumulated piles removed to free up parking and improve access."),
            ("Retail, industrial and commercial", "On-call hauling for plazas, industrial yards, warehouses and other commercial sites."),
            ("Support for snow contractors", "Already plowing a property? Bring us in when you need hauling capacity to move snow off site."),
        ],
        "faq": [
            ("We already have a plowing contractor. Can you still help?", "Yes. They clear the lot and we haul away the piles they've made."),
            ("Do you offer seasonal contracts?", "Ask for a snow-hauling quote and tell us about your site. We'll set up on-call or scheduled hauling."),
        ],
        "jobs": [],
        "cta": "Request a snow hauling quote",
    },
]
SVC = {s["slug"]: s for s in SERVICES}

# ---------------------------------------------------------------- projects (Our Work)
# Real Rempel photos only. A project groups photos of one kind of work; "note" says when
# the photos come from several jobs. Beat media: {"img": key, "tag": "before"|"done"|text}.
PROJECTS = [
    {
        "slug": "scrap-metal-pickup", "title": "Scrap metal pickup", "service": "junk-removal",
        "cover": "scrap_before", "video": "7cFFCD0C6kk",
        "summary": "A pile of scrap metal and old panels beside a lot, and the same spot after Rempel hauled it away.",
        "beats": [
            ("before", "The pile", "Scrap metal, old panels and odds and ends left beside the lot.", {"img": "scrap_before", "tag": "before"}),
            ("after", "The same spot, cleared", "All of it loaded and hauled away. Grass and pavement clear again.", {"img": "scrap_after", "tag": "done"}),
            ("compare", "Drag to compare", "Before and after, side by side.", {"ba": "scrap"}),
        ],
    },
    {
        "slug": "tear-outs", "title": "Tear-outs down to the studs", "service": "light-demolition",
        "cover": "wall_tearout", "note": "Photos from recent Rempel tear-out jobs.",
        "summary": "Flooring, drywall and trim torn out and hauled away, leaving the space ready to rebuild.",
        "beats": [
            ("debris", "Damaged materials out", "Ruined flooring, drywall and contents come out first.", {"img": "tearout_debris"}),
            ("walls", "Walls opened up", "Damaged drywall removed, down to the framing where needed.", {"img": "wall_tearout"}),
            ("trim", "Trim and flooring off", "Baseboards and flooring pulled, piece by piece.", {"img": "baseboard"}),
            ("studs", "Ready to rebuild", "Swept clean and down to the studs for the next trade.", {"img": "studs", "tag": "done"}),
            ("compare", "Before and after", "A carpet and underlay tear-out: piled out front, then cleared. Drag to compare.", {"ba": "carpet"}),
        ],
    },
    {
        "slug": "property-cleanouts", "title": "Property cleanouts", "service": "property-cleanouts",
        "cover": "basement", "video": "tubzVwC8faI", "note": "Photos from recent Rempel cleanouts.",
        "summary": "Basements, sheds and storage rooms cleared out and swept, ready for what's next.",
        "beats": [
            ("full", "Everything that has to go", "Years of stored things in an unfinished basement.", {"img": "basement", "tag": "before"}),
            ("load", "Loaded out", "Shelving and contents carried up and out to the truck.", {"img": "shelves"}),
            ("empty", "Cleared and swept", "Empty rooms, ready to sell, rent or renovate.", {"img": "basement_empty", "tag": "done"}),
            ("shed", "Sheds and storage too", "Outbuildings and storage areas cleared the same way.", {"img": "shed_empty", "tag": "done"}),
        ],
    },
    {
        "slug": "construction-cleanup", "title": "Construction site cleanup", "service": "construction-cleanup",
        "cover": "truck_debris", "video": "S3vcLNdFKqE", "note": "Photos from recent Rempel job sites.",
        "summary": "Building scrap and site debris loaded and hauled so the build can keep moving.",
        "beats": [
            ("site", "Debris on site", "Leftover lumber and scrap building up on the lot.", {"img": "site_debris", "tag": "before"}),
            ("equipment", "Equipment when it helps", "A skid steer for the heavy, bulky loads.", {"img": "skidsteer"}),
            ("carry", "Carried out by hand", "Panels and boards carried out to the truck.", {"img": "carry_board"}),
            ("load", "One big load", "A full truck box, hauled off site.", {"img": "truck_debris", "tag": "done"}),
        ],
    },
    {
        "slug": "yard-cleanups", "title": "Yard and brush cleanups", "service": "yard-waste-removal",
        "cover": "brush_fence", "note": "Photos from recent Rempel yard jobs.",
        "summary": "Branches and brush piles cleared from yards and fence lines.",
        "beats": [
            ("brush", "Brush along the fence", "Branches and trimmings piled up along the back fence.", {"img": "brush_fence", "tag": "before"}),
            ("load", "Loaded up", "Brush is bulky. It goes in by the armful.", {"img": "trailer_branches"}),
            ("gone", "Hauled away", "A full load, off to be disposed of properly.", {"img": "trailer_branches_b", "tag": "done"}),
        ],
    },
    {
        "slug": "household-junk", "title": "Household junk and furniture", "service": "junk-removal",
        "cover": "truck_couch", "video": "4VdWQjVnMAo", "note": "Photos from recent Rempel pickups.",
        "summary": "Couches, bins, boxes and odds and ends carried out and loaded.",
        "beats": [
            ("pile", "On the driveway", "Scrap and junk gathered up, ready to go.", {"img": "scrap_driveway", "tag": "before"}),
            ("couch", "Furniture loaded", "Couches and furniture carried out and strapped in.", {"img": "truck_couch"}),
            ("load", "Everything in one trip", "Bins, boxes and household junk in one load.", {"img": "truck_load", "tag": "done"}),
        ],
    },
    {
        "slug": "appliance-pickups", "title": "Appliance pickups", "service": "appliance-removal",
        "cover": "appliances_truck", "note": "Photos from recent Rempel pickups.",
        "summary": "Old fridges and washers carried out and taken for recycling.",
        "beats": [
            ("fridge", "Old fridges", "Out of the garage or basement and onto the truck.", {"img": "fridge_old", "tag": "before"}),
            ("washer", "Washers and dryers", "Broken or just replaced, we haul them away.", {"img": "washer_red"}),
            ("load", "Loaded together", "A fridge and a washer, one trip.", {"img": "appliances_truck", "tag": "done"}),
        ],
    },
]
PROJ = {p["slug"]: p for p in PROJECTS}

# Blog posts live in content/blog/<slug>.txt (see README for the format). Newest first.
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def load_posts():
    posts = []
    for f in sorted((ROOT / "content" / "blog").glob("*.txt")):
        head, _, body = f.read_text(encoding="utf-8").partition("\n\n")
        meta = dict(line.split(":", 1) for line in head.splitlines() if ":" in line)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        meta["slug"] = f.stem
        meta["body"] = body.strip()
        y, m, d = meta["date"].split("-")
        meta["date_text"] = f"{MONTHS[int(m) - 1]} {int(d)}, {y}"
        posts.append(meta)
    return sorted(posts, key=lambda p: p["date"], reverse=True)


def wix_or_key(v):
    return WIX.replace("d0f614_", "") + v if v.startswith("d0f614_") else img(v)


def inline(text):
    t = e(fill(text) if "{phone}" in text else text)
    phone = e(SITE["phone_display"])
    return t.replace(phone, f'<a href="tel:{SITE["phone_e164"]}">{phone}</a>')


def render_post_body(body):
    out, first_p = [], True
    for block in [b.strip() for b in body.split("\n\n") if b.strip()]:
        if block.startswith("## "):
            out.append(f"<h2>{e(block[3:])}</h2>")
        elif block.startswith("> "):
            out.append(f"<blockquote><p>{inline(block[2:])}</p></blockquote>")
        elif block.startswith("!img "):
            src, _, cap = block[5:].partition("|")
            cap = cap.strip()
            out.append(f'<figure><img src="{wix_or_key(src.strip())}" alt="{e(cap)}" loading="lazy">{f"<figcaption>{e(cap)}</figcaption>" if cap else ""}</figure>')
        else:
            cls = ' class="lead"' if first_p else ""
            first_p = False
            out.append(f"<p{cls}>{inline(block)}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------- helpers
e = html.escape
CURRENT_DEPTH = 0


def url(path=""):
    if not LOCAL:
        return "/" + path
    return "../" * CURRENT_DEPTH + path + ("index.html" if path == "" or path.endswith("/") else "")


def fill(text):
    return text.format(phone=SITE["phone_display"], cuft=SITE["truck_cuft"], kg=SITE["truck_kg"])


def svg(path_d, extra=""):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{path_d}</svg>'


I_PHONE = svg('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>')
I_CAMERA = svg('<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>')
I_CHECK = svg('<path d="M20 6 9 17l-5-5"/>')
I_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z" fill="currentColor"/></svg>'


def call_btn(cls="btn--sun", label=None):
    return f'<a class="btn {cls}" href="tel:{SITE["phone_e164"]}">{I_PHONE}{e(label or "Call " + SITE["phone_display"])}</a>'


def text_btn(cls="btn--line", label="Text us a photo"):
    return f'<a class="btn {cls}" href="sms:{SITE["phone_e164"]}">{I_CAMERA}{e(label)}</a>'


def quote_btn(cls="btn--line", label="Send photos online", service=None):
    q = f"?service={service}" if service else ""
    return f'<a class="btn {cls}" href="{url("quote/")}{q}">{e(label)}</a>'


def tag(kind):
    if not kind:
        return ""
    if kind == "before":
        return '<span class="tag tag--before">Before</span>'
    if kind == "done":
        return f'<span class="tag tag--done">{I_CHECK}Gone</span>'
    return f'<span class="tag">{e(kind)}</span>'


I_ARROWS = svg('<path d="M9 6l-6 6 6 6M15 6l6 6-6 6"/>')

# Before/after sliders. "split" = one side-by-side photo (left before, right after);
# otherwise two photos of the same spot. Only real Rempel photos.
SLIDERS = {
    "carpet": {"title": "Carpet and underlay tear-out", "before": "carpet_ba", "split": True, "ratio": "520 / 530",
               "labels_in_photo": True, "line": "Torn-out carpet and underlay piled out front, then the same yard cleared.", "link": "our-work/tear-outs/"},
    "scrap": {"title": "Scrap metal pickup", "before": "scrap_before", "after": "scrap_after", "ratio": "1 / 1",
              "line": "A scrap pile beside a lot, then the same spot hauled clear.", "link": "our-work/scrap-metal-pickup/"},
}


def ba_slider(key, ratio=None, hint=True):
    d = SLIDERS[key]
    ratio = ratio or d["ratio"]
    if d.get("split"):
        layers = (f'<div class="ba-layer ba-layer--split ba-before" style="background-image:url(\'{img(d["before"])}\')"></div>'
                  f'<div class="ba-layer ba-layer--split ba-after" style="background-image:url(\'{img(d["before"])}\')"></div>')
    else:
        layers = (f'<div class="ba-layer ba-before" style="background-image:url(\'{img(d["before"])}\')"></div>'
                  f'<div class="ba-layer ba-after" style="background-image:url(\'{img(d["after"])}\')"></div>')
    tags = "" if d.get("labels_in_photo") else tag("before") + tag("done")
    return f'''<div class="ba" style="--ba-ratio:{ratio}" role="group" aria-label="Before and after: {e(d["title"])}">
  {layers}{tags}
  <div class="ba-handle"><span class="ba-knob">{I_ARROWS}</span></div>
  {'<span class="ba-hint">Drag to compare</span>' if hint else ''}
  <input type="range" min="0" max="100" value="50" step="0.5" aria-label="Drag to compare before and after: {e(d["title"])}">
</div>'''


def ba_card(key):
    d = SLIDERS[key]
    return f'''<div class="ba-card">{ba_slider(key)}
  <div><h3>{e(d["title"])}</h3><p>{e(d["line"])} <a href="{url(d["link"])}">See the job</a></p></div>
</div>'''


def video_card(v):
    thumb = f"https://i.ytimg.com/vi/{v['id']}/oardefault.jpg"
    return f'''<div class="video">
  <button class="yt" type="button" data-yt="{v["id"]}" style="--thumb:url('{thumb}')" aria-label="Play video: {e(v["title"])}"><span class="yt-play">{I_PLAY}</span></button>
  <div><h3>{e(v["title"])}</h3><p>{e(v["line"])}</p></div>
</div>'''


def project_card(p):
    s = SVC[p["service"]]
    return f'''<a class="job-card" href="{url("our-work/" + p["slug"] + "/")}" data-service="{p["service"]}">
  <div class="job-thumb"><img src="{img(p["cover"])}" alt="{e(p["title"])}" loading="lazy">{'<span class="tag">' + I_PLAY + 'Video</span>' if p.get("video") else ""}</div>
  <div><h3>{e(p["title"])}</h3><div class="job-meta">{e(s["name"])}</div></div>
</a>'''


def cta_band(title="Text us a photo of what needs to go.", sub="We'll reply with a price. No need for anyone to come out first.", service=None):
    return f'''<section class="cta-band">
  <div class="wrap">
    <div><h2>{e(title)}</h2><p>{e(sub)}</p></div>
    <div class="btn-row">{call_btn("btn--navy")}{text_btn("btn--white", "Text us a photo")}{quote_btn("btn--line", service=service)}</div>
  </div>
</section>'''


def steps_block(process=None):
    process = process or [
        ("Send a photo", "Text a picture of the junk, project or property, or upload it online."),
        ("Get your price", "We reply with straightforward pricing and no hidden fees."),
        ("We haul it away", "We load it, clean up, and it's gone in a snap."),
    ]
    return '<ol class="steps">' + "".join(f"<li><h3>{e(h)}</h3><p>{e(p)}</p></li>" for h, p in process) + "</ol>"


def takes_list(items):
    return '<ul class="takes">' + "".join(f"<li>{I_CHECK}{e(t)}</li>" for t in items) + "</ul>"


def tags_head():
    ids = [i for i in (SITE["ga4_id"], SITE["gads_id"]) if i]
    if not ids:
        return ""
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={ids[0]}"></script>'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());"
            + "".join(f"gtag('config','{i}');" for i in ids) + "</script>")


NAV = [("Services", "services/"), ("Our work", "our-work/"), ("Videos", "our-work/#videos"), ("About", "about/"), ("Blog", "blog/")]


def nav_href(p):
    if "#" in p:
        base, frag = p.split("#")
        return url(base) + "#" + frag
    return url(p)


def page(path, title, meta, body, active=None, schema=None, head_extra="", pre_body=""):
    canonical = SITE["domain"] + "/" + path
    nav = "".join(f'<a href="{nav_href(p)}"{" aria-current=page" if active == p else ""}>{e(n)}</a>' for n, p in NAV)
    menu = "".join(f'<a href="{nav_href(p)}">{e(n)}</a>' for n, p in NAV + [("Get a price", "quote/")])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(sc)}</script>' for sc in (schema if isinstance(schema, list) else [schema] if schema else []))
    return f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(meta)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(meta)}">
<meta property="og:image" content="{img("chad_truck")}">
<meta name="theme-color" content="#ffc233">
<link rel="preload" href="{asset("assets/fonts/archivo-var.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{asset("assets/fonts/figtree-var.woff2")}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset("assets/site.css")}">
{tags_head()}{ld}{head_extra}
</head>
<body>
{pre_body}<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="{url("")}"><img src="{img("logo")}" alt="Rempel Removal home" width="127" height="55"></a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <a class="header-phone" href="tel:{SITE["phone_e164"]}">{I_PHONE}{e(SITE["phone_display"])}</a>
    <a class="btn btn--sun" href="{url("quote/")}">Get a price</a>
    <details class="menu"><summary>Menu</summary><div class="menu-panel">{menu}<a href="tel:{SITE["phone_e164"]}">Call {e(SITE["phone_display"])}</a></div></details>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div>
      <h2>Rempel Removal</h2>
      <p>Junk removal, light demolition and property cleanouts in {e(SITE["area"])}.</p>
      <a class="footer-phone" href="tel:{SITE["phone_e164"]}">{e(SITE["phone_display"])}</a><br>
      <a href="mailto:{SITE["email"]}">{e(SITE["email"])}</a>
    </div>
    <div>
      <h2>Services</h2>
      <ul>{"".join(f'<li><a href="{url(s["slug"] + "/")}">{e(s["name"])}</a></li>' for s in SERVICES)}</ul>
    </div>
    <div>
      <h2>Company</h2>
      <ul>
        <li><a href="{url("our-work/")}">Our work</a></li>
        <li><a href="{url("about/")}">About Chad</a></li>
        <li><a href="{url("blog/")}">Blog</a></li>
        <li><a href="{url("quote/")}">Get a price</a></li>
        <li><a href="{SITE["review_link"]}">Leave a Google review</a></li>
        <li><a href="{SITE["youtube"]}">YouTube</a></li>
        <li><a href="{SITE["instagram"]}">Instagram</a></li>
        <li><a href="{SITE["facebook"]}">Facebook</a></li>
      </ul>
    </div>
    <div class="footer-base">© 2026 Rempel Removal Services. Gone in a snap.</div>
  </div>
</footer>
<dialog class="vbox" aria-label="Video"><button class="vbox-close" type="button">Close</button><div class="vbox-frame"></div></dialog>
<nav class="callbar" aria-label="Contact">{call_btn("btn--sun", "Call")}{text_btn("btn--line", "Text a photo")}</nav>
<script src="{asset("assets/site.js")}" defer></script>
</body>
</html>
'''


def write(path, text):
    target = OUT / path if path.endswith(".html") else (OUT / path / "index.html" if path else OUT / "index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def at(path):
    global CURRENT_DEPTH
    CURRENT_DEPTH = path.count("/")


def videos_section(ids=None, title="Watch us work", sub="Short videos from real Rempel jobs around Saskatoon.", tone="section--navy", anchor=""):
    vids = [VID[i] for i in ids] if ids else VIDEOS
    cls = "videos" + (" videos--3" if len(vids) == 3 else " videos--1" if len(vids) == 1 else "")
    more = f'<a class="btn {"btn--sun" if tone == "section--navy" else "btn--navy"}" href="{SITE["youtube"]}">More on YouTube</a>'
    return f'''<section class="section {tone}"{f' id="{anchor}"' if anchor else ""}>
  <div class="wrap">
    <div class="section-head section-head--row"><div><h2>{e(title)}</h2><p style="margin-top:.75rem">{e(sub)}</p></div>{more}</div>
    <div class="{cls}">{"".join(video_card(v) for v in vids)}</div>
  </div>
</section>'''


# ---------------------------------------------------------------- pages
I_PIN = svg('<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>')

INTRO_HEAD = """<script>(function(){try{var d=document.documentElement;if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&!sessionStorage.getItem('rr-intro')){d.classList.add('intro-on');sessionStorage.setItem('rr-intro','1');setTimeout(function(){d.classList.remove('intro-on')},3200)}}catch(e){}})();</script>"""


def intro_screen():
    letters = "".join(f'<span style="--i:{i}">{ch}</span>' for i, ch in enumerate("REMPEL"))
    return f'''<div class="intro-screen" aria-hidden="true">
  <div class="intro-lockup">
    <div class="intro-word">{letters}</div>
    <div class="intro-row"><span class="intro-bar"></span><span class="intro-removal">REMOVAL</span><span class="intro-bar"></span></div>
    <div class="intro-tag">Gone in a snap.</div>
  </div>
</div>
'''


def build_home():
    at("")
    if HERO_VIDEO:
        v = HERO_VIDEO
        media_inner = (f'<video autoplay muted loop playsinline preload="metadata" poster="{img(v["poster"])}">'
                       + (f'<source src="{asset(v["webm"])}" type="video/webm">' if v.get("webm") else "")
                       + f'<source src="{asset(v["mp4"])}" type="video/mp4"></video>')
        media_attr = ""
    else:
        media_inner = "".join(
            f'<figure class="slide{" is-on" if i == 0 else ""}"><img src="{img(k)}" alt="{e(cap)}"{" fetchpriority=high" if i == 0 else " loading=lazy"}><figcaption><span class="tag">{e(cap)}</span></figcaption></figure>'
            for i, (k, cap) in enumerate(HERO_SLIDES))
        media_inner += '<div class="slide-dots">' + "".join(f'<button type="button" aria-label="Show photo {i + 1}: {e(cap)}"></button>' for i, (_, cap) in enumerate(HERO_SLIDES)) + "</div>"
        media_attr = ' data-slides="5000"'
    intro = f'''<section class="intro">
  <div class="intro-grid">
    <div class="intro-copy">
      <span class="intro-kicker intro-fade" style="--i:0">{I_PIN}Locally owned and operated</span>
      <h1><span class="h1-place intro-fade" style="--i:1">Junk removal in Saskatoon</span><span class="h1-line"><span style="--i:2">Need it gone?</span></span><span class="h1-line"><span style="--i:3">We'll haul it away.</span></span></h1>
      <p class="intro-sub intro-fade" style="--i:4">Junk removal, property cleanouts and light demolition. Text us a photo and get a straightforward price.</p>
      <div class="btn-row intro-fade" style="--i:5">{call_btn("btn--navy")}{text_btn("btn--line")}</div>
      <ul class="intro-points intro-fade" style="--i:6"><li>{I_CHECK}Licensed and insured</li><li>{I_CHECK}No bin needed</li><li>{I_CHECK}Donated or recycled where possible</li></ul>
    </div>
    <div class="intro-media"{media_attr}>
      {media_inner}
      <div class="intro-chip"><strong>{SITE["truck_cuft"]} cu ft</strong><span>truck, up to {SITE["truck_kg"]} kg a load</span></div>
    </div>
  </div>
</section>'''

    stats = f'''<section class="stats" aria-label="Rempel Removal in numbers"><div class="wrap"><ul>
  <li><strong data-count="{SITE["truck_cuft"]}" data-suffix=" cu ft">{SITE["truck_cuft"]} cu ft</strong><span>of truck space per load</span></li>
  <li><strong data-count="5000" data-suffix=" kg">{SITE["truck_kg"]} kg</strong><span>hauled in a single trip</span></li>
  <li><strong data-count="17">17</strong><span>seasons of pro football for owner Chad Rempel</span></li>
  <li><strong data-count="60" data-suffix="+ yrs">60+ yrs</strong><span>of the Rempel family building in Saskatoon</span></li>
</ul></div></section>'''

    first_video = VIDEOS[0]["id"]
    if BANNER_VIDEO:
        bm = f'<video autoplay muted loop playsinline preload="none" poster="{img(BANNER_VIDEO["poster"])}"><source src="{asset(BANNER_VIDEO["mp4"])}" type="video/mp4"></video>'
    else:
        bm = f'<img src="{img("truck_debris")}" alt="The Rempel Removal truck box, loaded full" loading="lazy">'
    banner = f'''<section class="banner">
  <div class="banner-media" data-banner>
    {bm}
    <div class="banner-copy">
      <h2>Gone in a snap.</h2>
      <p>One call, one big truck, and a crew that does the lifting. See them at work.</p>
      <div class="btn-row"><button class="btn btn--sun play-btn" type="button" data-lightbox="{first_video}">{I_PLAY}Play video</button><a class="btn btn--line" style="color:var(--white)" href="#videos">All videos</a></div>
    </div>
  </div>
</section>'''

    how_items = [
        ("scrap_before", "Text us a photo", "Send a picture of what needs to go and get a straightforward price back."),
        ("carry_board", "We do the lifting", "The crew carries it out and loads the truck. No bin in your driveway."),
        ("scrap_after", "Gone in a snap", "Everything hauled away and the space swept clean."),
    ]
    how = f'''<section class="section section--sun">
  <div class="wrap">
    <div class="section-head" data-reveal><h2>How it works</h2><p>Three steps, and you never have to lift a thing.</p></div>
    <ol class="how-cards">{"".join(f'<li class="how-card" data-reveal style="--i:{i}"><figure><img src="{img(k)}" alt="" loading="lazy"{" style=\"object-position:50% 15%\"" if k == "carry_board" else ""}></figure><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for i, (k, t, d) in enumerate(how_items))}</ol>
  </div>
</section>'''

    owner = f'''<section class="section">
  <div class="wrap owner">
    <div class="owner-photo"><img src="{img("football_a")}" alt="Chad Rempel during his pro football career" loading="lazy"><span class="tag">17 seasons in the CFL and NFL</span></div>
    <div>
      <h2>A local crew that does the little things right</h2>
      <p class="lede">Rempel Removal is run by Chad Rempel. He played 17 seasons of pro football as a long snapper, ran Saskatoon's first Booster Juice on 8th Street, and comes from a family that ran Rempel Brothers Construction for more than 60 years.</p>
      <div class="facts">
        <div class="fact"><strong>{SITE["truck_cuft"]} cu ft</strong><span>per load, up to {SITE["truck_kg"]} kg</span></div>
        <div class="fact"><strong>1 photo</strong><span>is all it takes to get a price</span></div>
        <div class="fact"><strong>60+ years</strong><span>of the Rempel family building in Saskatoon</span></div>
      </div>
      <p style="margin-top:1.75rem"><a class="btn btn--navy" href="{url("about/")}">Meet Chad</a></p>
    </div>
  </div>
</section>'''

    pair = f'''<section class="section section--sky">
  <div class="wrap">
    <div class="section-head"><h2>Before and after</h2><p>Real Rempel jobs. Drag the handle to see the difference.</p></div>
    <div class="ba-cards">{ba_card("carpet")}{ba_card("scrap")}</div>
  </div>
</section>'''

    cards_html = ""
    for i, s in enumerate(SERVICES):
        wide = " svc--wide" if i == 0 else ""
        cards_html += f'<a class="svc{wide}" href="{url(s["slug"] + "/")}"><img src="{img(s["img"])}" alt="" loading="lazy"><div class="svc-body"><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p></div></a>'
    services = f'''<section class="section section--mist" id="services">
  <div class="wrap">
    <div class="section-head"><h2>What we haul</h2><p>One call for junk, cleanouts, tear-outs and commercial snow.</p></div>
    <div class="svc-grid">{cards_html}</div>
  </div>
</section>'''


    projects = f'''<section class="section">
  <div class="wrap">
    <div class="section-head section-head--row"><div><h2>Recent work</h2><p style="margin-top:.75rem">Real photos from Rempel jobs around Saskatoon.</p></div><a class="btn btn--navy" href="{url("our-work/")}">See all our work</a></div>
    <div class="jobs">{"".join(project_card(PROJ[k]) for k in ["tear-outs", "property-cleanouts", "construction-cleanup"])}</div>
  </div>
</section>'''

    reviews = f'''<section class="section section--mist">
  <div class="wrap">
    <div class="section-head"><h2>What customers say</h2></div>
    <div class="reviews">
      <img src="{img("fishtank_review")}" alt="Five-star Google review of a fish tank removal" loading="lazy">
      <img src="{img("brush_review")}" alt="Five-star Google review of a brush pile removal" loading="lazy">
      <div class="reviews-cta">
        <div class="stars" aria-hidden="true">★★★★★</div>
        <p style="margin:0">Had a good experience with us? A Google review helps other Saskatoon families find a crew they can trust.</p>
        <a class="btn btn--navy" href="{SITE["review_link"]}">Leave a review</a>
      </div>
    </div>
  </div>
</section>'''

    schema = {
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": SITE["name"],
        "url": SITE["domain"], "telephone": SITE["phone_e164"], "email": SITE["email"],
        "image": img("chad_truck"), "logo": img("logo"),
        "areaServed": {"@type": "City", "name": "Saskatoon"},
        "address": {"@type": "PostalAddress", "addressLocality": "Saskatoon", "addressRegion": "SK", "addressCountry": "CA"},
        "sameAs": [SITE["instagram"], SITE["facebook"], SITE["youtube"]],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}} for s in SERVICES],
    }
    body = intro + stats + banner + how + owner + videos_section(anchor="videos") + pair + services + projects + reviews + cta_band()
    # Gentle fade-up for below-the-fold blocks on the homepage (staggered within each group)
    for pat in (r'<a class="svc[^>]*>', r'<div class="video">', r'<a class="job-card[^>]*>', r'<div class="ba-card">', r'<div class="owner-photo">', r'<div class="reviews-cta">'):
        counter = iter(range(1000))
        body = re.sub(pat, lambda m: m.group(0)[:-1] + f' data-reveal style="--i:{next(counter) % 4}">', body)
    write("", page("", "Junk Removal Saskatoon | Rempel Removal", "Junk removal, light demolition and property cleanouts in Saskatoon. Text a photo for a fast price. One big truck: up to 560 cu ft per trip.", body, schema=schema,
                   head_extra=INTRO_HEAD if INTRO_SCREEN else "", pre_body=intro_screen() if INTRO_SCREEN else ""))


def build_services_index():
    at("services/")
    cards = "".join(f'<a class="svc" href="{url(s["slug"] + "/")}"><img src="{img(s["img"])}" alt="" loading="lazy"><div class="svc-body"><h3>{e(s["name"])}</h3><p>{e(s["short"])}</p></div></a>' for s in SERVICES)
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>Services</h1><p>Junk removal, cleanouts, light demolition and commercial snow hauling in {e(SITE["area"])}.</p>
  <div class="btn-row">{call_btn("btn--navy")}{text_btn()}</div></div></div></section>
<section class="section"><div class="wrap"><div class="svc-grid">{cards}</div></div></section>''' + cta_band()
    write("services/", page("services/", "Junk Removal & Hauling Services Saskatoon | Rempel Removal", "Every service Rempel Removal offers in Saskatoon: junk removal, furniture and appliance removal, cleanouts, construction cleanup, light demolition, yard waste and snow hauling.", body, active="services/"))


def build_service(s):
    at(s["slug"] + "/")
    head_img = f'<img src="{img(s["img"])}" alt="{e(s["name"])} by Rempel Removal">'
    faq = s.get("faq", COMMON_FAQ)
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(fill(a))}</p></details>" for q, a in faq)
    projs = [PROJ[j] for j in s["jobs"] if j in PROJ]
    own = [p for p in PROJECTS if p["service"] == s["slug"]]
    strip_keys = []
    for p in own:
        strip_keys += [m["img"] for _, _, _, m in p["beats"] if m.get("img")]
    strip = ""
    if len(strip_keys) >= 3:
        strip = f'''<section class="section section--mist"><div class="wrap">
  <div class="section-head"><h2>From our recent jobs</h2></div>
  <div class="strip">{"".join(f'<img src="{img(k)}" alt="{e(s["name"])} job photo" loading="lazy">' for k in strip_keys[:6])}</div></div></section>'''
    ba_key = {"light-demolition": "carpet", "junk-removal": "scrap"}.get(s["slug"])
    ba_html = ""
    if ba_key:
        ba_html = f'''<section class="section section--sky"><div class="wrap pair-grid">
  <div><h2>Before and after</h2><p class="lede" style="margin-top:1rem">{e(SLIDERS[ba_key]["line"])} Drag the handle to compare.</p>
  <div class="btn-row" style="margin-top:1.5rem"><a class="btn btn--navy" href="{url(SLIDERS[ba_key]["link"])}">See the job</a></div></div>
  <div class="ba-single">{ba_slider(ba_key)}</div></div></section>'''
    video = videos_section([s["video"]], title="Watch one", sub=VID[s["video"]]["line"], tone="section--navy") if s.get("video") else ""
    projects = ""
    if projs:
        projects = f'''<section class="section"><div class="wrap">
  <div class="section-head"><h2>Recent work</h2></div>
  <div class="jobs">{"".join(project_card(p) for p in projs)}</div></div></section>'''
    points = "".join(f'<div class="point"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in s["points"])
    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": fill(a)}} for q, a in faq]}
    body = f'''<section class="page-head"><div class="wrap">
  <div>
    <div class="crumbs"><a href="{url("services/")}">Services</a></div>
    <h1>{e(s["h1"])}</h1>
    <p>{e(s["intro"])}</p>
    <div class="btn-row">{call_btn("btn--navy")}{text_btn()}</div>
  </div>
  {head_img}
</div></section>
<section class="section"><div class="wrap">
  <div class="section-head"><h2>{e(s.get("takes_title", "What we take"))}</h2></div>
  {takes_list(s["takes"])}
  <div class="points" style="margin-top:3rem">{points}</div>
</div></section>
{strip}
{ba_html}
<section class="section section--sun"><div class="wrap">
  <div class="section-head"><h2>{"Our process" if s.get("process") else "How it works"}</h2></div>
  {steps_block(s.get("process"))}
</div></section>
{video}
{projects}
<section class="section section--mist"><div class="wrap">
  <div class="section-head"><h2>Questions</h2></div>
  <div class="faq">{faq_html}</div>
</div></section>
{cta_band(title=s.get("cta", "Text us a photo of what needs to go."), service=s["slug"])}'''
    write(s["slug"] + "/", page(s["slug"] + "/", s["title"], s["meta"], body, active="services/", schema=faq_schema))


def build_our_work():
    at("our-work/")
    used = [s for s in SERVICES if any(p["service"] == s["slug"] for p in PROJECTS)]
    filters = '<button type="button" data-filter="all" aria-pressed="true">All work</button>' + "".join(
        f'<button type="button" data-filter="{s["slug"]}" aria-pressed="false">{e(s["name"])}</button>' for s in used)
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>Our work</h1>
  <p>Real Rempel jobs around Saskatoon, photographed by the crew. Open one to scroll through it.</p></div></div></section>
<section class="section"><div class="wrap">
  <div class="filters" data-filters role="group" aria-label="Filter by service">{filters}</div>
  <div class="jobs">{"".join(project_card(p) for p in PROJECTS)}</div>
</div></section>''' + videos_section(anchor="videos") + cta_band(title="Got one like these?")
    write("our-work/", page("our-work/", "Our Work: Junk Removal Jobs in Saskatoon | Rempel Removal", "Photos and videos of real Rempel Removal jobs: cleanouts, tear-outs, yard waste, construction cleanup and junk removal across Saskatoon.", body, active="our-work/"))


def beat_media(key, m, title, mobile=False, on=False):
    attrs = "" if mobile else f' data-media="{key}"'
    cls = ' class="is-on"' if on else ""
    if "ba" in m:
        html_ba = ba_slider(m["ba"], ratio="4 / 3" if mobile else None, hint=True)
        return html_ba.replace('<div class="ba"', f'<div class="ba{" is-on" if on else ""}"{attrs}', 1)
    return f'<img{cls}{attrs} src="{img(m["img"])}" alt="{e(title)}" loading="lazy">'


def build_project(p, nxt):
    at("our-work/" + p["slug"] + "/")
    s = SVC[p["service"]]
    media, steps = [], []
    n = len(p["beats"])
    for i, (key, heading, text, m) in enumerate(p["beats"]):
        media.append(beat_media(key, m, heading, on=(i == 0)))
        steps.append(f'''<div class="story-step" data-step="{key}">
  <div class="step-media">{beat_media(key, m, heading, mobile=True)}</div>
  <span class="num">{i + 1} of {n}</span>
  <h2>{e(heading)}</h2><p>{e(text)}</p>{tag(m.get("tag"))}
</div>''')
    if p.get("frames"):
        f = p["frames"]
        media = [f'<canvas class="is-on" data-media="all" data-frames="{asset(f["desktop"])}" data-count="{f["count"]}"></canvas>']
    note = f'<p class="note" style="font-size:1rem;margin-top:-.25rem">{e(p["note"])}</p>' if p.get("note") else ""
    video = videos_section([p["video"]], title="Watch a Rempel job like this", sub=VID[p["video"]]["line"]) if p.get("video") else ""
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <div class="crumbs"><a href="{url("our-work/")}">Our work</a> / <a href="{url(s["slug"] + "/")}">{e(s["name"])}</a></div>
  <h1>{e(p["title"])}</h1><p>{e(p["summary"])}</p>{note}</div></div></section>
<section class="section"><div class="wrap story" data-story>
  <div class="story-media">{"".join(media)}</div>
  <div class="story-steps">{"".join(steps)}</div>
</div></section>
{video}
<section class="section section--mist"><div class="wrap two-col">
  <div><h2>Got one like this?</h2><p class="lede" style="margin-top:1rem">Text us a photo and we'll send a price.</p><div class="btn-row">{text_btn("btn--navy")}{call_btn("btn--line")}</div></div>
  <div class="points">
    <div class="point"><h3><a href="{url(s["slug"] + "/")}">{e(s["name"])}</a></h3><p>{e(s["short"])}</p></div>
    <div class="point"><h3><a href="{url("our-work/" + nxt["slug"] + "/")}">Next: {e(nxt["title"])}</a></h3><p>{e(nxt["summary"])}</p></div>
  </div>
</div></section>'''
    write("our-work/" + p["slug"] + "/", page("our-work/" + p["slug"] + "/", f'{p["title"]} in Saskatoon | Rempel Removal', p["summary"], body, active="our-work/"))


def build_about():
    at("about/")
    body = f'''<section class="page-head"><div class="wrap">
  <div><h1>Meet Chad Rempel</h1>
  <p>Rempel Removal starts with Chad, who brings a lifetime of hard work, leadership and community roots to every job.</p>
  <div class="btn-row">{call_btn("btn--navy")}{text_btn()}</div></div>
  <img src="{img("chad_truck")}" alt="Chad Rempel with the Rempel Removal truck">
</div></section>
<section class="section"><div class="wrap two-col">
  <div><h2>From long snapping to junk removal</h2></div>
  <div>
    <p class="lede">For 17 years, Chad owned and operated the first Booster Juice location in Saskatoon, on 8th Street. In those same years he played 17 seasons of professional football in the CFL and NFL as a long snapper.</p>
    <p>As a long snapper, Chad learned that success comes down to doing the little things right: being consistent, dependable, disciplined and ready when your team needs you. Those values shaped how he built his business and how he works with people today.</p>
    <p>Chad's family owned Rempel Brothers Construction for more than 60 years, building a legacy of hard work, trust and doing the job right. He's proud to carry that forward with Rempel Removal.</p>
    <p>Whether it's a garage packed to the ceiling, a pile of demolition debris or a full property cleanout, Chad and his team will have it gone in a snap.</p>
    <p><a class="btn btn--navy" href="{url("blog/care/")}">Read Chad's post: CARE</a></p>
    <div class="about-photos" style="margin-top:2rem">
      <img src="{img("football_a")}" alt="Chad Rempel during his pro football career" loading="lazy">
      <img src="{img("football_b")}" alt="Chad Rempel long snapping" loading="lazy">
    </div>
  </div>
</div></section>
<section class="section section--sun"><div class="wrap">
  <div class="section-head"><h2>What we stand for</h2></div>
  <div class="points">
    <div class="point" style="background:var(--white)"><h3>Trust</h3><p>Success is built on doing the little things right. We're consistent, dependable and disciplined on every job.</p></div>
    <div class="point" style="background:var(--white)"><h3>Reliability</h3><p>A 60-year family legacy of hard work and integrity. We show up and do the job right the first time.</p></div>
    <div class="point" style="background:var(--white)"><h3>Local roots</h3><p>Proudly serving Saskatoon and area, and committed to the community we grew up in.</p></div>
  </div>
</div></section>''' + videos_section() + cta_band(title="Ready to reclaim your space?")
    write("about/", page("about/", "About Rempel Removal | Meet Chad Rempel", "Meet Chad Rempel: 17 seasons as a pro long snapper, Saskatoon's first Booster Juice, and a family construction legacy of 60+ years. Now he runs Rempel Removal.", body, active="about/"))


def post_card(p, big=False):
    fit = ' style="object-fit:contain;background:var(--white)"' if p.get("cover_fit") == "contain" else ""
    first = next((x for x in p["body"].split("\n\n") if x and not x.startswith(("#", ">", "!"))), "")
    return f'''<a class="post-card{" post-card--big" if big else ""}" href="{url("blog/" + p["slug"] + "/")}">
  <div class="post-cover"><img src="{wix_or_key(p["cover"])}" alt="" loading="lazy"{fit}></div>
  <div class="post-card-body"><span class="post-meta">{e(p["date_text"])} · {e(p["author"])}</span><h2>{e(p["title"])}</h2><p>{e(p["description"])}</p></div>
</a>'''


def build_blog():
    posts = load_posts()
    at("blog/")
    cards = post_card(posts[0], big=True) + "".join(post_card(p) for p in posts[1:])
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>Blog</h1><p>Local tips on junk removal and decluttering that Saskatoon homeowners can use, plus a few words from Chad.</p></div></div></section>
<section class="section section--mist"><div class="wrap"><div class="post-grid">{cards}</div></div></section>''' + cta_band()
    write("blog/", page("blog/", "Junk Removal Saskatoon Blog | Rempel Removal", "Local tips and advice on junk removal that Saskatoon homeowners can trust.", body, active="blog/"))

    for i, p in enumerate(posts):
        at("blog/" + p["slug"] + "/")
        others = [q for q in posts if q is not p][:2]
        schema = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"],
                  "author": {"@type": "Person" if p["author"] != SITE["name"] else "Organization", "name": p["author"]},
                  "publisher": {"@type": "Organization", "name": SITE["name"], "logo": {"@type": "ImageObject", "url": img("logo")}},
                  "image": wix_or_key(p["cover"]), "description": p["description"],
                  "mainEntityOfPage": SITE["domain"] + "/blog/" + p["slug"] + "/"}
        body = f'''<article>
<header class="post-head"><div class="wrap">
  <div class="crumbs"><a href="{url("blog/")}">Blog</a></div>
  <h1>{e(p["title"])}</h1>
  <p class="post-meta">{e(p["date_text"])} · {e(p["author"])}</p>
</div></header>
<div class="section"><div class="wrap"><div class="prose">
{render_post_body(p["body"])}
</div></div></div>
</article>
<section class="section section--mist"><div class="wrap">
  <div class="section-head"><h2>More from the blog</h2></div>
  <div class="post-grid">{"".join(post_card(q) for q in others)}</div>
</div></section>''' + cta_band(title="Got a pile that needs to disappear?")
        write("blog/" + p["slug"] + "/", page("blog/" + p["slug"] + "/", f'{p["title"]} | Rempel Removal Blog', p["description"], body, active="blog/", schema=schema))


def build_quote():
    at("quote/")
    opts = "".join(f'<option value="{s["slug"]}">{e(s["name"])}</option>' for s in SERVICES)
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>Get a price</h1><p>Send a few photos of what needs to go and we'll reply with a price.</p></div></div></section>
<section class="section section--mist"><div class="wrap quote-grid">
  <form class="form" name="quote" method="POST" action="{url("thanks/")}" data-netlify="true" netlify-honeypot="company" enctype="multipart/form-data" data-track>
    <input type="hidden" name="form-name" value="quote">
    <p class="visually-hidden"><label>Leave this empty <input name="company"></label></p>
    <div class="field-row">
      <div class="field"><label for="f-name">Name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" required></div>
    </div>
    <div class="field"><label for="f-email">Email <span class="hint">(optional)</span></label><input id="f-email" name="email" type="email" autocomplete="email"></div>
    <div class="field-row">
      <div class="field"><label for="f-service">What do you need?</label><select id="f-service" name="service">{opts}<option value="other">Something else</option></select></div>
      <div class="field"><label for="f-area">Neighbourhood or town</label><input id="f-area" name="area" autocomplete="address-level2"></div>
    </div>
    <div class="field"><label for="f-p1">Photos</label><span class="hint">Up to 3 photos, 8 MB total. Wide shots help us price it.</span>
      <input id="f-p1" name="photo1" type="file" accept="image/*">
      <input name="photo2" type="file" accept="image/*" aria-label="Second photo">
      <input name="photo3" type="file" accept="image/*" aria-label="Third photo">
    </div>
    <div class="field"><label for="f-msg">Anything we should know?</label><textarea id="f-msg" name="message" rows="4" placeholder="Stairs, access, when you'd like it gone"></textarea></div>
    <button class="btn btn--sun" type="submit">Send for a price</button>
  </form>
  <aside class="text-box">
    <h2>Faster: text us</h2>
    <p>Snap a photo and text it to us. It's the quickest way to a price.</p>
    <a class="big-phone" href="sms:{SITE["phone_e164"]}">{e(SITE["phone_display"])}</a>
    <div class="btn-row">{text_btn("btn--sun", "Text a photo")}{call_btn("btn--line", "Call instead")}</div>
    <p style="margin-top:1.5rem;margin-bottom:0">Or email <a href="mailto:{SITE["email"]}" style="color:var(--sun)">{e(SITE["email"])}</a></p>
  </aside>
</div></section>'''
    write("quote/", page("quote/", "Get a Free Junk Removal Quote Saskatoon | Rempel Removal", "Send Rempel Removal a photo of your junk for a quick, no-obligation price. Junk removal, cleanouts, tear-outs and snow hauling in Saskatoon.", body))
    at("thanks/")
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>Got it. We'll be in touch.</h1><p>Your photos are on their way to Rempel Removal. In a hurry? Call {e(SITE["phone_display"])}.</p>
  <div class="btn-row">{call_btn("btn--navy")}<a class="btn btn--line" href="{url("our-work/")}">See our work</a></div></div></div></section>'''
    write("thanks/", page("thanks/", "Thanks | Rempel Removal", "Your quote request was sent.", body))


def build_404():
    at("")
    body = f'''<section class="page-head page-head--plain"><div class="wrap"><div>
  <h1>That page is gone.</h1><p>Hauled away, maybe. Try the services list, or give us a call.</p>
  <div class="btn-row"><a class="btn btn--navy" href="{url("services/")}">See services</a>{call_btn("btn--line")}</div></div></div></section>'''
    write("404.html", page("", "Page not found | Rempel Removal", "Page not found.", body))


def build_meta():
    (OUT / "_redirects").write_text("\n".join([
        "/blank                       /furniture-removal/   301",
        "/blank-1                     /snow-removal/        301",
        "/general-junk-removal        /junk-removal/        301",
        "/light-demolition-tearouts   /light-demolition/    301",
        "/contact                     /quote/               301",
        "/about-us                    /about/               301",
        "/post/*                     /blog/:splat/         301",
    ]) + "\n")
    paths = ["", "services/", "our-work/", "about/", "blog/", "quote/"] + [s["slug"] + "/" for s in SERVICES] + ["our-work/" + p["slug"] + "/" for p in PROJECTS] + ["blog/" + p["slug"] + "/" for p in load_posts()]
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     + "".join(f"  <url><loc>{SITE['domain']}/{p}</loc></url>\n" for p in paths) + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "media").exists():
        shutil.copytree(ROOT / "media", OUT / "media")
    build_home()
    build_services_index()
    for s in SERVICES:
        build_service(s)
    build_our_work()
    for i, p in enumerate(PROJECTS):
        build_project(p, PROJECTS[(i + 1) % len(PROJECTS)])
    build_about()
    build_blog()
    build_quote()
    build_404()
    build_meta()
    print(f"Built {sum(1 for _ in OUT.rglob('*.html'))} pages into {OUT}")


if __name__ == "__main__":
    main()
