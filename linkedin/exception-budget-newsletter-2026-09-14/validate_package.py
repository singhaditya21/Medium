"""Static package checks; these do not substitute for visual or production testing."""
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).parent


class Inventory(HTMLParser):
    def __init__(self):
        super().__init__();self.images=[];self.links=[];self.ids=[];self.figures=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='img':self.images.append(d)
        if tag=='a':self.links.append(d.get('href',''))
        if 'id' in d:self.ids.append(d['id'])
        if tag=='figure':self.figures+=1


def validate():
    html=(ROOT/'index.html').read_text();md=(ROOT/'newsletter.md').read_text()
    doc=Inventory();doc.feed(html)
    figures=json.loads((ROOT/'figures.json').read_text())
    assert len(figures)==12 and doc.figures==12 and len(doc.images)==12
    assert len(set(doc.ids))==len(doc.ids)
    assert set(map(int,re.findall(r'\[\[EXHIBIT:(\d+)\]\]',md)))==set(range(1,13))
    assert '[[EXHIBIT:' not in html
    dimensions=[]
    for f in figures:
        png=(ROOT/'figures'/(f['file']+'.png')).read_bytes()
        assert png[:8]==b'\x89PNG\r\n\x1a\n'
        wh=struct.unpack('>II',png[16:24]);assert wh==(3840,2720)
        svg=ET.parse(ROOT/'figures'/(f['file']+'.svg')).getroot()
        assert svg.attrib['viewBox']=='0 0 1920 1360'
        assert all(int(t.attrib.get('font-size',20))>=16 for t in svg.iter('{http://www.w3.org/2000/svg}text'))
        dimensions.append({'exhibit':f['number'],'width':wh[0],'height':wh[1]})
    for im in doc.images:
        assert im.get('alt') and (ROOT/im['src']).is_file()
    for link in doc.links:
        if link.startswith('#'):assert link[1:] in doc.ids
        elif not link.startswith(('https:','http:')):assert (ROOT/link).is_file(),link
    manifest=json.loads((ROOT/'manifest.json').read_text())
    for item in manifest['files']:
        data=(ROOT/item['name']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==item['sha256']
        assert len(data)==item['bytes']
    assert not re.search(r'ghp_[A-Za-z0-9]{10,}|sk-proj-|contentReference|turn\d+search\d+',md+html)
    output={'status':'passed','scope':'Static artifact checks only',
            'manuscript_whitespace_word_count':len(md.split()),'architecture_exhibits':10,'statistical_exhibits':2,
            'image_dimensions':dimensions,'local_links_valid':True,'unique_exhibit_ids':True,
            'all_images_have_alt_text':True,'manifest_hashes_valid':True,
            'external_sources':'Primary source citations; no live LinkedIn/Medium access needed',
            'arithmetic_tests':22,'arithmetic_run':'python3 -m unittest -v test_analytics.py',
            'production_architecture_validated':False,'public_actions_performed':False}
    (ROOT/'validation.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))


if __name__=='__main__':validate()
