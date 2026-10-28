// Screenshot every .slide in carousel.html to out/slide-N.png and report overflow.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = __dirname;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1400 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(dir, 'carousel.html'));
  await page.evaluate(() => document.fonts.ready);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(dir, 'out', `slide-${i + 1}.png`) });
  }
  // report elements that spill past the slide or overlap the handle
  const issues = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.slide').forEach((s, i) => {
      const r = s.getBoundingClientRect();
      s.querySelectorAll('.cards,.steps,.fact-list,.cta-list,.note,.final,.stairs,.head').forEach(el => {
        const b = el.getBoundingClientRect();
        if (b.bottom > r.bottom - 80 || b.right > r.right) out.push(`slide ${i + 1}: ${el.className} bottom=${Math.round(b.bottom - r.top)}`);
      });
      const head = s.querySelector('.head').getBoundingClientRect();
      const body = s.querySelector('.cards,.steps,.fact-list,.cta-list');
      if (body && body.getBoundingClientRect().top < head.bottom + 20) out.push(`slide ${i + 1}: body overlaps head (${Math.round(head.bottom - r.top)})`);
      const steps = s.querySelector('.steps'), note = s.querySelector('.note');
      if (steps && note && steps.getBoundingClientRect().bottom > note.getBoundingClientRect().top - 20) out.push(`slide ${i + 1}: steps overlap note`);
      const cl = s.querySelector('.cta-list'), fin = s.querySelector('.final');
      if (cl && fin && cl.getBoundingClientRect().bottom > fin.getBoundingClientRect().top - 20) out.push(`slide ${i + 1}: cta overlaps final`);
    });
    return out;
  });
  console.log(issues.length ? issues.join('\n') : 'no layout issues');
  await browser.close();
})();
