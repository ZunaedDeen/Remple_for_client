/* Rempel Removal — site behaviour. No dependencies. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var small = window.matchMedia("(max-width: 700px)");
  var track = function (name, params) { if (typeof window.gtag === "function") window.gtag("event", name, params || {}); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ---------- Frame-sequence scrubber ----------
     <canvas data-frames="media/job/desktop/{i}.webp" data-count="120"
             data-frames-mobile="media/job/mobile/{i}.webp" data-count-mobile="60" data-pad="3">
     Frames are numbered from 1. draw(progress 0..1) picks the nearest loaded frame. */
  function Scrubber(canvas) {
    var mobile = small.matches && canvas.dataset.framesMobile;
    this.pattern = mobile ? canvas.dataset.framesMobile : canvas.dataset.frames;
    this.count = parseInt(mobile ? canvas.dataset.countMobile : canvas.dataset.count, 10) || 1;
    this.pad = parseInt(canvas.dataset.pad || "3", 10);
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.frames = new Array(this.count);
    this.current = -1;
    this.load();
  }
  Scrubber.prototype.src = function (i) {
    return this.pattern.replace("{i}", String(i + 1).padStart(this.pad, "0"));
  };
  Scrubber.prototype.load = function () {
    var self = this, order = [0, this.count - 1];
    for (var step = 8; step >= 1; step = Math.floor(step / 2)) {
      for (var i = 0; i < self.count; i += step) if (order.indexOf(i) < 0) order.push(i);
      if (step === 1) break;
    }
    order.forEach(function (i) {
      var img = new Image();
      img.decoding = "async";
      img.onload = function () { self.frames[i] = img; if (self.current < 0 || i === 0) self.draw(self.lastP || 0, true); };
      img.src = self.src(i);
    });
  };
  Scrubber.prototype.draw = function (p, force) {
    this.lastP = p;
    var target = Math.round(clamp(p, 0, 1) * (this.count - 1)), i = target, d = 0;
    while (!this.frames[i] && d < this.count) { d++; i = this.frames[target - d] ? target - d : target + d; if (i < 0 || i >= this.count) i = target; }
    var img = this.frames[i];
    if (!img || (i === this.current && !force)) return;
    var c = this.canvas, r = c.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
    if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
    var s = Math.max(w / img.naturalWidth, h / img.naturalHeight);
    var iw = img.naturalWidth * s, ih = img.naturalHeight * s;
    this.ctx.drawImage(img, (w - iw) / 2, (h - ih) / 2, iw, ih);
    this.current = i;
  };

  var root = document.documentElement;
  root.classList.add("js");

  /* ---------- Opening screen: tap or key to skip ---------- */
  var screen = document.querySelector(".intro-screen");
  if (screen) {
    var endIntro = function () { root.classList.remove("intro-on"); };
    screen.addEventListener("click", endIntro);
    screen.addEventListener("animationend", function (ev) { if (ev.target === screen) endIntro(); });
    window.addEventListener("keydown", function once() { endIntro(); window.removeEventListener("keydown", once); });
  }

  /* ---------- Hero slideshow: real photos crossfade with a slow zoom ---------- */
  var media = document.querySelector("[data-slides]");
  if (media) {
    var slides = Array.prototype.slice.call(media.querySelectorAll(".slide"));
    var dots = Array.prototype.slice.call(media.querySelectorAll(".slide-dots button"));
    var ms = parseInt(media.dataset.slides, 10) || 5000, cur = 0, timer = null, visible = true;
    media.style.setProperty("--slide-ms", ms + "ms");
    var go = function (i) {
      cur = (i + slides.length) % slides.length;
      slides.forEach(function (sl, k) { sl.classList.toggle("is-on", k === cur); });
      dots.forEach(function (d, k) {
        d.classList.remove("is-on"); void d.offsetWidth;
        d.classList.toggle("is-on", k === cur); d.classList.toggle("is-done", k < cur);
        d.setAttribute("aria-current", k === cur ? "true" : "false");
      });
    };
    var play = function () { clearInterval(timer); if (!reduce && visible && !document.hidden) { media.classList.remove("is-paused"); timer = setInterval(function () { go(cur + 1); }, ms); } else { media.classList.add("is-paused"); } };
    dots.forEach(function (d, k) { d.addEventListener("click", function () { go(k); play(); }); });
    document.addEventListener("visibilitychange", play);
    if ("IntersectionObserver" in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; play(); }).observe(media);
    go(0); play();
  }

  /* ---------- Banner: widens to full-bleed as it scrolls into view ---------- */
  var banner = document.querySelector("[data-banner]");
  if (banner && !reduce) {
    var bTick = false;
    var bUpdate = function () {
      bTick = false;
      var r = banner.getBoundingClientRect(), vh = window.innerHeight;
      var t = clamp((vh - r.top) / (vh * 0.85), 0, 1);
      var max = window.matchMedia("(max-width: 960px)").matches ? 4 : 6;
      banner.style.setProperty("--bi", ((1 - t) * max).toFixed(2) + "%");
      banner.style.setProperty("--br", ((1 - t) * 28).toFixed(1) + "px");
      banner.style.setProperty("--bz", (1.12 - 0.12 * t).toFixed(4));
    };
    window.addEventListener("scroll", function () { if (!bTick) { bTick = true; requestAnimationFrame(bUpdate); } }, { passive: true });
    window.addEventListener("resize", bUpdate);
    bUpdate();
  }

  /* ---------- Reveal on scroll + count-up numbers ---------- */
  var countUp = function (el) {
    var to = parseFloat(el.dataset.count), suffix = el.dataset.suffix || "", t0 = null, dur = 1300;
    var fmt = function (v) { return Math.round(v).toLocaleString("en-CA") + suffix; };
    if (reduce) { el.textContent = fmt(to); return; }
    var step = function (now) {
      if (t0 === null) t0 = now;
      var k = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(to * e);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  var revealEls = Array.prototype.slice.call(document.querySelectorAll("[data-reveal], [data-count]"));
  if ("IntersectionObserver" in window && revealEls.length) {
    document.querySelectorAll("[data-count]").forEach(function (el) { if (!reduce) el.textContent = "0" + (el.dataset.suffix || ""); });
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        rio.unobserve(en.target);
        if (en.target.hasAttribute("data-count")) countUp(en.target);
        else en.target.classList.add("is-in");
      });
    }, { threshold: 0.18, rootMargin: "0px 0px -6% 0px" });
    revealEls.forEach(function (el) { rio.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Video lightbox (YouTube Shorts) ---------- */
  var vbox = document.querySelector(".vbox");
  if (vbox && typeof vbox.showModal === "function") {
    var frame = vbox.querySelector(".vbox-frame");
    document.addEventListener("click", function (ev) {
      var b = ev.target.closest("[data-lightbox]");
      if (!b) return;
      ev.preventDefault();
      frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + b.dataset.lightbox + '?autoplay=1&playsinline=1&rel=0" title="Rempel Removal video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
      vbox.showModal();
      track("video_play", { video_id: b.dataset.lightbox });
    });
    vbox.querySelector(".vbox-close").addEventListener("click", function () { vbox.close(); });
    vbox.addEventListener("click", function (ev) { if (ev.target === vbox) vbox.close(); });
    vbox.addEventListener("close", function () { frame.innerHTML = ""; });
  }

  /* ---------- YouTube: load the player only when someone taps play ---------- */
  document.querySelectorAll("button.yt[data-yt]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (btn.classList.contains("is-playing")) return;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + btn.dataset.yt + "?autoplay=1&playsinline=1&rel=0";
      f.title = btn.getAttribute("aria-label") || "Rempel Removal video";
      f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      f.allowFullscreen = true;
      btn.innerHTML = "";
      btn.appendChild(f);
      btn.classList.add("is-playing");
      track("video_play", { video_id: btn.dataset.yt });
    });
  });

  /* ---------- Job story: swap sticky media as steps scroll past ---------- */
  var story = document.querySelector("[data-story]");
  if (story && "IntersectionObserver" in window) {
    var media = story.querySelectorAll(".story-media > [data-media]");
    var steps = story.querySelectorAll("[data-step]");
    var show = function (key) {
      media.forEach(function (m) { m.classList.toggle("is-on", m.dataset.media === key); });
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) show(e.target.dataset.step); });
    }, { rootMargin: "-45% 0px -45% 0px" });
    steps.forEach(function (s) { io.observe(s); });
    var storyScrub = story.querySelector(".story-media canvas[data-frames]");
    if (storyScrub && !reduce) {
      var sc = new Scrubber(storyScrub);
      var tick = false;
      var u = function () {
        tick = false;
        var r = story.getBoundingClientRect();
        sc.draw(clamp(-r.top / (story.offsetHeight - window.innerHeight), 0, 1));
      };
      window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(u); } }, { passive: true });
      u();
    }
  }

  /* ---------- Before / after sliders ----------
     Drag (or use arrow keys) to compare. The first time a slider scrolls into view,
     the handle sweeps once to show people it moves. */
  var sliders = Array.prototype.slice.call(document.querySelectorAll(".ba"));
  sliders.forEach(function (box) {
    var input = box.querySelector("input[type=range]");
    if (!input) return;
    var set = function (v) { input.value = v; box.style.setProperty("--split", v + "%"); var t = box.querySelector(".tag--before"), u = box.querySelector(".tag--done"); if (t) t.style.opacity = v < 18 ? 0 : 1; if (u) u.style.opacity = v > 82 ? 0 : 1; };
    var touch = function () { box.classList.add("is-touched"); box._touched = true; };
    input.addEventListener("input", function () { touch(); set(parseFloat(input.value)); });
    input.addEventListener("pointerdown", touch);
    set(parseFloat(input.value) || 50);
    box._set = set;
  });
  if (!reduce && "IntersectionObserver" in window) {
    var sweep = function (box) {
      var keys = [[0, 50], [700, 22], [1500, 78], [2200, 50]], t0 = null;
      var ease = function (x) { return x < .5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; };
      var frame = function (now) {
        if (box._touched) return;
        if (t0 === null) t0 = now;
        var t = now - t0, i = 1;
        while (i < keys.length - 1 && t > keys[i][0]) i++;
        var a = keys[i - 1], b = keys[i], k = clamp((t - a[0]) / (b[0] - a[0]), 0, 1);
        box._set(a[1] + (b[1] - a[1]) * ease(k));
        if (t < keys[keys.length - 1][0]) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    };
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && en.target._set && !en.target.closest(".story-media")) { seen.unobserve(en.target); setTimeout(function () { sweep(en.target); }, 300); }
      });
    }, { threshold: 0.6 });
    sliders.forEach(function (b) { seen.observe(b); });
  }

  /* ---------- Our Work filters ---------- */
  var filters = document.querySelector("[data-filters]");
  if (filters) {
    var cards = document.querySelectorAll("[data-service]");
    filters.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      filters.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      var f = b.dataset.filter;
      cards.forEach(function (c) { c.hidden = f !== "all" && c.dataset.service !== f; });
    });
  }

  /* ---------- Quote form: preselect service from ?service= ---------- */
  var sel = document.querySelector("select[name=service]");
  if (sel) {
    var q = new URLSearchParams(location.search).get("service");
    if (q && sel.querySelector('option[value="' + q + '"]')) sel.value = q;
  }

  /* ---------- Conversion events (fire only when Google tags are installed) ---------- */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href^='tel:'], a[href^='sms:']");
    if (!a) return;
    track(a.href.indexOf("sms:") === 0 ? "text_click" : "call_click", { link_url: a.href, page: location.pathname });
  });
  document.querySelectorAll("form[data-track]").forEach(function (f) {
    f.addEventListener("submit", function () { track("generate_lead", { form: f.getAttribute("name") }); });
  });
})();
