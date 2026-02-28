import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import json
import os

results_all = []
seen_ids = set()

queries = [
    'all:"CVPR 2026"',
    'all:"CVPR2026"',
    'all:"CVPR 26"',
    'all:"CVPR26"',
    'all:"cvpr26"',
    "all:\"CVPR'26\"",
    "all:\"CVPR '26\"",
    'all:"CVPR-2026"',
    'all:"Conference on Computer Vision and Pattern Recognition 2026"',
]

for q in queries:
    for start in range(0, 400, 200):
        params = urllib.parse.urlencode({
            'search_query': q,
            'start': start,
            'max_results': 200,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        })
        url = f'http://export.arxiv.org/api/query?{params}'
        print(f'Searching: {q} (start={start})')

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode('utf-8')

            root = ET.fromstring(data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            entries = root.findall('atom:entry', ns)
            count = 0

            for entry in entries:
                arxiv_id = entry.find('atom:id', ns).text.strip().split('/')[-1]
                if arxiv_id in seen_ids:
                    continue

                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                while '  ' in title:
                    title = title.replace('  ', ' ')

                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                while '  ' in summary:
                    summary = summary.replace('  ', ' ')

                published = entry.find('atom:published', ns).text.strip()

                combined = (title + ' ' + summary).lower()
                if 'workshop' in combined:
                    continue
                if 'finding' in combined:
                    continue

                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns).text.strip()
                    authors.append(name)

                link = entry.find('atom:id', ns).text.strip()
                pdf_link = link.replace('/abs/', '/pdf/')

                categories = []
                for cat in entry.findall('atom:category', ns):
                    categories.append(cat.get('term', ''))

                seen_ids.add(arxiv_id)
                results_all.append({
                    'id': arxiv_id,
                    'title': title,
                    'authors': authors,
                    'published': published[:10],
                    'link': link,
                    'pdf': pdf_link,
                    'categories': categories,
                    'summary': summary
                })
                count += 1

            print(f'  New papers added: {count}')
            if len(entries) < 200:
                break

        except Exception as e:
            print(f'  Error: {e}')

        time.sleep(3)

    time.sleep(3)

print(f'\n=== Total unique papers (excluding workshops): {len(results_all)} ===\n')

results_all.sort(key=lambda x: x['published'], reverse=True)

import sys
sys.stdout.reconfigure(encoding='utf-8')

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(output_dir, exist_ok=True)

json_path = os.path.join(output_dir, 'cvpr26.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results_all, f, ensure_ascii=False, indent=2)
print(f'JSON saved to {json_path}')

md_path = os.path.join(output_dir, 'CVPR26_papers.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(f'# CVPR 2026 论文列表 (arXiv)\n\n')
    f.write(f'> 来源: arXiv API 搜索\n')
    f.write(f'> 关键词: CVPR 2026, CVPR2026, CVPR 26, cvpr26\n')
    f.write(f'> 已排除 workshop 论文\n')
    f.write(f'> 总计: {len(results_all)} 篇论文\n\n')
    f.write(f'---\n\n')

    for i, r in enumerate(results_all, 1):
        authors_str = ', '.join(r['authors'][:5])
        if len(r['authors']) > 5:
            authors_str += f' 等 (共{len(r["authors"])}位作者)'
        cats = ', '.join(r['categories'][:3])

        f.write(f'## {i}. {r["title"]}\n\n')
        f.write(f'- **arXiv ID**: {r["id"]}\n')
        f.write(f'- **作者**: {authors_str}\n')
        f.write(f'- **发布日期**: {r["published"]}\n')
        f.write(f'- **分类**: {cats}\n')
        f.write(f'- **论文链接**: [{r["link"]}]({r["link"]})\n')
        f.write(f'- **PDF**: [{r["pdf"]}]({r["pdf"]})\n')
        f.write(f'- **摘要**: {r["summary"][:300]}{"..." if len(r["summary"]) > 300 else ""}\n\n')
        f.write(f'---\n\n')

print(f'Markdown saved to {md_path}')

for i, r in enumerate(results_all[:10], 1):
    print(f'{i}. [{r["published"]}] {r["title"][:80]}')
    print(f'   {r["link"]}')

print(f'\n... and {max(0, len(results_all)-10)} more papers')
