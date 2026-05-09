import urllib.request
import xml.etree.ElementTree as ET
import json
import random
import os

def fetch_arxiv_papers(query="search_query=all:search+engine+OR+all:machine+learning", max_results=300):
    url = f"http://export.arxiv.org/api/query?{query}&start=0&max_results={max_results}"
    print(f"Fetch url: {url}")
    print("Connecting to ArXiv API...")
    
    response = urllib.request.urlopen(url)
    xml_data = response.read()
    root = ET.fromstring(xml_data)
    
    ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
    papers = []
    
    for entry in root.findall('arxiv:entry', ns):
        # Safely extract text
        title_elem = entry.find('arxiv:title', ns)
        summary_elem = entry.find('arxiv:summary', ns)
        id_elem = entry.find('arxiv:id', ns)
        pub_elem = entry.find('arxiv:published', ns)
        
        title = title_elem.text.replace('\n', ' ').strip() if title_elem is not None else "No Title"
        summary = summary_elem.text.replace('\n', ' ').strip() if summary_elem is not None else ""
        link = id_elem.text if id_elem is not None else ""
        published = pub_elem.text if pub_elem is not None else "Unknown"
        
        authors = [author.find('arxiv:name', ns).text for author in entry.findall('arxiv:author', ns) if author.find('arxiv:name', ns) is not None]
        
        # 模拟权威分(PageRank/引用量) - 课程展示效果使用
        # 实际情况需要根据复杂的论文引用关系图进行图计算(PageRank)，这里用长尾分布(Beta)模拟一个合理的归一化得分0~1
        authority_score = random.betavariate(2, 5) 
        
        papers.append({
            "id": link.split('/')[-1] if link else str(random.randint(1000, 9999)),
            "title": title,
            "abstract": summary,
            "authors": authors,
            "published": published,
            "url": link,
            "authority_score": authority_score
        })
        
    os.makedirs('data', exist_ok=True)
    with open('data/papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully fetched {len(papers)} papers and saved to data/papers.json")

if __name__ == "__main__":
    fetch_arxiv_papers()
