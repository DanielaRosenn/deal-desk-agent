"""
Deal Desk Agent - branded slide deck (AgentHack 2026 palette).

Renders 12 on-brand 1920x1080 slides (slide-01..12.png) for the DevPost project
page / PPTX. Concept: "From laptop to production, governed."

Palette: orange #FA4616, ink #11161C, panel #1C232B, blue #2EA8FF, cyan #22D3EE,
amber #FFB020, teal #2BD9A6, violet #B794F6, slate text #C9D3DD.

Run:  python build_deck.py
"""

from __future__ import annotations

import os
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH_PNG = os.path.join(HERE, "..", "code-graph", "deal-desk-code-graph.png")

# palette
INK = "#11161C"
PANEL = "#1C232B"
PANEL2 = "#161C23"
ORANGE = "#FA4616"
BLUE = "#2EA8FF"
CYAN = "#22D3EE"
AMBER = "#FFB020"
TEAL = "#2BD9A6"
VIOLET = "#B794F6"
WHITE = "#F5F8FB"
SLATE = "#C9D3DD"
MUTED = "#8A97A4"

W, H = 16.0, 9.0  # 16:9 coordinate space


def new_slide():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.set_facecolor(INK)
    return fig, ax


def chrome(ax, n, kicker="TRACK 2 · UIPATH MAESTRO BPMN"):
    # top kicker with orange mark
    ax.add_patch(Rectangle((1.0, 8.5), 0.26, 0.26, color=ORANGE, zorder=5))
    ax.text(1.4, 8.63, "UiPath AgentHack 2026", ha="left", va="center",
            fontsize=15, color=WHITE, fontweight="bold", zorder=5)
    ax.text(14.95, 8.63, kicker, ha="right", va="center", fontsize=12.5,
            color=ORANGE, fontweight="bold", zorder=5)
    # footer
    ax.add_patch(Rectangle((0, 0), W, 0.06, color="#222A33", zorder=4))
    ax.text(1.0, 0.42, "Deal Desk Agent  -  from laptop to production, governed",
            ha="left", va="center", fontsize=11, color=MUTED, zorder=5)
    ax.add_patch(FancyBboxPatch((14.5, 0.2), 0.95, 0.44,
                 boxstyle="round,pad=0.02,rounding_size=0.22", linewidth=0,
                 facecolor=ORANGE, zorder=5))
    ax.text(14.97, 0.42, f"{n:02d}/12", ha="center", va="center", fontsize=11.5,
            color=INK, fontweight="bold", zorder=6)


def title(ax, text, y=7.55, color=WHITE, fs=33):
    ax.text(1.0, y, text, ha="left", va="top", fontsize=fs, color=color,
            fontweight="bold", zorder=5, linespacing=1.05)
    ax.add_patch(Rectangle((1.02, y - 1.02), 2.7, 0.07, color=ORANGE, zorder=5))


def subtitle(ax, text, y=6.35, color=BLUE, fs=18):
    ax.text(1.0, y, text, ha="left", va="top", fontsize=fs, color=color,
            fontweight="bold", zorder=5)


def bullets(ax, items, x=1.05, y_top=5.7, fs=17, width=70, lh=0.42, gap=0.34,
            marker=ORANGE, color=SLATE):
    y = y_top
    for it in items:
        wrapped = textwrap.wrap(it, width) or [""]
        ax.add_patch(Rectangle((x, y - 0.2), 0.16, 0.16, color=marker, zorder=6))
        ax.text(x + 0.42, y, "\n".join(wrapped), ha="left", va="top", fontsize=fs,
                color=color, linespacing=1.32, zorder=6)
        y -= len(wrapped) * lh + gap
    return y


def panel(ax, x0, y0, w, h, accent=ORANGE, fill=PANEL):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                 boxstyle="round,pad=0.04,rounding_size=0.18", linewidth=1.6,
                 edgecolor=accent, facecolor=fill, zorder=4))


def card(ax, x0, y0, w, h, head, lines, accent):
    panel(ax, x0, y0, w, h, accent=accent, fill=PANEL)
    ax.add_patch(Rectangle((x0 + 0.0, y0 + h - 0.12), w, 0.12, color=accent, zorder=5))
    ax.text(x0 + 0.35, y0 + h - 0.55, head, ha="left", va="top", fontsize=16.5,
            color=WHITE, fontweight="bold", zorder=6)
    y = y0 + h - 1.25
    for ln in lines:
        for wln in (textwrap.wrap(ln, 30) or [""]):
            ax.text(x0 + 0.35, y, wln, ha="left", va="top", fontsize=12.5,
                    color=SLATE, zorder=6, linespacing=1.25)
            y -= 0.42
        y -= 0.1


def save(fig, n):
    out = os.path.join(HERE, f"slide-{n:02d}.png")
    fig.savefig(out, facecolor=INK)
    plt.close(fig)
    return out


# --------------------------------------------------------------- slides ----
def slide_01():
    fig, ax = new_slide()
    chrome(ax, 1)
    ax.add_patch(Rectangle((1.0, 5.55), 2.4, 0.09, color=ORANGE, zorder=5))
    ax.text(1.0, 5.0, "Deal Desk Agent", ha="left", va="center", fontsize=62,
            color=WHITE, fontweight="bold", zorder=5)
    ax.text(1.0, 3.95, "From laptop to production - governed.", ha="left",
            va="center", fontsize=27, color=ORANGE, fontweight="bold", zorder=5)
    ax.text(1.0, 3.05, "An autonomous pricing-approval agent on UiPath Maestro BPMN.",
            ha="left", va="center", fontsize=18, color=SLATE, zorder=5)
    for i, (txt, c) in enumerate([
        ("Track 2: Maestro BPMN", ORANGE),
        ("Built with coding agents (Cursor + Claude)", BLUE),
        ("Runs on Automation Cloud", TEAL),
    ]):
        x = 1.0 + i * 4.7
        ax.add_patch(FancyBboxPatch((x, 1.7), 4.4, 0.7,
                     boxstyle="round,pad=0.04,rounding_size=0.2", linewidth=1.6,
                     edgecolor=c, facecolor=PANEL, zorder=5))
        ax.text(x + 0.3, 2.05, txt, ha="left", va="center", fontsize=14.5,
                color=WHITE, fontweight="bold", zorder=6)
    return save(fig, 1)


def slide_02():
    fig, ax = new_slide()
    chrome(ax, 2)
    title(ax, "Pricing approvals: 100% human-touched,\nmostly for nothing")
    bullets(ax, [
        "Every discount / renewal change is routed to a human - even the trivial ones",
        "Approval thresholds live in people's heads and drift between managers",
        "No SLA, so deals stall in inboxes; no audit trail, so compliance is guesswork",
    ], y_top=5.3, fs=19, gap=0.5)
    for i, (k, v, c) in enumerate([
        ("Slow", "inbox ping-pong", ORANGE),
        ("Inconsistent", "tribal thresholds", AMBER),
        ("Invisible", "no audit trail", VIOLET),
    ]):
        x = 1.0 + i * 4.7
        panel(ax, x, 1.0, 4.4, 1.7, accent=c)
        ax.text(x + 0.35, 2.25, k, ha="left", va="center", fontsize=19,
                color=WHITE, fontweight="bold", zorder=6)
        ax.text(x + 0.35, 1.6, v, ha="left", va="center", fontsize=13.5,
                color=SLATE, zorder=6)
    return save(fig, 2)


def slide_03():
    fig, ax = new_slide()
    chrome(ax, 3)
    title(ax, "An agent for judgment.\nMaestro for the lifecycle.")
    card(ax, 1.0, 1.2, 6.7, 4.2, "AGENT  (LangGraph)", [
        "Decides WHAT should happen",
        "Disposition + risk score",
        "Recommendation + rationale",
        "Sizes the approver chain as data",
    ], BLUE)
    card(ax, 8.3, 1.2, 6.7, 4.2, "MAESTRO BPMN", [
        "Runs HOW it happens",
        "Cards, human gate, SLA timer",
        "Iterates the agent's chain",
        "Audit on every path",
    ], ORANGE)
    ax.text(8.0, 3.3, "->", ha="center", va="center", fontsize=30,
            color=MUTED, fontweight="bold", zorder=7)
    return save(fig, 3)


def slide_04():
    fig, ax = new_slide()
    chrome(ax, 4)
    title(ax, "The agent: a Python LangGraph\ncoded agent, 3 entry points")
    for i, (k, v, c) in enumerate([
        ("plan", "score · disposition · draft · size chain", BLUE),
        ("render", "contextual Outlook Adaptive Card", CYAN),
        ("process_response", "interpret reply · decide next action", VIOLET),
    ]):
        y = 5.05 - i * 0.95
        ax.add_patch(FancyBboxPatch((1.0, y), 3.6, 0.7,
                     boxstyle="round,pad=0.04,rounding_size=0.16", linewidth=1.6,
                     edgecolor=c, facecolor=PANEL, zorder=5))
        ax.text(1.25, y + 0.35, k, ha="left", va="center", fontsize=15,
                color=WHITE, fontweight="bold", zorder=6)
        ax.text(4.9, y + 0.35, v, ha="left", va="center", fontsize=14, color=SLATE, zorder=6)
    panel(ax, 1.0, 1.0, 14.0, 1.55, accent=AMBER, fill=PANEL2)
    ax.text(1.3, 2.25, "Decision logic (from code)", ha="left", va="top",
            fontsize=13.5, color=AMBER, fontweight="bold", zorder=6)
    ax.text(1.3, 1.78,
            "risk = min(1.0, 0.5·discount/25% + 0.5·value/$500k)\n"
            "auto_clear: <=5% AND <=$50k   |   >25% adds Director+VP   |   "
            ">$500k adds CFO   |   bad payload -> exception",
            ha="left", va="top", fontsize=12, color=SLATE,
            family="monospace", linespacing=1.5, zorder=6, parse_math=False)
    return save(fig, 4)


def slide_05():
    fig, ax = new_slide()
    chrome(ax, 5)
    title(ax, "One Maestro BPMN process -\nthe right actor for each step")
    steps = [
        ("Start", "opportunity change", MUTED),
        ("Agent plan", "disposition + chain", BLUE),
        ("Gateway", "auto_clear / exception / approve", AMBER),
        ("Multi-instance", "render -> card -> task -> route", ORANGE),
        ("SLA timer", "reminder + escalate", VIOLET),
        ("Data Fabric", "audit every path", TEAL),
    ]
    x = 1.0
    for i, (k, v, c) in enumerate(steps):
        w = 2.25
        panel(ax, x, 3.4, w, 1.9, accent=c)
        ax.text(x + w / 2, 4.75, k, ha="center", va="center", fontsize=13.5,
                color=WHITE, fontweight="bold", zorder=6)
        for j, wln in enumerate(textwrap.wrap(v, 16)):
            ax.text(x + w / 2, 4.25 - j * 0.38, wln, ha="center", va="center",
                    fontsize=10.8, color=SLATE, zorder=6)
        if i < len(steps) - 1:
            ax.text(x + w + 0.04, 4.35, ">", ha="center", va="center", fontsize=17,
                    color=MUTED, fontweight="bold", zorder=6)
        x += w + 0.13
    bullets(ax, [
        "Sequential multi-instance subprocess iterates the agent-produced approver chain - "
        "1 manager or a 4-tier CFO deal, no branch explosion",
        "Boundary SLA timer escalates; requester is notified; Data Fabric logs every outcome",
    ], y_top=2.6, fs=15.5, gap=0.4)
    return save(fig, 5)


def slide_06():
    fig, ax = new_slide()
    chrome(ax, 6)
    title(ax, "The whole flow - explore it", y=7.55)
    if os.path.exists(GRAPH_PNG):
        img = Image.open(GRAPH_PNG)
        iax = fig.add_axes([0.06, 0.05, 0.88, 0.62])
        iax.imshow(img)
        iax.axis("off")
    ax.text(1.0, 6.35, "Salesforce + HiBob -> LangGraph agent -> Maestro BPMN -> "
            "Outlook / Action Center / Azure bridge / Data Fabric",
            ha="left", va="top", fontsize=14.5, color=SLATE, zorder=5)
    return save(fig, 6)


def slide_07():
    fig, ax = new_slide()
    chrome(ax, 7)
    title(ax, "Three paths, one process -\ndecided by the agent")
    cards = [
        ("1  Auto-clear", ["<=5% / <=$50k", "zero cards", "logged & closed"], TEAL),
        ("2  One manager", ["8% / $40k", "one Outlook card", "Approve -> done"], BLUE),
        ("3  Multi-tier", ["30% / $1.2M", "mgr -> dir -> VP", "-> CFO, in order"], ORANGE),
    ]
    for i, (h, lines, c) in enumerate(cards):
        x = 1.0 + i * 4.75
        card(ax, x, 1.4, 4.5, 3.9, h, lines, c)
    return save(fig, 7)


def slide_08():
    fig, ax = new_slide()
    chrome(ax, 8, kicker="BONUS · UIPATH FOR CODING AGENTS")
    title(ax, "Built by coding agents")
    subtitle(ax, "Natural language  ->  coding agents  ->  governed cloud process", y=6.4,
             color=ORANGE)
    flow = [("Prompts\n(laptop)", MUTED), ("Cursor + Claude\n+ uip skills", BLUE),
            ("Agent · BPMN ·\nbindings · DF", VIOLET), ("Automation\nCloud", TEAL)]
    x = 1.0
    for i, (k, c) in enumerate(flow):
        w = 3.2
        panel(ax, x, 4.55, w, 1.45, accent=c)
        ax.text(x + w / 2, 5.27, k, ha="center", va="center", fontsize=14,
                color=WHITE, fontweight="bold", zorder=6, linespacing=1.2)
        if i < len(flow) - 1:
            ax.text(x + w + 0.05, 5.27, ">", ha="center", va="center", fontsize=20,
                    color=ORANGE, fontweight="bold", zorder=6)
        x += w + 0.42
    bullets(ax, [
        "Coding agents generated/edited the LangGraph agent, the BPMN, bindings, "
        "schema exports, and the Data Fabric entity",
        "Low-code Maestro + pro-code agent combined - the combination UiPath flagged as "
        "especially interesting",
        "This IS the laptop -> production bridge: prompts became a deployed, governed process",
    ], y_top=3.85, fs=15.5, gap=0.38)
    return save(fig, 8)


def slide_09():
    fig, ax = new_slide()
    chrome(ax, 9)
    title(ax, "Governance & human-in-the-loop")
    cards = [
        ("Human gate", ["Action Center task", "Azure bridge resumes", "the instance"], VIOLET),
        ("Time governance", ["Boundary SLA timer", "reminder +", "escalation"], AMBER),
        ("Audit", ["Data Fabric logs", "agent rec vs.", "human decision"], TEAL),
        ("Guardrails", ["bad payload ->", "exception; empty", "chain -> fallback"], ORANGE),
    ]
    for i, (h, lines, c) in enumerate(cards):
        x = 1.0 + i * 3.55
        card(ax, x, 1.4, 3.35, 3.9, h, lines, c)
    return save(fig, 9)


def slide_10():
    fig, ax = new_slide()
    chrome(ax, 10)
    title(ax, "Runs on Automation Cloud -\nnot a laptop demo")
    bullets(ax, [
        "Coded agent published to the tenant feed; 3 entry points deployed as runnable processes",
        "BPMN validated (UiPath extensions + full diagram DI); live Outlook connection bound",
        "Full solution packaged as a deployable .uipx (agent + BPMN + Data Fabric ApprovalAudit)",
        "Unit tests passing: disposition, auto-clear, multi-tier, schema, guardrails, rendering",
    ], y_top=5.5, fs=18, gap=0.55)
    ax.text(1.0, 1.05, "UiPath is the orchestration + governance layer that ties it together.",
            ha="left", va="center", fontsize=15, color=ORANGE, fontweight="bold", zorder=5)
    return save(fig, 10)


def slide_11():
    fig, ax = new_slide()
    chrome(ax, 11)
    title(ax, "Business impact & reach")
    cards = [
        ("Deflection", ["low-risk deals", "clear with zero", "human touch"], TEAL),
        ("Speed + consistency", ["SLA + routing", "replace inbox", "ping-pong"], BLUE),
        ("Auditability", ["every decision", "logged for compliance", "& tuning"], VIOLET),
        ("Portable", ["invoice · expense ·", "onboarding", "(Track 2 examples)"], ORANGE),
    ]
    for i, (h, lines, c) in enumerate(cards):
        x = 1.0 + i * 3.55
        card(ax, x, 1.4, 3.35, 3.9, h, lines, c)
    return save(fig, 11)


def slide_12():
    fig, ax = new_slide()
    chrome(ax, 12)
    ax.add_patch(Rectangle((1.0, 5.65), 2.4, 0.09, color=ORANGE, zorder=5))
    ax.text(1.0, 5.05, "Decide. Draft. Route. Audit.", ha="left", va="center",
            fontsize=44, color=WHITE, fontweight="bold", zorder=5)
    ax.text(1.0, 4.15, "Autonomously - and shipped to production.", ha="left",
            va="center", fontsize=24, color=ORANGE, fontweight="bold", zorder=5)
    ax.text(1.0, 3.3, "Agent owns the judgment  ·  Maestro owns the lifecycle  ·  "
            "UiPath owns governance", ha="left", va="center", fontsize=16,
            color=SLATE, zorder=5)
    for i, (k, v) in enumerate([("DevPost", "<link>"), ("Demo video", "<link>"),
                                 ("Code", "<link>")]):
        x = 1.0 + i * 4.7
        panel(ax, x, 1.4, 4.4, 1.1, accent=BLUE)
        ax.text(x + 0.3, 2.15, k, ha="left", va="center", fontsize=15,
                color=WHITE, fontweight="bold", zorder=6)
        ax.text(x + 0.3, 1.7, v, ha="left", va="center", fontsize=13, color=CYAN, zorder=6)
    return save(fig, 12)


def build():
    fns = [slide_01, slide_02, slide_03, slide_04, slide_05, slide_06,
           slide_07, slide_08, slide_09, slide_10, slide_11, slide_12]
    for fn in fns:
        print(fn())


if __name__ == "__main__":
    build()
