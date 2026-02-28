# 抓取 arXiv + HuggingFace 论文并保存到 data/ 目录
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import json
import os
import sys
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

CATEGORIES = ["cs.CV", "cs.CL", "cs.LG", "cs.MM"]
CATEGORY_NAMES = {
    "cs.CV": "计算机视觉", "cs.CL": "计算与语言",
    "cs.LG": "机器学习", "cs.MM": "多媒体",
}
API_URL = "http://export.arxiv.org/api/query"
BATCH_SIZE = 200
API_DELAY = 3


def fetch_arxiv(category, target_date):
    papers = []
    start = 0
    d_from = target_date.strftime("%Y%m%d") + "0000"
    d_to = target_date.strftime("%Y%m%d") + "2359"
    query = f"cat:{category} AND submittedDate:[{d_from} TO {d_to}]"

    while True:
        params = urllib.parse.urlencode({
            "search_query": query, "start": start,
            "max_results": BATCH_SIZE, "sortBy": "submittedDate", "sortOrder": "descending",
        })
        data = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(f"{API_URL}?{params}", headers={"User-Agent": "ArxivBot/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read().decode("utf-8")
                break
            except Exception as e:
                print(f"  [WARN] Retry {attempt+1}: {e}")
                time.sleep(5 * (attempt + 1))
        if data is None:
            break

        root = ET.fromstring(data)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = root.findall("a:entry", ns)
        if not entries:
            break

        for e in entries:
            title = e.find("a:title", ns).text.strip().replace("\n", " ")
            while "  " in title:
                title = title.replace("  ", " ")
            summary = e.find("a:summary", ns).text.strip().replace("\n", " ")
            while "  " in summary:
                summary = summary.replace("  ", " ")
            link = e.find("a:id", ns).text.strip()
            authors = [a.find("a:name", ns).text.strip() for a in e.findall("a:author", ns)]
            cats = [c.get("term", "") for c in e.findall("a:category", ns)]
            cmt_el = e.find("a:comment", ns)
            comment = cmt_el.text.strip() if cmt_el is not None and cmt_el.text else ""

            papers.append({
                "id": link.split("/")[-1], "title": title, "authors": authors,
                "published": e.find("a:published", ns).text.strip()[:10],
                "link": link, "pdf": link.replace("/abs/", "/pdf/"),
                "categories": cats, "primary_category": category,
                "summary": summary, "comment": comment,
            })

        if len(entries) < BATCH_SIZE:
            break
        start += BATCH_SIZE
        time.sleep(API_DELAY)
    return papers


def fetch_hf(target_date):
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://huggingface.co/api/daily_papers?date={date_str}"
    print(f"  Fetching HuggingFace Daily Papers...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ArxivBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [ERROR] HF fetch failed: {e}")
        return []

    papers = []
    for item in data:
        pd = item.get("paper", {})
        authors = [a.get("name", "") for a in pd.get("authors", []) if not a.get("hidden")]
        org = item.get("organization")
        papers.append({
            "id": pd.get("id", ""), "title": item.get("title", ""),
            "authors": authors, "summary": item.get("summary", ""),
            "link": f"https://huggingface.co/papers/{pd.get('id','')}",
            "pdf": f"http://arxiv.org/pdf/{pd.get('id','')}",
            "upvotes": pd.get("upvotes", 0), "comments": item.get("numComments", 0),
            "organization": org.get("name", "") if isinstance(org, dict) else "",
        })
    papers.sort(key=lambda x: x["upvotes"], reverse=True)
    return papers


def translate_papers(papers, api_key, api_type="zhipu"):
    if not papers:
        return
    if api_type == "zhipu":
        api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        model = "glm-4-flash"
    else:
        api_url = "https://api.deepseek.com/v1/chat/completions"
        model = "deepseek-chat"
    batch_size = 10
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        items = [f"{j+1}. {p['summary'][:300]}" for j, p in enumerate(batch)]
        prompt = "以下是AI论文摘要，请为每篇用2-3句中文概括论文的研究问题、方法和主要贡献（50-80字），每篇占一行，保持编号格式，只输出结果：\n" + "\n".join(items)
        try:
            body = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1, "max_tokens": 2000,
            })
            req = urllib.request.Request(
                api_url,
                data=body.encode("utf-8"),
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for j, p in enumerate(batch):
                if j < len(lines):
                    cn = lines[j]
                    for prefix in [f"{j+1}.", f"{j+1}、", f"{j+1} "]:
                        if cn.startswith(prefix):
                            cn = cn[len(prefix):].strip()
                    p["summary_cn"] = cn
            print(f"    Translated {i+1}-{i+len(batch)} / {len(papers)}")
        except Exception as e:
            print(f"    [WARN] Translation failed for batch {i}: {e}")
        time.sleep(0.5)


def deduplicate(all_papers):
    seen = {}
    for p in all_papers:
        pid = p["id"]
        if pid not in seen:
            seen[pid] = p
            seen[pid]["listed_in"] = [p["primary_category"]]
        else:
            if p["primary_category"] not in seen[pid]["listed_in"]:
                seen[pid]["listed_in"].append(p["primary_category"])
    return list(seen.values())


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        target_date = (datetime.now() - timedelta(days=1)).date()

    date_str = target_date.strftime("%Y-%m-%d")
    print(f"=== Fetching papers for {date_str} ===")
    os.makedirs(DATA_DIR, exist_ok=True)

    papers_by_cat = {}
    all_raw = []
    for cat in CATEGORIES:
        print(f"  {cat}...")
        p = fetch_arxiv(cat, target_date)
        papers_by_cat[cat] = p
        all_raw.extend(p)
        print(f"    {len(p)} papers")
        time.sleep(API_DELAY)

    arxiv_papers = deduplicate(all_raw)
    hf_papers = fetch_hf(target_date)

    api_key = os.environ.get("ZHIPU_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
    api_type = "zhipu" if os.environ.get("ZHIPU_API_KEY") else "deepseek"
    if api_key:
        print(f"  Translating with {api_type}...")
        translate_papers(arxiv_papers, api_key, api_type)
        translate_papers(hf_papers, api_key, api_type)
    else:
        print("  [SKIP] No API key, skipping translation")

    save_data = {"arxiv": arxiv_papers, "huggingface": hf_papers}
    json_path = os.path.join(DATA_DIR, f"{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"  arXiv: {len(arxiv_papers)}, HF: {len(hf_papers)}")
    print(f"  Saved: {json_path}")


if __name__ == "__main__":
    main()
