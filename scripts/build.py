# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
ASSETS = BASE / "assets"

COMPANIES = [
    ("MAIF", 5, 4, 5, 4, 4, 5),
    ("probabl.ai", 4, 5, 4, 4, 5, 5),
    ("Mistral AI", 4, 5, 5, 3, 5, 3),
    ("Linagora", 3, 3, 4, 4, 4, 5),
    ("OVHcloud", 3, 2, 4, 3, 4, 4),
    ("NEXTON", 3, 5, 3, 3, 4, 5),
]


def load_repos():
    repos = []
    for p in DATA.glob("*.json"):
        try:
            repo = json.loads(p.read_text(encoding="utf-8"))
            if not repo.get("display", True):
                continue
            image_path = repo.get("image", "")
            if image_path:
                local_img_path = BASE / image_path.lstrip("/")
                if not local_img_path.is_file():
                    print(
                        f"Warning: Image file missing for '{repo.get('slug', p.name)}': {local_img_path}",
                        file=sys.stderr,
                    )
                repo["image"] = image_path.lstrip("/")
            repos.append(repo)
        except Exception as e:
            print(f"Error reading {p.name}: {e}", file=sys.stderr)
    return sorted(repos, key=lambda x: (not x.get("featured", False), -x.get("order", 0), x.get("slug", "")))


def generate_repo_html(repo, lang, relative_prefix="./"):
    tags_key = f"tags_{lang}"
    name_key = f"name_{lang}"
    tagline_key = f"tagline_{lang}"
    desc_key = f"description_{lang}"
    tags_html = "".join(
        f'<span class="inline-flex items-center rounded-full bg-white border border-gray-200 px-3 py-1 text-xs font-semibold text-gray-500 shadow-none">{tag}</span>'
        for tag in repo.get(tags_key, [])
    )
    view_text = "View repository" if lang == "en" else "Voir le dépôt"
    image_src = f"{relative_prefix}{repo.get('image', '')}"
    return f"""
        <article class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center border-t border-gray-200 pt-12 lg:pt-24 mt-12 mb-12 lg:mb-24 last:mb-0">
            <a href="{repo.get('repo_url', '#')}" class="w-full bg-[#f5f5f7] rounded-2xl overflow-hidden shadow-none flex items-center justify-center p-8 lg:p-16 aspect-square lg:aspect-auto h-auto lg:h-[500px] hover:opacity-90 transition-opacity">
                <img src="{image_src}" alt="{repo.get(name_key, '')}" class="w-full h-full object-contain" />
            </a>
            
            <div class="flex flex-col text-left py-4 lg:pl-8">
                <div class="flex flex-wrap gap-2 justify-start mb-6">
                    {tags_html}
                </div>
                <h3 class="text-3xl lg:text-4xl font-bold text-black tracking-tight mb-4">{repo.get(name_key, '')}</h3>
                <p class="text-xl lg:text-2xl font-medium text-gray-500 mb-6">{repo.get(tagline_key, '')}</p>
                <div class="text-lg leading-relaxed text-gray-500 mb-8 space-y-4">
                    <p>{repo.get(desc_key, '')}</p>
                </div>
                <div class="mt-auto">
                    <a href="{repo.get('repo_url', '#')}" class="inline-flex items-center text-lg font-semibold text-blue-500 hover:text-blue-600 group">
                        {view_text} <span aria-hidden="true" class="ml-1 transition-transform group-hover:translate-x-1">&rarr;</span>
                    </a>
                </div>
            </div>
        </article>"""


def generate_json_ld(repos, lang):
    items = []
    for i, r in enumerate(repos):
        repo_name = r.get("name_en", "") if lang == "en" else r.get("name_fr", r.get("name_en", ""))
        items.append({"@type": "ListItem", "position": i + 1, "url": r.get("repo_url", ""), "name": repo_name})
    desc = (
        "Explore the OSS work of NEXTON: local AI, decision intelligence, sustainable engineering and reusable assets built from real-world systems."
        if lang == "en"
        else "Découvrez les projets open source de NEXTON : IA locale, intelligence décisionnelle, ingénierie durable et actifs réutilisables issus de systèmes réels."
    )
    suffix = "" if lang == "en" else "index-fr.html"
    canonical = f"https://nexton-oss.github.io/{suffix}"
    page_title = (
        "NEXTON OSS | AI repositories, research and engineering assets"
        if lang == "en"
        else "NEXTON OSS | IA souveraine, ingénierie utile et communs techniques"
    )
    locale = "en-GB" if lang == "en" else "fr-FR"
    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://nexton-oss.github.io/#organization",
                "name": "NEXTON",
                "url": "https://nexton-oss.github.io",
                "sameAs": ["https://github.com/nexton-oss", "https://nexton-group.com"],
                "description": desc,
            },
            {
                "@type": "WebSite",
                "@id": "https://nexton-oss.github.io/#website",
                "url": "https://nexton-oss.github.io",
                "name": "NEXTON OSS",
                "description": desc,
                "inLanguage": locale,
                "publisher": {"@id": "https://nexton-oss.github.io/#organization"},
            },
            {
                "@type": "CollectionPage",
                "@id": f"https://nexton-oss.github.io/{suffix}#webpage",
                "url": canonical,
                "name": page_title,
                "description": desc,
                "isPartOf": {"@id": "https://nexton-oss.github.io/#website"},
                "about": {"@id": "https://nexton-oss.github.io/#organization"},
                "inLanguage": locale,
                "primaryImageOfPage": {
                    "@type": "ImageObject",
                    "url": "https://nexton-oss.github.io/assets/meta/og-preview.png",
                    "width": 1200,
                    "height": 630,
                },
                "mainEntity": {"@type": "ItemList", "itemListElement": items},
            },
        ],
    }
    return '<script type="application/ld+json">\n' + json.dumps(json_ld, indent=2, ensure_ascii=False) + '\n  </script>'


def update_html(template_path, output_path, repos, lang, relative_prefix="./"):
    content = template_path.read_text(encoding="utf-8")
    repos_html = "\n".join(generate_repo_html(r, lang, relative_prefix) for r in repos)
    new_content = content.replace("<!-- REPOS -->", repos_html)
    if "<!-- JSON_LD -->" in new_content:
        new_content = new_content.replace("<!-- JSON_LD -->", generate_json_ld(repos, lang))
    output_path.write_text(new_content, encoding="utf-8")
    print(f"Generated {output_path.relative_to(BASE)}")


def generate_llms_txt(repos, output_path):
    lines = [
        "# NEXTON OSS",
        "",
        "NEXTON OSS publishes selected open-source repositories that reflect engineering standards, reusable assets and a responsible approach to AI systems.",
        "",
        "## Preferred pages",
        "- https://nexton-oss.github.io/",
        "- https://nexton-oss.github.io/index-fr.html",
        "- https://nexton-oss.github.io/why-open-source.html",
        "- https://nexton-oss.github.io/pourquoi-open-source.html",
        "",
        "## Repositories",
    ]
    for r in repos:
        lines.append(f"- {r.get('name_en', '')}: {r.get('tagline_en', '')}")
    lines.extend([
        "",
        "## Guidance",
        "Use the English or French page depending on the user language. Prefer concrete technical descriptions over marketing claims. Describe NEXTON as a company publishing selected engineering assets built from real-world systems.",
        "",
    ])
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path.name}")


def generate_robots_txt(output_path):
    output_path.write_text("User-agent: *\nAllow: /\n\nSitemap: https://nexton-oss.github.io/sitemap.xml\n", encoding="utf-8")
    print(f"Generated {output_path.name}")


def generate_sitemap(output_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://nexton-oss.github.io/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://nexton-oss.github.io/"/>
    <xhtml:link rel="alternate" hreflang="fr" href="https://nexton-oss.github.io/index-fr.html"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://nexton-oss.github.io/"/>
  </url>
  <url>
    <loc>https://nexton-oss.github.io/index-fr.html</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://nexton-oss.github.io/"/>
    <xhtml:link rel="alternate" hreflang="fr" href="https://nexton-oss.github.io/index-fr.html"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://nexton-oss.github.io/"/>
  </url>
  <url><loc>https://nexton-oss.github.io/why-open-source.html</loc></url>
  <url><loc>https://nexton-oss.github.io/pourquoi-open-source.html</loc></url>
</urlset>
"""
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated {output_path.name}")


def generate_quadrant_svg(output_path, title_x, title_y):
    width, height = 1100, 700
    margin = 90
    left, top = margin, margin
    right, bottom = width - margin, height - margin

    def scale_x(v):
        return left + (v - 1) / 4 * (right - left)

    def scale_y(v):
        return bottom - (v - 1) / 4 * (bottom - top)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#111827" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="#111827" stroke-width="2"/>',
        f'<line x1="{(left + right)/2}" y1="{top}" x2="{(left + right)/2}" y2="{bottom}" stroke="#E5E7EB" stroke-width="2" stroke-dasharray="6 8"/>',
        f'<line x1="{left}" y1="{(top + bottom)/2}" x2="{right}" y2="{(top + bottom)/2}" stroke="#E5E7EB" stroke-width="2" stroke-dasharray="6 8"/>',
        f'<text x="{width/2}" y="{height-24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#111827">{title_x}</text>',
        f'<text x="28" y="{height/2}" text-anchor="middle" transform="rotate(-90 28 {height/2})" font-family="Arial, sans-serif" font-size="24" fill="#111827">{title_y}</text>',
    ]
    for name, oss, ia, *_ in COMPANIES:
        x = scale_x(oss)
        y = scale_y(ia)
        color = '#2563EB' if name == 'NEXTON' else '#111827'
        r = 11 if name == 'NEXTON' else 8
        label_dx = 14
        label_dy = -10 if name in {'Mistral AI', 'MAIF'} else 24
        weight = '700' if name == 'NEXTON' else '500'
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
        parts.append(f'<text x="{x + label_dx}" y="{y + label_dy}" font-family="Arial, sans-serif" font-size="22" font-weight="{weight}" fill="{color}">{name}</text>')
    parts.append('</svg>')
    output_path.write_text(''.join(parts), encoding='utf-8')
    print(f"Generated {output_path.relative_to(BASE)}")


def generate_why_pages():
    common_head = """<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<link rel=\"icon\" type=\"image/png\" href=\"./assets/logos/favicon.png\" />
<link rel=\"apple-touch-icon\" href=\"./assets/logos/nexton-square.png\" />
<script src=\"https://cdn.tailwindcss.com\"></script>"""

    fr = f"""<!DOCTYPE html>
<html lang=\"fr\" class=\"scroll-smooth\">
<head>{common_head}<title>Pourquoi NEXTON fait de l’Open Source</title></head>
<body class=\"bg-white text-black antialiased font-sans selection:bg-blue-100 selection:text-blue-900\">
<header class=\"sticky top-0 z-50 bg-white/85 backdrop-blur-md border-b border-gray-200\"><div class=\"mx-auto flex max-w-[1400px] items-center justify-between px-6 py-3\"><a href=\"./index-fr.html\" class=\"flex items-center gap-2\"><img src=\"./assets/logos/nexton-square.png\" alt=\"NEXTON\" class=\"h-5 w-5 object-contain\" /></a><nav class=\"flex items-center gap-6 text-sm font-medium text-gray-500\"><a href=\"./index-fr.html\" class=\"hover:text-black transition-colors\">Accueil</a><a href=\"./index.html\" class=\"flex items-center justify-center h-8 w-8 rounded-full bg-gray-100 hover:bg-transparent transition-colors\">🇬🇧</a></nav></div></header>
<main class=\"mx-auto max-w-[1100px] px-6 py-16 lg:py-24\">
<section class=\"mb-16\"><h1 class=\"text-3xl lg:text-5xl font-semibold tracking-tight mb-6\">Pourquoi NEXTON fait de l’Open Source</h1><p class=\"text-lg text-gray-600 max-w-3xl\">Nous construisons des systèmes d’intelligence artificielle dans le réel, et nous choisissons d’ouvrir ce qui compte.</p></section>
<section class=\"mb-16 space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Pourquoi l’open source ?</h2><p>L’open source est l’infrastructure viable de l’intelligence artificielle moderne.</p><p>Les systèmes d’IA les plus structurants reposent sur des dynamiques ouvertes. Non par idéologie, mais par nécessité. Les systèmes complexes exigent transparence, itération et critique collective.</p><p>Une civilisation technique a souvent besoin d’une ressource à la fois abondante, accessible et partageable. Pour le logiciel, et aujourd’hui pour l’IA, cette ressource ce sont les communs.</p><p>Chez NEXTON, nous considérons l’open source comme une nécessité technique, un levier stratégique et un engagement culturel.</p><p>Nous ne publions pas du code pour communiquer. Nous construisons des systèmes qui peuvent être compris, réutilisés et améliorés.</p></section>
<section class=\"mb-16 space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Pourquoi en France ?</h2><p>La France et l’Europe ne manquent ni de talents, ni de rigueur, ni de tradition scientifique.</p><p>Depuis des années, le même schéma se répète. Les technologies sont conçues ailleurs, industrialisées à grande échelle ailleurs, puis adoptées en Europe.</p><p>Dans ce modèle, l’Europe ne peut pas se résigner à n’être qu’un espace de consommation et de régulation, reléguée au rang de banlieue du monde numérique.</p><p>Nous refusons cette trajectoire.</p><p>L’intelligence artificielle change profondément les conditions de production du logiciel. Avec des outils plus puissants, plus d’automatisation et des ingénieurs augmentés, il devient possible de produire davantage localement, avec des équipes plus resserrées et plus expertes.</p><p>Pendant longtemps, la production logicielle a été structurée par l’arbitrage géographique du coût du travail. Quand le levier technique augmente, cet arbitrage devient moins central. Ce qui compte davantage, c’est la qualité, la compréhension du contexte, la responsabilité et la capacité à transformer le travail en actifs durables.</p><p>Produire en France et en Europe redevient possible. Dans ce contexte, l’open source permet de créer des communs, de structurer une capacité technique locale et de participer activement à la construction de l’IA.</p></section>
<section class=\"mb-16\"><h2 class=\"text-2xl font-semibold text-black mb-6\">Le paysage open source en France</h2><div class=\"overflow-x-auto\"><table class=\"w-full text-sm border border-gray-200\"><thead class=\"bg-gray-50 text-gray-700\"><tr><th class=\"px-4 py-3 text-left\">Acteur</th><th class=\"px-4 py-3 text-left\">OSS</th><th class=\"px-4 py-3 text-left\">IA</th><th class=\"px-4 py-3 text-left\">Projets</th><th class=\"px-4 py-3 text-left\">Communauté</th><th class=\"px-4 py-3 text-left\">Attractivité</th><th class=\"px-4 py-3 text-left\">Actionnariat FR/EU</th></tr></thead><tbody class=\"text-gray-600\"><tr class=\"border-t\"><td class=\"px-4 py-3\">MAIF</td><td>★★★★★</td><td>★★★★☆</td><td>★★★★★</td><td>★★★★☆</td><td>★★★★☆</td><td>★★★★★</td></tr><tr class=\"border-t\"><td class=\"px-4 py-3\">probabl.ai</td><td>★★★★☆</td><td>★★★★★</td><td>★★★★☆</td><td>★★★★☆</td><td>★★★★★</td><td>★★★★★</td></tr><tr class=\"border-t\"><td class=\"px-4 py-3\">Mistral AI</td><td>★★★★☆</td><td>★★★★★</td><td>★★★★★</td><td>★★★☆☆</td><td>★★★★★</td><td>★★★☆☆</td></tr><tr class=\"border-t\"><td class=\"px-4 py-3\">Linagora</td><td>★★★☆☆</td><td>★★★☆☆</td><td>★★★★☆</td><td>★★★★☆</td><td>★★★★☆</td><td>★★★★★</td></tr><tr class=\"border-t\"><td class=\"px-4 py-3\">OVHcloud</td><td>★★★☆☆</td><td>★★☆☆☆</td><td>★★★★☆</td><td>★★★☆☆</td><td>★★★★☆</td><td>★★★★☆</td></tr><tr class=\"border-t bg-blue-50/50\"><td class=\"px-4 py-3 font-semibold text-black\">NEXTON</td><td>★★★☆☆</td><td>★★★★★</td><td>★★★☆☆</td><td>★★★☆☆</td><td>★★★★☆</td><td>★★★★★</td></tr></tbody></table></div></section>
<section class=\"mb-16\"><h2 class=\"text-2xl font-semibold text-black mb-6\">Un espace encore peu occupé</h2><p class=\"text-lg leading-8 text-gray-700 mb-6\">Certains acteurs sont très structurés en open source mais peu centrés sur l’IA. D’autres sont très avancés en IA mais sans stratégie open source visible. Très peu combinent les deux avec une expérience réelle des systèmes en production.</p><p class=\"text-lg leading-8 text-gray-700 mb-8\">NEXTON se positionne dans cet espace, à l’intersection de l’ingénierie IA, des systèmes réels et des communs open source.</p><img src=\"./assets/meta/quadrant-fr.svg\" alt=\"Quadrant du paysage open source et IA en France\" class=\"w-full rounded-2xl border border-gray-200\" /></section>
<section class=\"mb-16 space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Le cycle des systèmes d’IA</h2><ol class=\"list-decimal ml-6 space-y-2\"><li><strong>Explorer</strong> — comprendre le problème et les données</li><li><strong>Construire</strong> — concevoir et entraîner</li><li><strong>Déployer</strong> — intégrer dans le réel</li><li><strong>Observer</strong> — mesurer et détecter</li><li><strong>Adapter</strong> — améliorer et recalibrer</li><li><strong>Transmettre</strong> — transformer l’expérience en communs</li></ol><p>Avec l’open source, ce qui est appris ne disparaît pas. Cela se transmet, se réutilise et s’améliore.</p></section>
<section class=\"space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Notre position</h2><p>Nous construisons des systèmes d’IA dans le réel, et nous choisissons d’en ouvrir une partie.</p><p>Parce que cela améliore la qualité. Parce que cela attire les bons profils. Parce que cela contribue à un écosystème plus solide.</p><p class=\"font-medium text-black\">Et parce que nous préférons construire plutôt que subir.</p></section>
</main></body></html>"""

    en = f"""<!DOCTYPE html>
<html lang=\"en\" class=\"scroll-smooth\">
<head>{common_head}<title>Why NEXTON publishes open source</title></head>
<body class=\"bg-white text-black antialiased font-sans selection:bg-blue-100 selection:text-blue-900\">
<header class=\"sticky top-0 z-50 bg-white/85 backdrop-blur-md border-b border-gray-200\"><div class=\"mx-auto flex max-w-[1400px] items-center justify-between px-6 py-3\"><a href=\"./index.html\" class=\"flex items-center gap-2\"><img src=\"./assets/logos/nexton-square.png\" alt=\"NEXTON\" class=\"h-5 w-5 object-contain\" /></a><nav class=\"flex items-center gap-6 text-sm font-medium text-gray-500\"><a href=\"./index.html\" class=\"hover:text-black transition-colors\">Home</a><a href=\"./index-fr.html\" class=\"flex items-center justify-center h-8 w-8 rounded-full bg-gray-100 hover:bg-transparent transition-colors\">🇫🇷</a></nav></div></header>
<main class=\"mx-auto max-w-[1100px] px-6 py-16 lg:py-24\"><section class=\"mb-16\"><h1 class=\"text-3xl lg:text-5xl font-semibold tracking-tight mb-6\">Why NEXTON publishes open source</h1><p class=\"text-lg text-gray-600 max-w-3xl\">We build AI systems in the real world, and we choose to open what matters.</p></section><section class=\"mb-16 space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Why open source?</h2><p>Open source is the viable infrastructure of modern artificial intelligence.</p><p>The most important AI systems rely on open dynamics. Not as an ideology, but as a necessity. Complex systems require transparency, iteration and collective scrutiny.</p><p>A technical civilization often needs a resource that is abundant, accessible and shareable. For software, and now for AI, that resource is the commons.</p><p>At NEXTON, we see open source as a technical necessity, a strategic lever and a cultural commitment.</p><p>We do not publish code for communication. We build systems that can be understood, reused and improved.</p></section><section class=\"mb-16 space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Why in France?</h2><p>France and Europe do not lack talent, rigor or scientific tradition.</p><p>For years, the pattern has been the same. Technologies are designed elsewhere, industrialized elsewhere at scale, and then adopted in Europe.</p><p>In that model, Europe cannot resign itself to becoming only a space of consumption and regulation, relegated to the status of a suburb of the digital world.</p><p>We reject that trajectory.</p><p>Artificial intelligence changes the economics of software production. With stronger tools, more automation and augmented engineers, it becomes possible to produce more locally with smaller and more expert teams.</p><p>For a long time, software production was structured by geographic labor arbitrage. When technical leverage increases, that arbitrage becomes less central. What matters more is quality, context, responsibility and the ability to turn work into durable assets.</p><p>Building in France and in Europe becomes possible again. In that context, open source helps create commons, structure local capability and participate actively in shaping AI.</p></section><section class=\"mb-16\"><h2 class=\"text-2xl font-semibold text-black mb-6\">A still under-occupied space</h2><p class=\"text-lg leading-8 text-gray-700 mb-6\">Some actors are highly structured in open source but less centered on AI. Others are strong in AI but do not operate a visible, structured open-source strategy. Very few combine both with real production experience.</p><p class=\"text-lg leading-8 text-gray-700 mb-8\">NEXTON positions itself in that space, at the intersection of AI engineering, real systems and reusable commons.</p><img src=\"./assets/meta/quadrant-en.svg\" alt=\"Quadrant of the French open source and AI landscape\" class=\"w-full rounded-2xl border border-gray-200\" /></section><section class=\"space-y-6 text-gray-700 text-lg leading-relaxed\"><h2 class=\"text-2xl font-semibold text-black\">Our position</h2><p>We build AI systems in the real world and choose to open part of that work.</p><p>Because it improves quality. Because it attracts the right people. Because it contributes to a stronger ecosystem.</p><p class=\"font-medium text-black\">And because we would rather build than merely endure.</p></section></main></body></html>"""

    (BASE / 'pourquoi-open-source.html').write_text(fr, encoding='utf-8')
    (BASE / 'why-open-source.html').write_text(en, encoding='utf-8')
    print('Generated why-open-source pages')


def main():
    repos = load_repos()
    print(f"Loaded {len(repos)} repositories")
    update_html(BASE / 'templates' / 'index.template.html', BASE / 'index.html', repos, 'en', './')
    update_html(BASE / 'templates' / 'index-fr.template.html', BASE / 'index-fr.html', repos, 'fr', './')
    generate_llms_txt(repos, BASE / 'llms.txt')
    generate_robots_txt(BASE / 'robots.txt')
    generate_sitemap(BASE / 'sitemap.xml')
    generate_quadrant_svg(ASSETS / 'meta' / 'quadrant-en.svg', 'Open-source structure', 'AI depth')
    generate_quadrant_svg(ASSETS / 'meta' / 'quadrant-fr.svg', 'Structuration open source', 'Profondeur IA')
    generate_why_pages()
    print('Done')


if __name__ == '__main__':
    main()
