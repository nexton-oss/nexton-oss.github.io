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

def generate_repo_html(repo, lang, relative_prefix=""):
    tags_key = f"tags_{lang}"
    name_key = f"name_{lang}"
    tagline_key = f"tagline_{lang}"
    desc_key = f"description_{lang}"
    
    tags_list = repo.get(tags_key, [])
    # Flat tags without shadow, strict gray borders for readability
    tags_html = "".join([f'<span class="inline-flex items-center rounded-full bg-white border border-gray-200 px-3 py-1 text-xs font-semibold text-gray-500 shadow-none">{tag}</span>' for tag in tags_list])
    
    view_text = "View repository" if lang == "en" else "Voir le dépôt"
    image_src = f"{relative_prefix}{repo.get('image', '')}"
    
    # Apple HIG style: flat bg-gray-50 container, padding p-8 or p-12 for inner space.
    # On mobile (portrait), grid-cols-1 forces stacking. On desktop (landscape), grid-cols-2 splits nicely left and right.
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

def update_html(template_path, output_path, repos, lang, relative_prefix=""):
    content = template_path.read_text(encoding="utf-8")
    repos_html = "\n".join(generate_repo_html(r, lang, relative_prefix) for r in repos)
    
    # Generate JSON-LD dynamically to stay completely perfectly synced.
    items = []
    for i, r in enumerate(repos):
        repo_name = r.get("name_en", "") if lang == "en" else r.get("name_fr", r.get("name_en", ""))
        items.append({
            "@type": "ListItem",
            "position": i + 1,
            "url": r.get("repo_url", ""),
            "name": repo_name
        })
    
    desc = "Curated open-source projects from NEXTON. Discover reliable building blocks for cost-aware decision intelligence, local-first LLMs and privacy-centric engineering." if lang == "en" else "Découvrez les projets open source de NEXTON. Des ressources fiables pour l'intelligence décisionnelle sensible aux coûts, les LLMs locaux et l'ingénierie soucieuse de la vie privée."
    suffix = "" if lang == "en" else "index-fr.html"
    canonical = f"https://nexton-oss.github.io/{suffix}"
    page_title = "NEXTON OSS | Sovereign AI, Decision Intelligence & Trust by Design" if lang == "en" else "NEXTON OSS | IA Souveraine, Intelligence Décisionnelle & Confiance by Design"
    locale = "en-GB" if lang == "en" else "fr-FR"

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://nexton-oss.github.io/#organization",
                "name": "NEXTON",
                "url": "https://nexton-oss.github.io",
                "sameAs": ["https://github.com/nexton-oss", "https://github.com/nexton-group"],
                "description": desc
            },
            {
                "@type": "WebSite",
                "@id": "https://nexton-oss.github.io/#website",
                "url": "https://nexton-oss.github.io",
                "name": "NEXTON OSS",
                "description": desc,
                "inLanguage": locale,
                "publisher": {"@id": "https://nexton-oss.github.io/#organization"}
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
                    "height": 630
                },
                "mainEntity": {
                    "@type": "ItemList",
                    "itemListElement": items
                }
            }
        ]
    }
    
    json_ld_script = '<script type="application/ld+json">\n' + json.dumps(json_ld, indent=2, ensure_ascii=False) + '\n  </script>'

    # Replace content markers
    if "<!-- REPOS -->" not in content:
        print(f"Error: <!-- REPOS --> placeholder not found in {template_path.name}", file=sys.stderr)
        return
        
    new_content = content.replace("<!-- REPOS -->", repos_html)
    
    if "<!-- JSON_LD -->" in new_content:
        new_content = new_content.replace("<!-- JSON_LD -->", json_ld_script)

    output_path.write_text(new_content, encoding="utf-8")
    print(f"Successfully generated {output_path.relative_to(BASE)} from {template_path.relative_to(BASE)} ({lang})")

if __name__ == "__main__":
    repos = load_repos()
    print(f"Loaded {len(repos)} repositories")
    
    update_html(
        template_path=BASE / "templates" / "index.template.html",
        output_path=BASE / "index.html",
        repos=repos,
        lang="en",
        relative_prefix="./"
    )
    
    update_html(
        template_path=BASE / "templates" / "index-fr.template.html",
        output_path=BASE / "index-fr.html",
        repos=repos,
        lang="fr",
        relative_prefix="./"
    )
    print("Done")
