#!/usr/bin/env python3
"""Generate Cape Town + Garden Route itinerary as a Word document."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

OUTPUT_PATH = "/Users/David/Library/Mobile Documents/com~apple~CloudDocs/skills/accommodation-finder/cape-town-garden-route-itinerary.docx"


def set_font(run, name="Calibri", size=11, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_hyperlink(paragraph, url, text, font_size=10):
    """Add a clickable hyperlink to a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    new_run = OxmlElement("w:r")

    rPr = OxmlElement("w:rPr")

    rStyle = OxmlElement("w:rStyle")
    rStyle.set(qn("w:val"), "Hyperlink")
    rPr.append(rStyle)

    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Calibri")
    rFonts.set(qn("w:hAnsi"), "Calibri")
    rPr.append(rFonts)

    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(font_size * 2))
    rPr.append(sz)

    new_run.append(rPr)

    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)

    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def set_table_borders(table):
    """Add borders to all cells in a table."""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")

    tblBorders = OxmlElement("w:tblBorders")
    for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "AAAAAA")
        tblBorders.append(border)

    tblPr.append(tblBorders)
    if tbl.tblPr is None:
        tbl.append(tblPr)


def shade_row(row, color="F2F2F2"):
    """Apply background shading to a table row."""
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), color)
        tcPr.append(shd)


def add_section_heading(doc, text, level=1):
    """Add a styled section heading."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    size = 14 if level == 1 else 12
    set_font(run, size=size, bold=True, color=(31, 73, 125))
    return p


def add_bullet(doc, text, indent=0):
    """Add a bullet point paragraph."""
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.25 + indent * 0.25)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_font(run, size=10.5)
    return p


def add_body_text(doc, text, bold=False, size=10.5, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_font(run, size=size, bold=bold)
    return p


def add_day_block(doc, day_label, activities):
    """Add a day header + bullet list."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(day_label)
    set_font(run, size=11, bold=True, color=(0, 112, 192))

    for activity in activities:
        add_bullet(doc, activity)


def build_accommodation_table(doc, headers, rows, link_col=3):
    """Build a bordered accommodation table with hyperlinks in the last column."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT

    # Header row
    hdr_row = table.rows[0]
    shade_row(hdr_row, "1F497D")
    for i, header in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(header)
        set_font(run, size=10, bold=True, color=(255, 255, 255))

    # Data rows
    for idx, row_data in enumerate(rows):
        row = table.add_row()
        if idx % 2 == 0:
            shade_row(row, "EBF3FB")

        for col_idx, cell_data in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]

            if col_idx == link_col and cell_data.startswith("airbnb.com"):
                url = "https://" + cell_data
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                add_hyperlink(p, url, "View listing", font_size=9)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(str(cell_data))
                set_font(run, size=10)

    set_table_borders(table)

    # Column widths
    col_widths = [Cm(1.5), Cm(3.0), Cm(2.5), Cm(2.2), Cm(5.5)]
    for i, width in enumerate(col_widths[:len(headers)]):
        for cell in table.column_cells(i):
            cell.width = width

    return table


def build_budget_table(doc, headers, rows):
    """Build the budget summary table."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT

    hdr_row = table.rows[0]
    shade_row(hdr_row, "1F497D")
    for i, header in enumerate(headers):
        cell = hdr_row.cells[i]
        p = cell.paragraphs[0]
        run = p.add_run(header)
        set_font(run, size=10, bold=True, color=(255, 255, 255))

    for idx, row_data in enumerate(rows):
        row = table.add_row()
        if idx % 2 == 0:
            shade_row(row, "EBF3FB")
        for col_idx, cell_data in enumerate(row_data):
            cell = row.cells[col_idx]
            p = cell.paragraphs[0]
            is_total = "TOTAL" in str(cell_data)
            run = p.add_run(str(cell_data))
            set_font(run, size=10, bold=is_total)

    set_table_borders(table)

    col_widths = [Cm(9.0), Cm(5.5)]
    for i, width in enumerate(col_widths):
        for cell in table.column_cells(i):
            cell.width = width

    return table


# ─────────────────────────────────────────────────────────────────────────────
# Main document construction
# ─────────────────────────────────────────────────────────────────────────────

doc = Document()

# Page margins
section = doc.sections[0]
section.top_margin = Cm(2.0)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# Default style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)

# ── TITLE ────────────────────────────────────────────────────────────────────
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_p.paragraph_format.space_after = Pt(4)
title_run = title_p.add_run("Cape Town + Garden Route")
set_font(title_run, size=20, bold=True, color=(31, 73, 125))

subtitle_p = doc.add_paragraph()
subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle_p.paragraph_format.space_after = Pt(2)
sub_run = subtitle_p.add_run("March 22–29, 2026")
set_font(sub_run, size=14, bold=False, color=(89, 89, 89))

pax_p = doc.add_paragraph()
pax_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
pax_p.paragraph_format.space_after = Pt(16)
pax_run = pax_p.add_run("David, Lobke & Noah")
set_font(pax_run, size=12, bold=True, color=(89, 89, 89))

# Horizontal rule effect via bottom border on a paragraph
hr_p = doc.add_paragraph()
hr_p.paragraph_format.space_after = Pt(12)
pPr = hr_p._p.get_or_add_pPr()
pBdr = OxmlElement("w:pBdr")
bottom = OxmlElement("w:bottom")
bottom.set(qn("w:val"), "single")
bottom.set(qn("w:sz"), "6")
bottom.set(qn("w:space"), "1")
bottom.set(qn("w:color"), "1F497D")
pBdr.append(bottom)
pPr.append(pBdr)

# ── SECTION 1: TRIP OVERVIEW ─────────────────────────────────────────────────
add_section_heading(doc, "1. Trip Overview")

overview_items = [
    "Route: Cape Town → Hermanus → Wilderness → Knysna → Plettenberg Bay → George Airport → fly home",
    "Duration: 8 days / 7 nights",
    "Total driving: ~750 km one-way",
    "Weather: 17–29°C, dry and sunny",
    "Timezone: +1h vs Belgium — no jet lag!",
]
for item in overview_items:
    add_bullet(doc, item)

# ── SECTION 2: FLIGHTS ───────────────────────────────────────────────────────
doc.add_page_break()
add_section_heading(doc, "2. Flights (TBC)")

add_body_text(doc, "Outbound — Saturday 21 March 2026", bold=True, size=11)
add_bullet(doc, "Option A: KLM non-stop AMS → CPT — depart ~11:00, arrive 21:55 — EUR 3,560/pp")
add_bullet(doc, "Option B: Air France non-stop CDG → CPT — depart ~20:xx, arrive Sun 05:50 — EUR 2,750/pp")

p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(6)

add_body_text(doc, "Return — Sunday 29 March 2026", bold=True, size=11)
add_bullet(doc, "CPT → AMS or CDG (matching outbound carrier)")

note_p = doc.add_paragraph()
note_p.paragraph_format.space_after = Pt(4)
note_run = note_p.add_run("Action required: Confirm preferred option and book flights.")
set_font(note_run, size=10.5, bold=True, color=(192, 0, 0))

# ── SECTION 3: DAY-BY-DAY ────────────────────────────────────────────────────
doc.add_page_break()
add_section_heading(doc, "3. Day-by-Day Itinerary")

days = [
    (
        "Day 0 — Sun 22 Mar: ARRIVE CAPE TOWN",
        [
            "Evening arrival from flight",
            "Settle into accommodation",
            "V&A Waterfront walk, dinner at the harbour",
            "Overnight: Cape Town (Night 1 of 2)",
        ],
    ),
    (
        "Day 1 — Mon 23 Mar: CAPE TOWN CITY",
        [
            "Morning: Table Mountain cable car (go early before cloud)",
            "Drive to Simon's Town (45 min)",
            "Boulders Beach — African penguins (best 09:00–10:30)",
            "Lunch in Kalk Bay (harbour, fish & chips)",
            "Afternoon: Kirstenbosch Botanical Garden — Boomslang tree canopy walkway",
            "Evening: Dinner in Cape Town",
            "Overnight: Cape Town (Night 2)",
        ],
    ),
    (
        "Day 2 — Tue 24 Mar: CAPE TOWN → HERMANUS (1.5h drive)",
        [
            "Morning: Pick up rental car",
            "Drive scenic R44 Clarence Drive past Betty's Bay",
            "Stop: Stony Point penguin colony (less crowded, free)",
            "Arrive Hermanus by lunch",
            "Afternoon: Cliff Path walk (short section with Noah)",
            "Whale watching from shore (season tapering but possible)",
            "Overnight: Hermanus",
        ],
    ),
    (
        "Day 3 — Wed 25 Mar: HERMANUS → WILDERNESS (3.5h drive)",
        [
            "Morning: Hermanus beach/harbour",
            "Drive through Swellendam — coffee at historic Drostdy",
            "Optional: Bontebok National Park quick game drive",
            "Afternoon: Arrive Wilderness — beach, lagoon, river mouth",
            "Map of Africa viewpoint",
            "Canoe/paddleboard on Touw River gorge",
            "Overnight: Wilderness",
        ],
    ),
    (
        "Day 4 — Thu 26 Mar: WILDERNESS → KNYSNA (45 min drive)",
        [
            "Morning: Wilderness beach — safe lagoon swimming for Noah",
            "Drive to Knysna",
            "Knysna Heads — dramatic sandstone cliffs",
            "Lunch: Knysna Waterfront — oysters!",
            "Afternoon: Monkeyland primate sanctuary OR Birds of Eden",
            "Knysna Elephant Park — feeding & interaction",
            "Overnight: Knysna",
        ],
    ),
    (
        "Day 5 — Fri 27 Mar: KNYSNA → PLETTENBERG BAY (30 min drive)",
        [
            "Morning: Knysna Forest — Big Tree trail (45 min, pushchair-friendly)",
            "Drive to Plettenberg Bay",
            "Robberg Nature Reserve — short coastal walk (2 km with Noah, seals)",
            "Afternoon: Plettenberg Bay beach (Lentjiesklip — sheltered, family-friendly)",
            "Overnight: Plettenberg Bay (Night 1 of 2)",
        ],
    ),
    (
        "Day 6 — Sat 28 Mar: TSITSIKAMMA + PLETT",
        [
            "Morning: Tsitsikamma National Park — Storms River suspension bridge (1h drive)",
            "Picnic in the park",
            "Afternoon: Return to Plett, beach time or Tenikwa Wildlife Centre",
            "Evening: Final dinner in Plett",
            "Overnight: Plettenberg Bay (Night 2)",
        ],
    ),
    (
        "Day 7 — Sun 29 Mar: FLY HOME",
        [
            "Morning: Drive to George Airport (1h)",
            "Drop rental car at GRJ",
            "FlySafair/Airlink GRJ → CPT (45 min)",
            "Connect to international flight home",
        ],
    ),
]

for day_label, activities in days:
    add_day_block(doc, day_label, activities)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ── SECTION 4: ACCOMMODATION ──────────────────────────────────────────────────
doc.add_page_break()
add_section_heading(doc, "4. Accommodation Options")

acc_headers = ["Code", "Price", "Rating", "Reviews", "Airbnb Link"]

# Cape Town
add_body_text(doc, "Cape Town — 2 nights (Sun–Mon, 22–23 Mar)", bold=True, size=11, space_after=4)
ct_rows = [
    ["CT1", "EUR 161", "4.80/5", "182", "airbnb.com/rooms/741981929609404169"],
    ["CT2", "EUR 300", "4.85/5", "68",  "airbnb.com/rooms/961364437444227337"],
    ["CT3", "EUR 412", "4.86/5", "250", "airbnb.com/rooms/49434290"],
    ["CT4", "EUR 585", "4.93/5", "30",  "airbnb.com/rooms/30052127"],
    ["CT5", "EUR 763", "4.97/5", "149", "airbnb.com/rooms/29322407"],
]
build_accommodation_table(doc, acc_headers, ct_rows, link_col=4)
doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Hermanus
add_body_text(doc, "Hermanus — 1 night (Tue 24 Mar)", bold=True, size=11, space_after=4)
h_rows = [
    ["H1", "EUR 66",  "4.74/5", "95",  "airbnb.com/rooms/19394802"],
    ["H2", "EUR 99",  "4.70/5", "322", "airbnb.com/rooms/16969612"],
    ["H3", "EUR 149", "4.75/5", "71",  "airbnb.com/rooms/4613329"],
    ["H4", "EUR 175", "4.89/5", "122", "airbnb.com/rooms/54119606"],
]
build_accommodation_table(doc, acc_headers, h_rows, link_col=4)
doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Wilderness
add_body_text(doc, "Wilderness — 1 night (Wed 25 Mar)", bold=True, size=11, space_after=4)
w_rows = [
    ["W1", "EUR 60",  "4.77/5", "47",  "airbnb.com/rooms/53285108"],
    ["W2", "EUR 115", "4.84/5", "56",  "airbnb.com/rooms/29875214"],
    ["W3", "EUR 116", "4.71/5", "21",  "airbnb.com/rooms/35123446"],
    ["W4", "EUR 235", "4.91/5", "241", "airbnb.com/rooms/29300468"],
]
build_accommodation_table(doc, acc_headers, w_rows, link_col=4)
doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Knysna
add_body_text(doc, "Knysna — 1 night (Thu 26 Mar)", bold=True, size=11, space_after=4)
k_rows = [
    ["K1", "EUR 43",  "4.86/5", "127", "airbnb.com/rooms/33789619"],
    ["K2", "EUR 50",  "4.91/5", "570", "airbnb.com/rooms/21745934"],
    ["K3", "EUR 71",  "4.89/5", "9",   "airbnb.com/rooms/39592919"],
    ["K4", "EUR 288", "4.90/5", "243", "airbnb.com/rooms/5972847"],
]
build_accommodation_table(doc, acc_headers, k_rows, link_col=4)
doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Plettenberg Bay
add_body_text(doc, "Plettenberg Bay — 2 nights (Fri–Sat 27–28 Mar)", bold=True, size=11, space_after=4)
p_rows = [
    ["P1", "EUR 125", "4.97/5", "429", "airbnb.com/rooms/4478230"],
    ["P2", "EUR 142", "4.81/5", "91",  "airbnb.com/rooms/20968700"],
    ["P3", "EUR 194", "4.65/5", "257", "airbnb.com/rooms/11540007"],
    ["P4", "EUR 305", "4.96/5", "321", "airbnb.com/rooms/27800381"],
]
build_accommodation_table(doc, acc_headers, p_rows, link_col=4)

# ── SECTION 5: BUDGET ────────────────────────────────────────────────────────
doc.add_page_break()
add_section_heading(doc, "5. Budget Estimate (3 passengers)")

budget_headers = ["Item", "Estimate"]
budget_rows = [
    ["Flights (AMS or CDG → CPT, return)", "EUR 8,250 – 10,700"],
    ["Accommodation (7 nights)", "~EUR 800"],
    ["Car rental (6 days, one-way CPT → GRJ)", "~EUR 350"],
    ["Domestic flight GRJ → CPT", "~EUR 200"],
    ["Fuel", "~EUR 80"],
    ["Food & activities", "~EUR 700"],
    ["TOTAL", "~EUR 10,400 – 12,000"],
]
build_budget_table(doc, budget_headers, budget_rows)

# ── SECTION 6: LOGISTICS ─────────────────────────────────────────────────────
add_section_heading(doc, "6. Logistics")

logistics = [
    "Car rental: Pick up Cape Town Airport Tue 24 Mar, drop off George Airport (GRJ) Sun 29 Mar — 6 days. Avis, Hertz, and Europcar all offer one-way rentals on this route.",
    "Child seat: Book car seat with rental at time of reservation — fills up fast.",
    "Vehicle: SUV recommended (comfort + luggage capacity).",
    "Driving: Left-hand side; well-maintained N2 highway throughout.",
    "GRJ → CPT domestic flight: FlySafair or Airlink, 45 min, ~EUR 50–80/pp.",
]
for item in logistics:
    add_bullet(doc, item)

# ── SECTION 7: NOAH HIGHLIGHTS ───────────────────────────────────────────────
add_section_heading(doc, "7. Noah Highlights")

noah_items = [
    "Boulders Beach penguins — African penguin colony (Day 1)",
    "Monkeyland primate sanctuary — walk-through forest with primates (Day 4)",
    "Knysna Elephant Park — feeding and close-up interaction (Day 4)",
    "Tsitsikamma suspension bridge — above the river gorge (Day 6)",
    "Wilderness beach lagoon — safe, shallow swimming (Days 3–4)",
    "Birds of Eden — one of the world's largest free-flight aviaries (Day 4)",
    "Robberg Nature Reserve — seals on the rocks (Day 5)",
]
for i, item in enumerate(noah_items, 1):
    add_bullet(doc, f"{i}. {item}")

# Final save
doc.save(OUTPUT_PATH)
print(f"Document saved: {OUTPUT_PATH}")
