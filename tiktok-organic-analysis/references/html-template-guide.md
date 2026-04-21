# HTML Report Template Guide

## Full CSS Design System

```css
:root {
  --bg-primary: #0d0d0d;
  --bg-secondary: #141414;
  --bg-card: #1a1a1a;
  --border: #2a2a2a;
  --border-accent: #3a3a3a;
  --text-primary: #f0ebe3;
  --text-secondary: #9a9080;
  --text-muted: #5a5248;
  --accent-gold: #c9a96e;
  --accent-gold-light: #e8c896;
  --accent-rose: #d4867a;
  --accent-sage: #8aab8a;
  --accent-slate: #7a9aaa;
  --accent-purple: #b8a8d8;
  --gradient-gold: linear-gradient(135deg, #c9a96e, #e8c896);
}
```

## Required Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```
- Headings: `font-family: 'Playfair Display', serif`
- Body: `font-family: 'Inter', sans-serif`

---

## Key Components

### 1. Report Header
```html
<header style="background: linear-gradient(160deg, #0d0d0d 0%, #1a1208 50%, #0d0d0d 100%); border-bottom: 1px solid #2a2a2a; padding: 60px 40px 50px;">
  <div style="max-width: 1200px; margin: 0 auto;">
    <!-- TikTok tag -->
    <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(255,0,80,0.12); border:1px solid rgba(255,0,80,0.25); color:#ff4080; font-size:11px; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; padding:6px 14px; border-radius:20px; margin-bottom:20px;">
      <div style="width:8px;height:8px;background:#ff0050;border-radius:50%;animation:pulse 2s infinite;"></div>
      TikTok Organic Intelligence
    </div>
    <!-- Title -->
    <h1 style="font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:#f0ebe3; line-height:1.15; margin-bottom:12px;">
      [Brand Name]<br><span style="background:linear-gradient(135deg,#c9a96e,#e8c896);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">TikTok Content Analysis</span>
    </h1>
    <!-- Subtitle -->
    <p style="font-size:17px; color:#9a9080; margin-bottom:32px; max-width:600px;">[Description]</p>
    <!-- Meta row -->
    <div style="display:flex; gap:32px; flex-wrap:wrap;">
      <div><span style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#5a5248;font-weight:600;display:block;">Report Date</span><span style="font-size:14px;color:#9a9080;">April 2026</span></div>
      <div><span style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#5a5248;font-weight:600;display:block;">Categories</span><span style="font-size:14px;color:#9a9080;">3 product categories</span></div>
    </div>
  </div>
</header>
```

### 2. Sticky Navigation Bar
```html
<nav style="background:#141414; border-bottom:1px solid #2a2a2a; position:sticky; top:0; z-index:100;">
  <div style="max-width:1200px; margin:0 auto; padding:0 40px; display:flex; overflow-x:auto;">
    <a href="#executive" style="color:#5a5248; text-decoration:none; font-size:13px; font-weight:500; padding:16px 20px; border-bottom:2px solid transparent; white-space:nowrap;">Executive Summary</a>
    <!-- repeat for each section -->
  </div>
</nav>
```

### 3. Stat Card
```html
<div style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:24px; text-align:center;">
  <span style="font-family:'Playfair Display',serif; font-size:32px; font-weight:700; color:#c9a96e; display:block; margin-bottom:4px;">124M+</span>
  <span style="font-size:12px; color:#5a5248; font-weight:500; text-transform:uppercase; letter-spacing:0.08em;">#homedecor views</span>
</div>
```

### 4. Category Hero Block
```html
<!-- For each category, use matching gradient + border -->
<!-- Rattan/warm: #1a1208 bg, #3a2a08 border -->
<!-- Tableware/purple: #120e1a bg, #2e1e3a border -->
<!-- Linen/sage: #0e1510 bg, #1e3022 border -->
<div style="border-radius:16px; padding:36px; background:linear-gradient(135deg,#1a1208,#201808); border:1px solid #3a2a08; position:relative; overflow:hidden; margin-bottom:32px;">
  <span style="font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#c9a96e;margin-bottom:10px;display:block;">🌿 RATTAN & STORAGE</span>
  <h3 style="font-family:'Playfair Display',serif; font-size:26px; font-weight:700; color:#f0ebe3; margin-bottom:8px;">The Organisation Content Goldmine</h3>
  <p style="font-size:14px; color:#9a9080; max-width:500px;">[Category framing sentence]</p>
  <!-- Decorative emoji -->
  <div style="position:absolute;right:32px;top:50%;transform:translateY(-50%);font-size:80px;opacity:0.12;">🪨</div>
</div>
```

### 5. Hook Card (quote block)
```html
<div style="background:rgba(201,169,110,0.05); border:1px solid rgba(201,169,110,0.15); border-left:3px solid #c9a96e; border-radius:8px; padding:16px 20px; margin-bottom:10px; font-size:15px; color:#f0ebe3; font-style:italic; line-height:1.5;">
  "Transform your messy closet in 60 seconds with this one piece"
</div>
```
For purple category: `rgba(184,168,216,...)` / `#b8a8d8`
For sage category: `rgba(138,171,138,...)` / `#8aab8a`

### 6. Video Card (MUST be an `<a>` tag)
```html
<a href="https://www.tiktok.com/@creator/video/123" target="_blank" rel="noopener"
   style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; overflow:hidden; text-decoration:none; color:inherit; display:block; transition:transform 0.2s, border-color 0.2s;">
  <!-- Thumbnail placeholder -->
  <div style="background:linear-gradient(135deg,#1e1808,#2a2010); height:120px; display:flex; align-items:center; justify-content:center; font-size:28px;">🌿</div>
  <!-- Meta -->
  <div style="padding:14px;">
    <div style="font-size:11px; color:#c9a96e; font-weight:600; margin-bottom:4px;">@creatorhandle</div>
    <div style="font-size:13px; color:#f0ebe3; margin-bottom:10px; line-height:1.4;">Video caption here</div>
    <div style="display:flex; gap:12px; margin-bottom:8px;">
      <span style="font-size:11px; color:#5a5248;">❤️ <strong style="color:#9a9080;">1.7K</strong></span>
      <span style="font-size:11px; color:#5a5248;">🔖 <strong style="color:#9a9080;">419</strong></span>
    </div>
    <div style="font-size:11px; color:#ff4080; font-weight:600; opacity:0.7;">▶ Watch on TikTok ↗</div>
  </div>
</a>
```
Place 6 cards in a `display:grid; grid-template-columns:repeat(3,1fr); gap:16px;` wrapper.

### 7. Creator Table
```html
<table style="width:100%; border-collapse:collapse;">
  <thead>
    <tr>
      <th style="text-align:left; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#5a5248; padding:10px 14px; border-bottom:1px solid #2a2a2a;">Handle</th>
      <th ...>Content Type</th>
      <th ...>UK?</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:12px 14px; border-bottom:1px solid rgba(42,42,42,0.5); font-size:13px; color:#c9a96e; font-weight:600; font-family:monospace;">@ourbeigebungalow</td>
      <td style="padding:12px 14px; border-bottom:1px solid rgba(42,42,42,0.5); font-size:13px; color:#9a9080;">Beige/neutral home styling</td>
      <td style="padding:12px 14px; border-bottom:1px solid rgba(42,42,42,0.5); font-size:13px; color:#9a9080;">✅</td>
    </tr>
  </tbody>
</table>
```

### 8. Strategic Insight Callout
```html
<div style="background:rgba(201,169,110,0.06); border:1px solid rgba(201,169,110,0.2); border-radius:10px; padding:20px 24px; display:flex; gap:14px; align-items:flex-start;">
  <span style="font-size:20px; flex-shrink:0; margin-top:2px;">🎯</span>
  <p style="font-size:14px; color:#9a9080; line-height:1.6;"><strong style="color:#f0ebe3;">Strategic Opportunity:</strong> [Insight text]</p>
</div>
```

### 9. Opportunity Card (Playbook)
```html
<div style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:28px; margin-bottom:16px; position:relative;">
  <div style="position:absolute;top:24px;right:24px; font-family:'Playfair Display',serif; font-size:48px; font-weight:700; color:rgba(201,169,110,0.08); line-height:1;">01</div>
  <span style="font-size:10px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#c9a96e; margin-bottom:8px; display:block;">RATTAN — IMMEDIATE</span>
  <div style="font-size:17px; font-weight:600; color:#f0ebe3; margin-bottom:8px;">Content idea title</div>
  <p style="font-size:14px; color:#9a9080; margin-bottom:16px; line-height:1.6;">[Description and production notes]</p>
  <div style="display:flex; gap:16px; flex-wrap:wrap; font-size:12px; color:#5a5248;">
    <span>⏱️ <strong style="color:#9a9080;">1 hour</strong></span>
    <span>🎵 <strong style="color:#9a9080;">Lo-fi</strong></span>
    <span>📍 <strong style="color:#9a9080;">#homedecor</strong></span>
  </div>
</div>
```

### 10. 90-Day Roadmap Table
```html
<div style="background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; overflow:hidden;">
  <!-- Header row -->
  <div style="display:grid; grid-template-columns:200px 1fr 180px;">
    <div style="padding:12px 20px; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#5a5248; background:#141414; border-right:1px solid #2a2a2a;">Phase</div>
    <div style="... border-right:...">Focus</div>
    <div style="...">Target</div>
  </div>
  <!-- Data rows -->
  <div style="display:grid; grid-template-columns:200px 1fr 180px; border-top:1px solid #2a2a2a;">
    <div style="padding:18px 20px; border-right:1px solid #2a2a2a;"><strong style="color:#c9a96e;">Month 1</strong><br><span style="font-size:12px;color:#5a5248;">Foundation</span></div>
    <div style="padding:18px 20px; font-size:13px; color:#9a9080; border-right:1px solid #2a2a2a;">[Focus description]</div>
    <div style="padding:18px 20px; font-size:13px; color:#9a9080;"><strong style="color:#f0ebe3;">1,000 followers</strong><br><span style="font-size:12px;color:#5a5248;">10–15 posts</span></div>
  </div>
</div>
```

### 11. Required `<style>` block (add to `<head>`)
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; background: #0d0d0d; color: #f0ebe3; line-height: 1.6; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
.section { padding: 64px 0; border-bottom: 1px solid #2a2a2a; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }
.video-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.divider { height: 1px; background: #2a2a2a; margin: 32px 0; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
@media (max-width: 768px) { .two-col, .three-col, .video-grid, .stat-row { grid-template-columns: 1fr; } .container { padding: 0 20px; } }
```

---

## Section ID Anchors

Each section needs an `id` for the nav bar:
- `id="executive"` — Executive Summary
- `id="[category-slug]"` — one per category (e.g. `id="rattan"`, `id="tableware"`)
- `id="crosscat"` — Cross-Category Patterns
- `id="playbook"` — Brand Playbook

---

## Footer
```html
<footer style="background:#141414; border-top:1px solid #2a2a2a; padding:40px; text-align:center;">
  <div style="font-family:'Playfair Display',serif; font-size:22px; color:#c9a96e; margin-bottom:8px;">[Brand Name]</div>
  <p style="font-size:13px; color:#5a5248;">TikTok Organic Content Analysis · [Date] · Prepared by Launch With Us · Confidential</p>
</footer>
```
