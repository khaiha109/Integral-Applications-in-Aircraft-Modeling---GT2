"""LaTeX -> OOXML (OMML) equation helper, via pandoc, with a fix for a known
pandoc docx-writer bug (wrong child order inside <m:dPr>)."""
import subprocess, tempfile, os
from lxml import etree

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
}
W = NS['w']; M = NS['m']
_DPR_ORDER = ['begChr', 'sepChr', 'endChr', 'grow', 'shp', 'ctrlPr']

def _fix_dpr_order(root):
    for dpr in root.iter('{%s}dPr' % M):
        children = list(dpr)
        def key(c):
            name = etree.QName(c).localname
            return _DPR_ORDER.index(name) if name in _DPR_ORDER else 99
        children_sorted = sorted(children, key=key)
        for c in children:
            dpr.remove(c)
        for c in children_sorted:
            dpr.append(c)

def _fix_rpr_nor_sty(root):
    # CT_RPR: lit?, (nor? | (scr?, sty?)), brk?, aln?  -- pandoc sometimes
    # emits both <m:nor/> and <m:sty/> together, which is invalid (nor is an
    # alternative to the scr/sty pair, not combinable with sty). Drop the
    # redundant <m:nor/> when <m:sty/> is also present.
    for rpr in root.iter('{%s}rPr' % M):
        nor = rpr.find('{%s}nor' % M)
        sty = rpr.find('{%s}sty' % M)
        if nor is not None and sty is not None:
            rpr.remove(nor)

_CACHE = {}

def latex_to_omml(latex, display=False):
    """Return an lxml <m:oMath> (or <m:oMathPara> for display) element for the
    given LaTeX source, suitable for appending into a python-docx paragraph's
    XML (p._p.append(...))."""
    key = (latex, display)
    if key in _CACHE:
        return etree.fromstring(etree.tostring(_CACHE[key]))
    src = ("$$" + latex + "$$") if display else ("$" + latex + "$")
    with tempfile.TemporaryDirectory() as td:
        mdpath = os.path.join(td, "f.md")
        docxpath = os.path.join(td, "f.docx")
        with open(mdpath, "w", encoding="utf-8") as fh:
            fh.write(src)
        subprocess.run(["pandoc", mdpath, "-o", docxpath], check=True,
                        capture_output=True)
        import zipfile
        with zipfile.ZipFile(docxpath) as z:
            xml = z.read("word/document.xml")
    root = etree.fromstring(xml)
    _fix_dpr_order(root)
    _fix_rpr_nor_sty(root)
    tag = '{%s}oMathPara' % M if display else '{%s}oMath' % M
    el = root.find('.//' + tag)
    if el is None:
        # fall back: wrap any oMath found
        el = root.find('.//{%s}oMath' % M)
    _CACHE[key] = el
    return etree.fromstring(etree.tostring(el))
