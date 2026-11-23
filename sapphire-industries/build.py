"""Generates industry/index.html and one internal page per industry. Run: python build.py"""
import os

INDUSTRIES = [
    ("government", "Government",
     "Public-sector bodies need secure, citizen-centric digital services. SCS delivers e-governance, social protection, data platforms and cash-transfer systems that improve transparency and reach.",
     ["E-governance & citizen portals", "Social protection & cash transfer systems", "Data warehousing & analytics", "Information security & compliance"],
     [("Social Protection Strategy Unit", "Health and Nutrition Conditional Cash Transfer Program")]),
    ("finance-and-banking", "Finance and Banking",
     "From core banking to compliance, SCS helps banks and financial institutions modernise operations, reduce risk and improve customer experience.",
     ["Core & digital banking", "Regulatory & compliance solutions", "Risk, fraud and AML analytics", "Payments & integration"],
     [("Formerly Saudi Pak Commercial Bank", "Silk Bank Limited"),
      ("JS Bank Limited", "JS Bank Limited Reduces Costs by 50% and Meets Compliance Obligations")]),
    ("manufacturing", "Manufacturing",
     "SCS connects plants, supply chains and finance with ERP, MRP and analytics so manufacturers plan better and waste less.",
     ["ERP & supply-chain management", "Plant maintenance", "Production planning", "Industrial reporting & analytics"],
     [("Maximizing Profits, Minimizing Costs", "End-to-End Integrated Solution for United Energy Pakistan")]),
    ("media", "Media",
     "Media houses depend on fast content workflows and reliable infrastructure. SCS provides systems for asset management, billing and audience analytics.",
     ["Digital asset management", "Subscriber billing", "Audience analytics", "Cloud & streaming infrastructure"], []),
    ("higher-education", "Higher Education",
     "Universities and institutes use SCS platforms for admissions, student records, learning delivery and institutional reporting.",
     ["Student information systems", "Learning management", "Admissions & fee management", "Institutional analytics"], []),
    ("healthcare", "Healthcare",
     "SCS builds secure health information systems that connect patient records, hospital operations and public-health programmes.",
     ["Hospital information systems", "Electronic health records", "Health programme monitoring", "Data security & privacy"],
     [("Social Protection Strategy Unit", "Health and Nutrition Conditional Cash Transfer Program")]),
    ("energy", "Energy",
     "Utilities and energy companies rely on SCS for asset management, billing, ERP and end-to-end integrated operations.",
     ["Asset & work management", "Billing & revenue systems", "ERP for energy", "Spatial / GIS data management"],
     [("Maximizing Profits, Minimizing Costs", "End-to-End Integrated Solution for United Energy Pakistan")]),
]

INTRO = ("At Sapphire Consulting Services (SCS), we pride ourselves on delivering industry-specific solutions through our "
         "dedicated teams of experts. Our industrial divisions are composed of highly skilled functional and technical "
         "consultants, each specializing in different sectors. These teams are adept at understanding the unique challenges "
         "and nuances of their respective industries. Presently, SCS concentrates on providing technology solutions to a "
         "variety of key industries, leveraging our deep domain expertise to offer tailored, innovative solutions that drive "
         "success and efficiency in each sector.")

NAV = ["Information Security Policy", "Company", "Industries", "Technology", "Services", "Careers", "Blog", "Contact"]

FOOT = """<footer><div class="wrap cols">
<div><div class="logo" style="color:#fff">Sapphire<span>.</span></div><p>Sapphire Consulting Services (Pvt.) Limited - SCS is an international systems consulting company providing a broad portfolio of technology and business solutions to help its worldwide clients improve their business performance.</p></div>
<div><h5>Contact Us</h5><p>1609 Hidden Springs Path<br>Round Rock, TX 78665</p><p>+1 (201) 255 2790</p><p>info@sapphire.co</p></div>
<div><h5>Discover</h5><ul>""" + "".join(f"<li>{n}</li>" for n in NAV) + """</ul></div>
<div><h5>Get In Touch</h5><p>Get Business news, tip and solutions to your problems from our experts.</p><input placeholder="Enter email address"><button>Subscribe Now</button></div>
</div><div class="copy">&copy; 2026 Sapphire Consulting Services (Pvt) Ltd. All rights reserved.</div></footer></body></html>"""


def head(title, crumb):
    nav = "".join(
        '<a href="{R}industry/"%s>%s</a>' % (' class="active"' if n == "Industries" else "", n) if n == "Industries"
        else '<a href="#">%s</a>' % n
        for n in NAV)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Sapphire</title><link rel="stylesheet" href="{{R}}style.css"></head><body>
<div class="topbar"><div class="wrap"><span>info@sapphire.co</span><span>in &nbsp; f &nbsp; t</span></div></div>
<header class="main"><div class="wrap"><a class="logo" href="{{R}}industry/">Sapphire<span>.</span></a><nav>{nav}</nav></div></header>
<div class="banner"><div class="wrap"><h1>{title}</h1><small>{crumb}</small></div></div><div class="wrap layout"><main>"""


def side(cur=None):
    li = "".join(
        '<li><a href="{R}industry/%s.html"%s>%s</a></li>' % (s, ' class="on"' if s == cur else "", n)
        for s, n, _, _, _ in INDUSTRIES)
    return f"""</main><aside><div class="box"><hr><ul>{li}</ul></div>
<div class="box"><h4>Need Help?</h4><hr><p>+1 (201) 255 2790<br>info@sapphire.co</p></div>
<div class="box"><h4>Connect</h4><hr><div class="social"><span>t</span><span>f</span><span>in</span></div></div></aside></div>"""


def card(title, desc, slug):
    img = "https://placehold.co/600x400/cfd6e4/14206b?text=" + title.replace(" ", "+")
    return (f'<div class="card"><img alt="" src="{img}"><h3>{title}</h3><p>{desc}</p>'
            f'<a class="more" href="{{R}}industry/{slug}.html">Read More</a></div>')


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html.replace("{R}", "../"))


cases, seen = [], set()
for slug, _, _, _, cs in INDUSTRIES:
    for t, d in cs:
        if (t, d) not in seen:
            seen.add((t, d))
            cases.append((t, d, slug))

write("industry/index.html",
      head("Industries", "Home / Industries")
      + f'<h2 class="t">Industries</h2><p>{INTRO}</p><div class="cards">'
      + "".join(card(t, d, s) for t, d, s in cases[:4])
      + '</div><div class="more-cases">More Case Studies</div>' + side() + FOOT)

for slug, name, desc, points, cs in INDUSTRIES:
    hero = "https://placehold.co/900x300/cfd6e4/14206b?text=" + name.replace(" ", "+")
    body = (f'<h2 class="t">{name}</h2><img class="hero" alt="" src="{hero}"><p>{desc}</p>'
            '<h2 class="t" style="margin-top:18px">What we deliver</h2><ul class="list">'
            + "".join(f"<li>{p}</li>" for p in points) + "</ul>")
    if cs:
        body += ('<h2 class="t" style="margin-top:18px">Case studies</h2><div class="cards">'
                 + "".join(card(t, d, slug) for t, d in cs) + "</div>")
    write(f"industry/{slug}.html",
          head(name, f'Home / <a href="{{R}}industry/">Industries</a> / {name}') + body + side(slug) + FOOT)
