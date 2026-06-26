#!/usr/bin/env python3
"""
Daily NEET article generator for neetsuccess.com
Generates a complete HTML article using Claude API and saves it to the repo.
Run via GitHub Actions on a daily schedule.
"""

import anthropic
import os
import sys
from datetime import datetime
import re

# 30+ topic rotation â cycles through by day of year
TOPICS = [
    {"slug": "neet-biology-cell-division", "title": "Cell Division for NEET: Mitosis vs Meiosis â Everything That Comes in the Exam", "subject": "Biology"},
    {"slug": "neet-physics-mechanics-guide", "title": "NEET Physics Mechanics: 15 Concepts You Cannot Afford to Miss", "subject": "Physics"},
    {"slug": "neet-chemistry-organic-basics", "title": "Organic Chemistry for NEET: The Building Blocks Every Aspirant Must Know", "subject": "Chemistry"},
    {"slug": "neet-genetics-mendelian-laws", "title": "Mendelian Genetics for NEET: Master the Laws, Ace the Questions", "subject": "Biology"},
    {"slug": "neet-physics-optics-guide", "title": "Ray Optics for NEET: Complete Guide to Lenses, Mirrors and Light", "subject": "Physics"},
    {"slug": "neet-chemistry-equilibrium", "title": "Chemical Equilibrium for NEET: Le Chatelier's Principle and Beyond", "subject": "Chemistry"},
    {"slug": "neet-ecology-environment", "title": "Ecology for NEET: High-Yield Topics That Appear Every Year", "subject": "Biology"},
    {"slug": "neet-physics-electrostatics", "title": "Electrostatics for NEET: From Coulomb's Law to Capacitors", "subject": "Physics"},
    {"slug": "neet-chemistry-electrochemistry", "title": "Electrochemistry for NEET: Cells, EMF and How to Score Full Marks", "subject": "Chemistry"},
    {"slug": "neet-human-physiology-overview", "title": "Human Physiology for NEET: The 8 Systems You Must Master", "subject": "Biology"},
    {"slug": "neet-physics-thermodynamics", "title": "Thermodynamics for NEET: Laws, Processes and Exam Shortcuts", "subject": "Physics"},
    {"slug": "neet-chemistry-p-block-elements", "title": "P-Block Elements for NEET: Patterns, Properties and Predictions", "subject": "Chemistry"},
    {"slug": "neet-plant-physiology-guide", "title": "Plant Physiology for NEET: Photosynthesis and Respiration Deep Dive", "subject": "Biology"},
    {"slug": "neet-physics-modern-physics", "title": "Modern Physics for NEET: Photoelectric Effect to Nuclear Physics", "subject": "Physics"},
    {"slug": "neet-chemistry-d-block-elements", "title": "D-Block Elements for NEET: Transition Metals Made Simple", "subject": "Chemistry"},
    {"slug": "neet-reproduction-flowering-plants", "title": "Reproduction in Flowering Plants: Complete NEET Chapter Guide", "subject": "Biology"},
    {"slug": "neet-physics-current-electricity", "title": "Current Electricity for NEET: Circuits, Resistance and Kirchhoff Laws", "subject": "Physics"},
    {"slug": "neet-chemistry-coordination-compounds", "title": "Coordination Compounds for NEET: IUPAC, Isomerism and Stability", "subject": "Chemistry"},
    {"slug": "neet-biotechnology-applications", "title": "Biotechnology for NEET: Recombinant DNA and Real Exam Questions", "subject": "Biology"},
    {"slug": "neet-physics-waves-sound", "title": "Waves and Sound for NEET: Doppler Effect and Standing Waves", "subject": "Physics"},
    {"slug": "neet-chemistry-biomolecules", "title": "Biomolecules for NEET: Proteins, Carbs and Nucleic Acids Simplified", "subject": "Chemistry"},
    {"slug": "neet-evolution-strategies", "title": "Evolution for NEET: Darwin, Fossils and the Exam Pattern Explained", "subject": "Biology"},
    {"slug": "neet-physics-magnetic-effects", "title": "Magnetic Effects for NEET: Moving Charges, Fields and Forces", "subject": "Physics"},
    {"slug": "neet-chemistry-hydrocarbons-guide", "title": "Hydrocarbons for NEET: Alkanes, Alkenes, Alkynes and Arenes", "subject": "Chemistry"},
    {"slug": "neet-animal-kingdom-classification", "title": "Animal Kingdom for NEET: Classification, Phyla and NCERT Questions", "subject": "Biology"},
    {"slug": "neet-physics-rotational-motion", "title": "Rotational Motion for NEET: Torque, Angular Momentum and MOI", "subject": "Physics"},
    {"slug": "neet-chemistry-chemical-kinetics", "title": "Chemical Kinetics for NEET: Rate Laws, Activation Energy, Numericals", "subject": "Chemistry"},
    {"slug": "neet-human-reproduction-guide", "title": "Human Reproduction for NEET: Complete Chapter Guide and Questions", "subject": "Biology"},
    {"slug": "neet-physics-fluid-mechanics", "title": "Fluid Mechanics for NEET: Bernoulli, Viscosity and Surface Tension", "subject": "Physics"},
    {"slug": "neet-revision-strategy-guide", "title": "NEET Revision Strategy: The 48-Hour Pre-Exam Checklist That Works", "subject": "Strategy"},
    {"slug": "neet-mock-test-analysis", "title": "How to Analyse NEET Mock Tests to Jump 80â100 Marks", "subject": "Strategy"},
    {"slug": "neet-chemistry-solid-state", "title": "Solid State Chemistry for NEET: Crystal Systems, Defects and PYQs", "subject": "Chemistry"},
    {"slug": "neet-biology-kingdoms-overview", "title": "Five Kingdoms Classification for NEET: Whittaker's System Explained", "subject": "Biology"},
    {"slug": "neet-physics-semiconductors", "title": "Semiconductors for NEET: Diodes, Transistors and Logic Gates", "subject": "Physics"},
    {"slug": "neet-dropper-strategy-2027", "title": "NEET Dropper Strategy 2027: How to Use Your Extra Year to Score 650+", "subject": "Strategy"},
]


def get_today_topic():
    """Pick topic based on day of year â ensures rotation without repeats in a month."""
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def generate_article_html(topic: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""Write a complete, standalone HTML article page for neetsuccess.com.

Topic: {topic['title']}
Subject tag: {topic['subject']}
Filename slug: {topic['slug']}
Date: {today}

Use EXACTLY this HTML structure (fill in all [PLACEHOLDERK]):

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{topic['title']} | NEETSuccess</title>
  <meta name="description" content="[Write a compelling 140-155 char meta description for NEET students]">
  <link rel="canonical" href="https://neetsuccess.com/{topic['slug']}.html">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>ð¯</text></svg>">
  <style>
    .article-hero {{ background: linear-gradient(135deg, #0C1B33 0%, #1A2F52 100%); padding: 64px 0 48px; }}
    .article-hero h1 {{ color: #fff; font-size: clamp(1.6rem, 3.5vw, 2.4rem); line-height: 1.25; margin-bottom: 16px; }}
    .article-meta {{ color: rgba(255,255,255,0.55); font-size: 0.9rem; }}
    .article-meta span {{ margin-right: 20px; }}
    .article-body {{ max-width: 780px; margin: 0 auto; padding: 56px 24px; }}
    .article-body h2 {{ font-size: 1.4rem; font-weight: 700; color: #0C1B33; margin: 40px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #E8E9ED; }}
    .article-body h3 {{ font-size: 1.1rem; font-weight: 600; color: #1A2F52; margin: 28px 0 10px; }}
    .article-body p {{ color: #3a4257; line-height: 1.8; margin-bottom: 16px; font-size: 1.02rem; }}
    .article-body ul, .article-body ol {{ padding-left: 24px; margin-bottom: 20px; }}
    .article-body li {{ color: #3a4257; line-height: 1.8; margin-bottom: 6px; font-size: 1rem; }}
    .highlight-box {{ background: #FFF6E0; border-left: 4px solid #E8A020; padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 24px 0; }}
    .highlight-box strong {{ color: #b8860b; display: block; margin-bottom: 6px; }}
    .highlight-box p {{ margin: 0; color: #5a4a00; font-size: 0.95rem; }}
    .cta-box {{ background: linear-gradient(135deg, #0C1B33, #1A2F52); color: #fff; padding: 32px; border-radius: 12px; margin: 40px 0; text-align: center; }}
    .cta-box h3 {{ color: #E8A020; margin-bottom: 10px; font-size: 1.1rem; }}
    .cta-box p {{ color: rgba(255,255,255,0.8); margin-bottom: 20px; font-size: 0.95rem; }}
    .cta-box a {{ display: inline-block; background: #E8A020; color: #0C1B33; padding: 12px 28px; border-radius: 8px; font-weight: 700; text-decoration: none; }}
    .article-tag-hero {{ display: inline-block; background: rgba(232,160,32,0.15); color: #E8A020; border: 1px solid rgba(232,160,32,0.3); padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 20px; }}
  </style>
</head>
<body>

  <nav class="nav">
    <div class="nav-inner">
      <a href="/" class="logo">NEET<span>Success</span></a>
      <ul class="nav-links">
        <li><a href="/strategy.html">Strategy</a></li>
        <li><a href="/motivation.html">Mindset</a></li>
        <li><a href="/best-neet-coaching-2025.html">Best Coaching</a></li>
        <li><a href="/resources.html">Resources</a></li>
      </ul>
    </div>
  </nav>

  <section class="article-hero">
    <div class="container">
      <div class="article-tag-hero">{topic['subject']} Â· NEET Guide</div>
      <h1>{topic['title']}</h1>
      <div class="article-meta">
        <span>ð {today}</span>
        <span>Â·</span>
        <span>â± [X] min read</span>
        <span>Â·</span>
        <span>ð¯ NEET {topic['subject']}</span>
      </div>
    </div>
  </section>

  <div class="article-body">
    [WRITE 900-1200 WORDS OF BODY CONTENT HERE â genuine, exam-specific, NCERT-grounded]

    Structure required:
    1. Opening hook paragraph â what's at stake for NEET students with this topic
    2. 3-4 H2 sections covering the topic thoroughly with specific chapter references, common exam patterns, and actual strategies
    3. At least 1 highlight-box div with a key tip or common mistake students make
    4. 1 cta-box div linking to /best-neet-coaching-2025.html â mention how Padhle's AIM720 mentors track weak chapters in this subject specifically
    5. Closing paragraph with a practical next-step for the student

    Rules:
    - Reference specific NCERT chapters by number/name where relevant
    - Mention actual question counts or marks weightage where known
    - No filler sentences â every sentence should give the student something useful
    - Write as if a NEET topper is explaining to a struggling student
  </div>

  <footer class="footer">
    <div class="container">
      <div class="footer-inner">
        <div class="footer-brand">
          <a href="/" class="logo">NEET<svan>Success</span></a>
          <p>An independent resource for NEET aspirants. Not affiliated with any coaching institute.</p>
          <p class="footer-highlight">After extensive research, <strong>Padhle's AIM720 batch is the #1 NEET coaching for 2026</strong> â personalised live mentorship, 2-way classes, and emotional support at a fair price.</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p>Â© 2026 NEETSuccess.com Â· Independent student resource</p>
      </div>
    </div>
  </footer>

</body>
</html>

Return ONLY the complete HTML. No explanation, no markdown fences, no commentary."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens<4096,
        messages=[{"role": "user", "content": prompt}]
    )

    html = message.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the output
    if html.startswith("```html"):
        html = html[7:]
    elif html.startswith("```"):
        html = html[3:]
    if html.endswith("```"):
        html = html[:-3]

    return html.strip()


def update_sitemap(slug: str, today_str: str):
    """Append the new article URL to sitemap.xml if not already present."""
    path = "sitemap.xml"
    if not os.path.exists(path):
        print("sitemap.xml not found, skipping update.")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if f"/{slug}.html" in content:
        print(f"sitemap.xml already contains {slug}, skipping.")
        return

    entry = f"""  <url>
    <loc>https://neetsuccess.com/{slug}.html</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.75</priority>
  </url>"""

    content = content.replace("</urlset>", f"{entry}\n</urlset>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"â sitemap.xml updated with {slug}")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTROPOIC_API_KEY environment variable not set.")
        sys.exit(1)

    topic = get_today_topic()
    filename = f"{topic['slug']}.html"
    today_str = datetime.now().strftime("%Y-%m-%d")

    print(f"ð Topic: {topic['title']}")
    print(f"ð Output: {filename}")

    # Don't overwrite an existing article
    if os.path.exists(filename):
        print(f"â£ï¸  {filename} already exists â skipping to avoid overwrite.")
        sys.exit(0)

    print("ð¤ Calling Claude API...")
    html = generate_article_html(topic)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"â Saved {filename} ({len(html):,d} bytes)")

    update_sitemap(topic["slug"], today_str)
    print("ð Done!")


if __name__ == "__main__":
    main()
