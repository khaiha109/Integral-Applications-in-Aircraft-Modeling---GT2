import re
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from omml import latex_to_omml
def f(x,n=2): return f"{x:,.{n}f}".replace(",","X").replace(".",",").replace("X"," ")
class Doc:
    def __init__(s):
        d=s.d=Document(); sec=d.sections[0]; sec.page_width=Cm(21); sec.page_height=Cm(29.7)
        sec.left_margin=Cm(3); sec.right_margin=Cm(2); sec.top_margin=Cm(2); sec.bottom_margin=Cm(2)
        st=d.styles["Normal"]; st.font.name="Times New Roman"; st.font.size=Pt(13); st.font.color.rgb=RGBColor(0,0,0)
        st.element.rPr.rFonts.set(qn("w:eastAsia"),"Times New Roman")
        st.paragraph_format.space_after=Pt(4); st.paragraph_format.line_spacing=1.2
        zoom=d.settings.element.find(qn("w:zoom"))
        if zoom is not None: zoom.set(qn("w:percent"),"100")
    def _runs(s,p,t,bold=False):
        # markup: _{sub} ^{sup} **bold**; dùng gạch nối thường thay cho gạch dài
        t=t.replace("—","-").replace("–","-").replace("−","-")
        for tok in re.split(r"(_\{[^}]*\}|\^\{[^}]*\}|\*\*[^*]+\*\*)",t):
            if not tok: continue
            if tok.startswith("_{"): r=p.add_run(tok[2:-1]); r.font.subscript=True; r.bold=bold
            elif tok.startswith("^{"): r=p.add_run(tok[2:-1]); r.font.superscript=True; r.bold=bold
            elif tok.startswith("**"): r=p.add_run(tok[2:-2]); r.bold=True
            else: r=p.add_run(tok); r.bold=bold
            r.font.name="Times New Roman"; r.font.size=Pt(13); r.font.color.rgb=RGBColor(0,0,0)
    def para(s,t,bold=False,center=False,justify=True,indent=True):
        p=s.d.add_paragraph(); s._runs(p,t,bold)
        if center: p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        elif justify: p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        if indent and not center and not bold: p.paragraph_format.first_line_indent=Cm(1)
        return p
    def H(s,t,center=False):
        p=s.para(t,bold=True,center=center); p.paragraph_format.space_before=Pt(10); p.paragraph_format.keep_with_next=True; p.alignment=WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    def eq(s,t,num=None):
        p=s.d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; s._runs(p,t+("     ("+num+")" if num else ""))
        p.paragraph_format.space_before=Pt(2); p.paragraph_format.space_after=Pt(6)
    def tex(s,latex,num=None):
        """Real Word equation object (OMML), centered, with the equation
        number right-aligned on the same line (classic report layout):
        [tab] equation [tab] (num)"""
        p=s.d.add_paragraph()
        pf=p.paragraph_format; pf.space_before=Pt(4); pf.space_after=Pt(8)
        pf.tab_stops.add_tab_stop(Cm(8.0),WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Cm(16.0),WD_TAB_ALIGNMENT.RIGHT)
        p.add_run("\t")
        el=latex_to_omml(latex,display=False)
        p._p.append(el)
        if num:
            r=p.add_run("\t("+num+")")
            r.font.name="Times New Roman"; r.font.size=Pt(13); r.font.color.rgb=RGBColor(0,0,0)
    def bullet(s,t):
        p=s.d.add_paragraph(); s._runs(p,"- "+t); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent=Cm(0.8); p.paragraph_format.first_line_indent=Cm(-0.5)
    def cap(s,t):
        p=s.para(t,bold=True,center=True); p.paragraph_format.keep_with_next=True
    def img(s,path,w=15,caption=None):
        p=s.d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(path,width=Cm(w)); p.paragraph_format.keep_with_next=True
        if caption: c=s.para(caption,center=True); c.paragraph_format.space_after=Pt(8)
    def table(s,head,rows,widths,cap=None):
        if cap: s.cap(cap)
        t=s.d.add_table(rows=1,cols=len(head)); t.style="Table Grid"; t.autofit=False
        sc=16.0/sum(widths); widths=[w*sc for w in widths]
        for i,gc in enumerate(t._tbl.tblGrid.findall(qn("w:gridCol"))): gc.set(qn("w:w"),str(int(widths[i]*567)))
        for i,h in enumerate(head): c=t.rows[0].cells[i]; c.text=""; s._runs(c.paragraphs[0],h,True)
        for row in rows:
            cs=t.add_row().cells
            for i,v in enumerate(row): cs[i].text=""; s._runs(cs[i].paragraphs[0],str(v))
        for row in t.rows:
            for i,c in enumerate(row.cells):
                c.width=Cm(widths[i])
                for p in c.paragraphs: p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.0
        s.d.add_paragraph()
    def save(s,p): s.d.save(p)
