#!/usr/bin/env node
/**
 * Magritte Collection Scraper
 * Uses Puppeteer (already installed at ~/.npm/_npx/.../puppeteer-mcp-claude)
 * to navigate to a Magritte collection URL, wait for content to render,
 * scroll to trigger lazy loading, and extract all creative image URLs.
 *
 * Usage:
 *   node magritte_scrape.js <collection_url> [max_scrolls]
 * Outputs: JSON array of { url, alt, width, height } image objects
 */

const PUPPETEER_PATH = '/Users/yoannatafrova/.npm/_npx/18b9ac6ecf823310/node_modules/puppeteer';

const puppeteer = require(PUPPETEER_PATH);

async function scrape(url, maxScrolls = 3) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900 });
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    console.error(`Navigating to ${url}...`);
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

    // Wait a beat for client-side React to render
    await new Promise(r => setTimeout(r, 3000));

    // Scroll down to trigger lazy loading
    for (let i = 0; i < maxScrolls; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight * 2));
      await new Promise(r => setTimeout(r, 1500));
    }

    // Extract all images that look like ad creatives (not icons/logos)
    const images = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('img'));
      return imgs
        .map(img => ({
          url: img.src || img.currentSrc,
          alt: img.alt || '',
          width: img.naturalWidth || img.width,
          height: img.naturalHeight || img.height,
        }))
        .filter(i => i.url && i.url.startsWith('http'));
    });

    // Also grab any <video> sources
    const videos = await page.evaluate(() => {
      const vids = Array.from(document.querySelectorAll('video'));
      return vids
        .map(v => ({
          url: v.src || (v.querySelector('source') && v.querySelector('source').src),
          poster: v.poster || '',
          type: 'video',
        }))
        .filter(v => v.url && v.url.startsWith('http'));
    });

    // Also grab background-image URLs from inline styles (Magritte often uses these for thumbnails)
    const bgImages = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('[style*="background-image"]'));
      return els
        .map(el => {
          const m = el.style.backgroundImage.match(/url\(["']?(.+?)["']?\)/);
          return m ? { url: m[1], type: 'bg-image' } : null;
        })
        .filter(Boolean);
    });

    const results = {
      page_url: url,
      scraped_at: new Date().toISOString(),
      image_count: images.length,
      video_count: videos.length,
      bg_image_count: bgImages.length,
      images,
      videos,
      bg_images: bgImages,
    };

    console.log(JSON.stringify(results, null, 2));
  } catch (err) {
    console.error('Scrape error:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

const url = process.argv[2];
const maxScrolls = parseInt(process.argv[3] || '3', 10);

if (!url) {
  console.error('Usage: node magritte_scrape.js <collection_url> [max_scrolls]');
  process.exit(1);
}

scrape(url, maxScrolls);
