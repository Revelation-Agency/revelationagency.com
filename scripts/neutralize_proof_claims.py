"""Neutralize unverified numeric outcome claims on Trust Energy and NMS
case-study pages, per artifacts/portfolio-proof-migration.csv.

- Every replacement is scoped by an exact string match. If the string is not
  found (page already neutralized, or copy has evolved), the file is left
  untouched.
- We swap the three quarantined metric tiles for factual, delivery-focused
  copy. No new number is introduced.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


# Trust Energy: whole outcomes block gets rewritten.
TRUST_ENERGY_OLD = """  <div class="cs-outcomes__inner">
    <h2>Four years at half-industry CPL.</h2>
    <div class="cs-outcomes__grid">
      <div class="cs-metric">
        <div class="cs-metric__value">$25</div>
        <div class="cs-metric__label">Cost per lead vs. $40-$50 industry CPL</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">1:4</div>
        <div class="cs-metric__label">Lead-to-appointment conversion ratio</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">4yr</div>
        <div class="cs-metric__label">Continuous full-stack engagement</div>
      </div>
    </div>
  </div>"""

TRUST_ENERGY_NEW = """  <div class="cs-outcomes__inner">
    <h2>Full-stack engagement, over multiple years.</h2>
    <p style="max-width:720px;margin:8px 0 32px;font-size:16px;line-height:1.7;color:#ccc;">Revelation Agency owned brand, website, video, and marketing operations for Trust Energy across a multi-year continuous engagement. Specific outcome numbers (CPL, conversion, ROAS) are held pending a written proof record from the client.</p>
    <div class="cs-outcomes__grid">
      <div class="cs-metric">
        <div class="cs-metric__value">Full-stack</div>
        <div class="cs-metric__label">Brand + website + video + marketing operations delivered</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Multi-year</div>
        <div class="cs-metric__label">Continuous engagement, not a one-off project</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">In-Production</div>
        <div class="cs-metric__label">Deliverables shipped and running for the Trust Energy team</div>
      </div>
    </div>
  </div>"""


# NMS: outcomes block also rewritten. "12 active CRM automations" replaced
# with a factual "CRM + sales automation system in production" claim; a
# real count will only be published if a screenshot proof is attached later.
NMS_OLD = """      <div class="cs-metric">
        <div class="cs-metric__value">$50</div>
        <div class="cs-metric__label">Average cost per lead on paid social</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">25%</div>
        <div class="cs-metric__label">Lead-to-appointment conversion rate</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">5x</div>
        <div class="cs-metric__label">Return on ad spend (ROAS)</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">12</div>
        <div class="cs-metric__label">Active CRM &amp; sales automations running 24/7</div>
      </div>"""

NMS_NEW = """      <div class="cs-metric">
        <div class="cs-metric__value">Full-stack</div>
        <div class="cs-metric__label">Brand, website, video, social, SEO, and marketing ops delivered</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">In-Production</div>
        <div class="cs-metric__label">Paid social + CRM + sales-automation system in operation</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Multi-year</div>
        <div class="cs-metric__label">Continuous engagement across multiple disciplines</div>
      </div>
      <div class="cs-metric">
        <div class="cs-metric__value">Owned</div>
        <div class="cs-metric__label">Marketing operating system built and operated by Revelation</div>
      </div>"""


REPLACEMENTS = [
    ("portfolio/case-studies/trust-energy.html", TRUST_ENERGY_OLD, TRUST_ENERGY_NEW),
    ("portfolio/case-studies/net-metering-systems.html", NMS_OLD, NMS_NEW),
]


def main() -> int:
    changed = 0
    for path, old, new in REPLACEMENTS:
        with open(path, "r", encoding="utf-8") as f:
            data = f.read()
        if old in data:
            data = data.replace(old, new, 1)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(data)
            print(f"[neutralized] {path}")
            changed += 1
        else:
            print(f"[skip] {path} — original tile block not found; already neutralized or copy evolved.")
    print(f"\nchanged {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
