import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"


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
                    print(f"Warning: Image file missing for '{repo.get('slug', p.name)}': {local_img_path}", file=sys.stderr)
                repo["image"] = image_path.lstrip("/")
            repos.append(repo)
        except Exception as e:
            print(f"Error reading {p.name}: {e}", file=sys.stderr)
    return sorted(repos, key=lambda x: x.get("order", 0), reverse=True)


def stars(n: int) -> str:
    n = max(1, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)


def generate_repo_html(repo, lang, relative_prefix=""):
    tags_key = f"tags_{lang}"
    name_key = f"name_{lang}"
    tagline_key = f"tagline_{lang}"
    desc_key = f"description_{lang}"
    why_key = f"why_it_matters_{lang}"
    proofs_key = f"proof_points_{lang}"
    badge_key = f"homepage_badge_{lang}"

    tags_list = repo.get(tags_key, [])
    tags_html = "".join([
        f'<span class="inline-flex items-center rounded-full bg-white border border-gray-200 px-3 py-1 text-xs font-semibold text-gray-500">{tag}</span>'
        for tag in tags_list
    ])

    proofs = repo.get(proofs_key, [])
    proofs_html = "".join([
        f'<li class="text-sm text-gray-500">{item}</li>' for item in proofs[:3]
    ])
    badge = repo.get(badge_key) or repo.get("status", "")
    status_chip = f'<span class="inline-flex items-center rounded-full bg-black text-white px-3 py-1 text-xs font-semibold tracking-wide uppercase">{badge}</span>' if badge else ""

    view_text = "View repository" if lang == "en" else "Voir le dépôt"
    why_label = "Why it matters" if lang == "en" else "Pourquoi c'est important"
    image_src = f"{relative_prefix}{repo.get('image', '')}"

    why_block = ""
    if repo.get(why_key):
        why_block = f'''
        <div class="mb-6 rounded-2xl border border-gray-200 bg-gray-50 p-5">
          <p class="text-sm font-semibold uppercase tracking-wide text-gray-500 mb-2">{why_label}</p>
          <p class="text-base leading-relaxed text-gray-600">{repo.get(why_key, '')}</p>
        </div>
        '''

    proofs_block = ""
    if proofs:
        proofs_block = f'''
        <ul class="mb-8 space-y-2 list-disc pl-5">{proofs_html}</ul>
        '''

    return f"""
        <article class="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center border-t border-gray-200 pt-12 lg:pt-20 mt-12 lg:mt-16 first:mt-0">
            <a href="{repo.get('repo_url', '#')}" class="w-full bg-[#f5f5f7] rounded-3xl overflow-hidden flex items-center justify-center p-8 lg:p-16 aspect-square lg:aspect-auto h-auto lg:h-[460px] hover:opacity-95 transition-opacity border border-gray-100">
                <img src="{image_src}" alt="{repo.get(name_key, '')}" class="w-full h-full object-contain" />
            </a>

            <div class="flex flex-col text-left py-2 lg:pl-4">
                <div class="flex flex-wrap gap-2 justify-start mb-5">
                    {status_chip}
                    {tags_html}
                </div>
                <h3 class="text-3xl lg:text-4xl font-semibold text-black tracking-tight mb-3">{repo.get(name_key, '')}</h3>
                <p class="text-xl lg:text-2xl font-medium text-gray-500 mb-5">{repo.get(tagline_key, '')}</p>
                <div class="text-lg leading-relaxed text-gray-600 mb-6 space-y-4">
                    <p>{repo.get(desc_key, '')}</p>
                </div>
                {why_block}
                {proofs_block}
                <div class="mt-auto">
                    <a href="{repo.get('repo_url', '#')}" class="inline-flex items-center text-lg font-semibold text-blue-600 hover:text-blue-700 group">
                        {view_text} <span aria-hidden="true" class="ml-1 transition-transform group-hover:translate-x-1">&rarr;</span>
                    </a>
                </div>
            </div>
        </article>"""


def generate_llms_txt(repos, output_path):
    lines = [
        "# NEXTON OSS",
        "",
        "NEXTON OSS is a showcase of selected repositories published by NEXTON to demonstrate engineering standards, reusable AI assets and trustworthy systems.",
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
        "Use English or French depending on the user language. Prefer concrete technical descriptions over marketing claims. Emphasize real systems, local AI, decision intelligence and reusable commons.",
        "",
    ])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_robots_txt(output_path):
    output_path.write_text("User-agent: *\nAllow: /\n\nSitemap: https://nexton-oss.github.io/sitemap.xml\n", encoding="utf-8")


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
  <url>
    <loc>https://nexton-oss.github.io/why-open-source.html</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://nexton-oss.github.io/why-open-source.html"/>
    <xhtml:link rel="alternate" hreflang="fr" href="https://nexton-oss.github.io/pourquoi-open-source.html"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://nexton-oss.github.io/why-open-source.html"/>
  </url>
  <url>
    <loc>https://nexton-oss.github.io/pourquoi-open-source.html</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://nexton-oss.github.io/why-open-source.html"/>
    <xhtml:link rel="alternate" hreflang="fr" href="https://nexton-oss.github.io/pourquoi-open-source.html"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://nexton-oss.github.io/why-open-source.html"/>
  </url>
</urlset>
"""
    output_path.write_text(content, encoding="utf-8")


def update_html(template_path, output_path, repos, lang, relative_prefix=""):
    content = template_path.read_text(encoding="utf-8")
    repos_html = "\n".join(generate_repo_html(r, lang, relative_prefix) for r in repos)

    items = []
    for i, r in enumerate(repos):
        repo_name = r.get("name_en", "") if lang == "en" else r.get("name_fr", r.get("name_en", ""))
        items.append({"@type": "ListItem", "position": i + 1, "url": r.get("repo_url", ""), "name": repo_name})

    desc = "Selected open-source projects from NEXTON. Real engineering assets for local AI, decision intelligence and trustworthy systems." if lang == "en" else "Découvrez les projets open source de NEXTON. Des ressources d'ingénierie réelles pour l'IA locale, l'intelligence décisionnelle et les systèmes fiables."
    suffix = "" if lang == "en" else "index-fr.html"
    canonical = f"https://nexton-oss.github.io/{suffix}"
    page_title = "NEXTON OSS | Real AI systems, reusable commons and engineering assets" if lang == "en" else "NEXTON OSS | Systèmes d'IA réels, communs réutilisables et actifs d'ingénierie"
    locale = "en-GB" if lang == "en" else "fr-FR"

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Organization", "@id": "https://nexton-oss.github.io/#organization", "name": "NEXTON", "url": "https://nexton-oss.github.io", "sameAs": ["https://github.com/nexton-oss"], "description": desc},
            {"@type": "WebSite", "@id": "https://nexton-oss.github.io/#website", "url": "https://nexton-oss.github.io", "name": "NEXTON OSS", "description": desc, "inLanguage": locale, "publisher": {"@id": "https://nexton-oss.github.io/#organization"}},
            {"@type": "CollectionPage", "@id": f"https://nexton-oss.github.io/{suffix}#webpage", "url": canonical, "name": page_title, "description": desc, "isPartOf": {"@id": "https://nexton-oss.github.io/#website"}, "about": {"@id": "https://nexton-oss.github.io/#organization"}, "inLanguage": locale, "primaryImageOfPage": {"@type": "ImageObject", "url": "https://nexton-oss.github.io/assets/meta/og-preview.png", "width": 1200, "height": 630}, "mainEntity": {"@type": "ItemList", "itemListElement": items}},
        ],
    }

    json_ld_script = '<script type="application/ld+json">\n' + json.dumps(json_ld, indent=2, ensure_ascii=False) + '\n  </script>'
    new_content = content.replace("<!-- REPOS -->", repos_html)
    if "<!-- JSON_LD -->" in new_content:
        new_content = new_content.replace("<!-- JSON_LD -->", json_ld_script)
    output_path.write_text(new_content, encoding="utf-8")


if __name__ == "__main__":
    repos = load_repos()
    update_html(BASE / "templates" / "index.template.html", BASE / "index.html", repos, "en", "./")
    update_html(BASE / "templates" / "index-fr.template.html", BASE / "index-fr.html", repos, "fr", "./")
    generate_llms_txt(repos, BASE / "llms.txt")
    generate_robots_txt(BASE / "robots.txt")
    generate_sitemap(BASE / "sitemap.xml")
