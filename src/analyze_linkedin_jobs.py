import sys
import os
import json
import re
from collections import Counter
from datetime import datetime
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def trim_title(t):
    m = re.search(r'\s*[-(\[]', t)
    return t[:m.start()].strip() if m else t.strip()

def barchart(counts, output_path, figsize_scale=0.4):
    labels = list(counts.keys())
    values = list(counts.values())
    fig, ax = plt.subplots(figsize=(8, max(3, len(labels) * figsize_scale)))
    bars = ax.barh(labels, values)
    ax.bar_label(bars, padding=3)
    ax.set_xlabel('Count')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def generate_summary_document(json_path):
    
    base = json_path.rsplit('.', 1)[0]
    md_path = base + '.md'

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    # Location chart
    location_counts = Counter(d.get('Location', '') for d in data)
    location_counts = dict(sorted(location_counts.items(), key=lambda x: x[1]))
    location_img = base + '_locations.png'
    barchart(location_counts, location_img, figsize_scale=0.5)

    # Company names
    company_counts = Counter(d.get('Company Name', '') for d in data)
    companies_sorted = sorted(company_counts.items(), key=lambda x: -x[1])
    companies_multi = [(n, c) for n, c in companies_sorted if c >= 2]
    companies_single = [n for n, c in companies_sorted if c == 1]

    # Titles (trimmed)
    title_counts = Counter(trim_title(d.get('Title', '')) for d in data)
    titles_sorted = sorted(title_counts.items(), key=lambda x: -x[1])
    titles_multi = {t: c for t, c in titles_sorted if c >= 2}
    titles_single = [t for t, c in titles_sorted if c == 1]
    title_img = base + '_titles.png'
    barchart(dict(sorted(titles_multi.items(), key=lambda x: x[1])), title_img, figsize_scale=0.45)

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('## Locations\n\n')
        f.write(f'![Locations]({location_img.split("/")[-1].split(chr(92))[-1]})\n\n')

        f.write('## Companies (N ≥ 2)\n\n')
        f.write(', '.join(f'{n} ({c})' for n, c in companies_multi) + '\n\n')

        f.write('## Companies (N = 1)\n\n')
        f.write(', '.join(companies_single) + '\n\n')

        f.write('## Titles (N ≥ 2)\n\n')
        f.write(f'![Titles]({title_img.split("/")[-1].split(chr(92))[-1]})\n\n')

        f.write('## Titles (N = 1)\n\n')
        f.write(', '.join(titles_single) + '\n\n')

    print(f'Written: {md_path}')

def generate_links_document(json_path, titles):
    base = json_path.rsplit('.', 1)[0]
    md_path = base + '_links.md'

    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    TYPE_MAP = {
        'hybrid':  ('Hybrid',  '🔀'),
        'remote':  ('Remote',  '🏠'),
        'on-site': ('On-site', '🏢'),
    }

    def extract_type(primary_desc):
        m = re.search(r'\(([^)]+)\)\s*$', primary_desc.strip())
        if not m:
            return primary_desc
        raw = m.group(1).lower()
        for key, (label, emoji) in TYPE_MAP.items():
            if key in raw:
                return f'{emoji} {label}'
        return m.group(1)

    def parse_dt(s):
        return datetime.strptime(s.rstrip('Z').split('.')[0], '%Y-%m-%dT%H:%M:%S')

    def compute_age(created_at, scraped_at):
        delta = parse_dt(scraped_at) - parse_dt(created_at)
        days = delta.days
        return f'{days // 7}w' if days >= 7 else f'{days}d'

    lines = []
    for title in titles:
        jobs = [d for d in data if trim_title(d.get('Title', '')) == title]
        if not jobs:
            continue
        lines.append(f'## {title}\n')
        lines.append('| Title | Type | Old | Company Name | Link |')
        lines.append('|-------|------|-----|--------------|------|')
        for job in jobs:
            t = job.get('Title', '')
            job_type = extract_type(job.get('Primary Description', ''))
            age = compute_age(job.get('Created At', ''), job.get('Scraped At', ''))
            company = job.get('Company Name', '')
            url = job.get('Detail URL', '')
            lines.append(f'| {t} | {job_type} | {age} | {company} | [link]({url}) |')
        lines.append('')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Written: {md_path}')


if __name__ == '__main__':
    json_path = sys.argv[1]

    generate_summary_document(json_path)

    yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'job_titles.yaml')
    with open(yaml_path, encoding='utf-8') as f:
        titles = yaml.safe_load(f)

    generate_links_document(json_path, titles)
