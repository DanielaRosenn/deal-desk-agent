"""
Deal Desk Agent - Code Graph (Maestro BPMN + LangGraph agent).

Renders an animated drill-down GIF of the production topology:
Salesforce (live IS + AgentHub MCP sidecar) + HiBob (org chart) ->
Coded Agent (LangGraph: plan / render / process_response) ->
Maestro BPMN orchestration ->
WaitDecision Robot (RPA) -> Outlook HTML email -> AWS HITL Portal ->
Slack DM + Data Fabric audit.

Accurate architecture (v1.2.3, June 2026):
- Approval delivery: Outlook HTML email with portal link (not Adaptive Card)
- Human decision channel: AWS HITL Portal (CloudFront) (not Action Center)
- Robot: WaitDecision UiPath Robot (RPA) (not Azure Function)
- Salesforce: live IS + AgentHub MCP sidecar
- Notification: Slack DM to requester after outcome

Outputs (next to this file):
  - deal-desk-flow.gif   (animated drill-down, <5 MB for the AgentHack gallery)
  - deal-desk-code-graph.png  (crisp static of the full graph)

Run:  python deal_desk_code_graph.py
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette ----
# AgentHack 2026 dark palette: orange #FA4616, ink #11161C, blue #2EA8FF,
# cyan #22D3EE, amber #FFB020, teal #2BD9A6, violet #B794F6.
PALETTE = {
    # type:        (fill,      stroke,    text)
    "external": ("#1C232B", "#7C8A99", "#C9D3DD"),
    "agent": ("#15212E", "#2EA8FF", "#BFE3FF"),
    "bpmn": ("#241405", "#FA4616", "#FFD2C2"),
    "decision": ("#241F0C", "#FFB020", "#FFE3A6"),
    "human": ("#211A2E", "#B794F6", "#E4D7FF"),
    "data": ("#1C232B", "#7C8A99", "#C9D3DD"),
    "endok": ("#0F2A21", "#2BD9A6", "#A8F0D6"),
    "live": ("#0F2630", "#22D3EE", "#BDF1FB"),
}
BG = "#11161C"
EDGE_COLOR = "#566472"


# ------------------------------------------------------------------ model ----
@dataclass
class Node:
    id: str
    x: float
    y: float
    w: float
    h: float
    label: str
    type: str
    tag: str = ""


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""
    rad: float = 0.0
    dashed: bool = False
    lt: float = 0.5  # label position along the edge (0=src, 1=dst)
    lx: float = 0.0  # extra label x offset
    ly: float = 0.0  # extra label y offset


@dataclass
class Cluster:
    x0: float
    y0: float
    x1: float
    y1: float
    title: str
    color: str


CLUSTERS = [
    Cluster(2.5, 49, 24, 97, "SOURCE SYSTEMS  (production)", "#7C8A99"),
    Cluster(27, 23, 50, 97, "CODED AGENT  -  LangGraph", "#2EA8FF"),
    Cluster(53, 5, 78, 97, "MAESTRO BPMN  orchestration", "#FA4616"),
    Cluster(81, 4, 98.5, 97, "DELIVERY CHANNELS  (live)", "#22D3EE"),
]

NODES = {
    # source systems
    "sf": Node("sf", 13.2, 82, 17, 12, "Salesforce\nOpportunity change", "external", "live IS + AgentHub MCP"),
    "hibob": Node("hibob", 13.2, 62, 17, 11, "HiBob\nOrg chart", "external", "mocked in demo"),
    # coded agent (langgraph)
    "plan": Node("plan", 38.5, 82, 18, 13, "plan\nevaluate | risk score\nLLM rationale | chain", "agent"),
    "render": Node("render", 38.5, 58, 18, 11, "render\nAdaptive Card payload", "agent"),
    "proc": Node("proc", 38.5, 36, 18, 12, "process_response\ninterpret decisions", "agent"),
    # maestro bpmn
    "start": Node("start", 65.5, 89, 17, 9, "Start\nopportunity change", "external"),
    "gw": Node("gw", 65.5, 75, 17, 9, "Disposition\ngateway", "decision"),
    "mi": Node("mi", 65.5, 59, 19, 13, "Multi-instance\nsubprocess\n(per approver)", "bpmn"),
    "sla": Node("sla", 65.5, 41, 17, 9, "Boundary\nSLA timer", "human"),
    "dfins": Node("dfins", 65.5, 26, 17, 9, "Data Fabric\ninsert (audit)", "data"),
    "end": Node("end", 65.5, 12, 16, 8, "End\noutcome", "endok"),
    # delivery channels — three simultaneous (accurate v1.3.16)
    "robot": Node("robot", 89.5, 82, 16, 12, "WaitDecision\nRobot  (RPA)", "bpmn", "v1.3.16  Persistence"),
    "ac": Node("ac", 89.5, 65, 16, 11, "Action Center\nexternal task\n(Deal Desk catalog)", "human"),
    "outlook": Node("outlook", 89.5, 49, 16, 11, "Outlook\nAdaptive Card\n(originator 61fed71d)", "live"),
    "slack_a": Node("slack_a", 89.5, 33, 16, 10, "Slack\nBlock Kit DM\n(to approver)", "live"),
    "slack_r": Node("slack_r", 89.5, 18, 16, 9, "Slack + Outlook\nsummary to AE", "live"),
    "dfdb": Node("dfdb", 89.5, 8, 16, 8, "Data Fabric\nApprovalAudit", "data"),
}

EDGES = [
    # trigger
    Edge("sf", "start", "opportunity change", lt=0.78),
    # plan
    Edge("start", "plan", "invoke plan agent", rad=-0.15),
    Edge("hibob", "plan", "org chart", rad=0.18, dashed=True, lt=0.7),
    Edge("plan", "gw", "disposition + chain", rad=-0.12),
    # gateway branches
    Edge("gw", "mi", "needs_approval"),
    Edge("gw", "dfins", "auto_approve / exception", rad=-0.52, lt=0.5, lx=-13.0),
    # per-approver loop
    Edge("mi", "render", "per approver", rad=0.25),
    Edge("render", "robot", "card payload", rad=-0.15, lt=0.7),
    # robot → three channels
    Edge("robot", "ac", "CreateExternalTask", lt=0.5),
    Edge("robot", "outlook", "send Adaptive Card", rad=-0.22, lt=0.55),
    Edge("robot", "slack_a", "Slack Block Kit DM", rad=-0.35, lt=0.55),
    # wait and return
    Edge("ac", "robot", "decision (Persistence)", rad=0.42, dashed=True, lt=0.45),
    Edge("outlook", "robot", "button click (Action.Http)", rad=0.38, dashed=True, lt=0.5),
    Edge("robot", "proc", "out_Decision returned", rad=0.28, lt=0.42, ly=1.0),
    Edge("proc", "mi", "next approver", rad=0.32),
    Edge("proc", "dfins", "approved / rejected", rad=-0.35),
    # SLA
    Edge("sla", "robot", "reminder", rad=0.38, dashed=True, lt=0.5),
    # close
    Edge("proc", "slack_r", "notify requester", rad=-0.32, lt=0.6, lx=1.5),
    Edge("dfins", "dfdb", "write record"),
    Edge("dfins", "end", "close"),
]

# drill-down narrative: each step reveals nodes/edges + a caption
STEPS = [
    (["sf", "start"], ["sf>start"], "1  Salesforce opportunity change starts the Maestro process"),
    (["plan"], ["start>plan"], "2  Maestro invokes the plan agent (LangGraph)"),
    (["hibob"], ["hibob>plan"], "3  Agent resolves approver chain from HiBob org chart"),
    (["gw"], ["plan>gw"], "4  Agent returns disposition + risk score + LLM rationale + chain"),
    (["dfins", "dfdb", "end"], ["gw>dfins", "dfins>dfdb", "dfins>end"],
     "5  Auto-approve / exception -> audit directly (zero human touch)"),
    (["mi"], ["gw>mi"], "6  needs_approval -> per-approver sequential loop"),
    (["render"], ["mi>render"],
     "7  render agent builds Adaptive Card payload with deal data + LLM recommendation"),
    (["robot"], ["render>robot"],
     "8  WaitDecision Robot receives card payload (UiPath RPA v1.3.16)"),
    (["ac"], ["robot>ac"],
     "9  Robot creates Action Center external task (Deal Desk catalog, Approve / Reject)"),
    (["outlook"], ["robot>outlook"],
     "10  Robot sends Outlook Adaptive Card (originator 61fed71d, three action buttons)"),
    (["slack_a"], ["robot>slack_a"],
     "11  Robot sends Slack Block Kit DM to approver simultaneously"),
    ([], ["ac>robot", "outlook>robot"],
     "12  Robot suspends via UiPath Persistence - no BPMN polling. Approver decides via any channel."),
    (["proc"], ["robot>proc", "proc>mi", "proc>dfins"],
     "13  Robot returns decision directly to BPMN -> process_response agent interprets"),
    (["sla"], ["sla>robot"], "14  SLA timer fires reminder if approver goes silent"),
    (["slack_r"], ["proc>slack_r"], "15  Requester notified via Slack + Outlook summary"),
    ([], [], "Adaptive Card + Action Center + Slack  -  all three verified live  Jun 22 2026"),
]

PULSE_FRAMES = 4
HOLD_FRAMES = 16
FIGSIZE = (9.0, 6.0)
DPI = 100


def _edge_key(e: Edge) -> str:
    return f"{e.src}>{e.dst}"


EDGE_BY_KEY = {_edge_key(e): e for e in EDGES}


def draw_frame(visible_nodes, visible_edges, active_nodes, active_edges, pulse, caption):
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # clusters (always faint background)
    for c in CLUSTERS:
        ax.add_patch(
            FancyBboxPatch(
                (c.x0, c.y0), c.x1 - c.x0, c.y1 - c.y0,
                boxstyle="round,pad=0.2,rounding_size=2.2",
                linewidth=1.2, edgecolor=c.color, facecolor=c.color + "12",
                linestyle=(0, (4, 3)), zorder=1,
            )
        )
        ax.text((c.x0 + c.x1) / 2, c.y1 - 2.4, c.title, ha="center", va="top",
                fontsize=7.5, color=c.color, fontweight="bold", zorder=2)

    # node patches (store for arrow clipping)
    patches = {}
    halo = math.sin(pulse * math.pi)  # 0..1..0
    for nid, n in NODES.items():
        if nid not in visible_nodes:
            continue
        fill, stroke, text = PALETTE[n.type]
        is_active = nid in active_nodes
        if is_active and halo > 0:
            ax.add_patch(
                FancyBboxPatch(
                    (n.x - n.w / 2 - 1.1, n.y - n.h / 2 - 1.1), n.w + 2.2, n.h + 2.2,
                    boxstyle="round,pad=0.2,rounding_size=2.0",
                    linewidth=0, facecolor=stroke, alpha=0.16 + 0.22 * halo, zorder=3,
                )
            )
        p = FancyBboxPatch(
            (n.x - n.w / 2, n.y - n.h / 2), n.w, n.h,
            boxstyle="round,pad=0.2,rounding_size=1.6",
            linewidth=2.4 if is_active else 1.4,
            edgecolor=stroke, facecolor=fill, zorder=5,
        )
        ax.add_patch(p)
        patches[nid] = p
        ax.text(n.x, n.y + (1.6 if n.tag else 0), n.label, ha="center", va="center",
                fontsize=6.6, color=text, fontweight="bold", zorder=6, linespacing=1.15)
        if n.tag:
            ax.text(n.x, n.y - n.h / 2 + 1.7, n.tag, ha="center", va="center",
                    fontsize=4.8, color=text, style="italic", alpha=0.8, zorder=6)

    # edges
    for key in visible_edges:
        e = EDGE_BY_KEY[key]
        if e.src not in patches or e.dst not in patches:
            continue
        is_active = key in active_edges
        color = PALETTE[NODES[e.dst].type][1] if is_active else EDGE_COLOR
        lw = 2.6 if is_active else 1.4
        arrow = FancyArrowPatch(
            posA=(NODES[e.src].x, NODES[e.src].y),
            posB=(NODES[e.dst].x, NODES[e.dst].y),
            patchA=patches[e.src], patchB=patches[e.dst],
            connectionstyle=f"arc3,rad={e.rad}",
            arrowstyle="-|>", mutation_scale=11,
            linewidth=lw, color=color, zorder=4,
            linestyle="--" if e.dashed else "-",
            shrinkA=2, shrinkB=2, alpha=0.95 if is_active else 0.7,
        )
        ax.add_patch(arrow)
        if e.label:
            mx = NODES[e.src].x + (NODES[e.dst].x - NODES[e.src].x) * e.lt + e.lx
            my = NODES[e.src].y + (NODES[e.dst].y - NODES[e.src].y) * e.lt + e.rad * 9 + e.ly
            ax.text(mx, my, e.label, ha="center", va="center", fontsize=5.0,
                    color=color if is_active else "#94A3B8",
                    fontweight="bold" if is_active else "normal", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.12", fc=BG, ec="none", alpha=0.88))

    # title + caption
    ax.text(50, 98.4, "Deal Desk Agent  -  Maestro BPMN + LangGraph", ha="center",
            va="top", fontsize=11.5, fontweight="bold", color="#F8FAFC")
    ax.add_patch(FancyBboxPatch((6, 0.6), 88, 4.6, boxstyle="round,pad=0.2,rounding_size=1.4",
                                linewidth=0, facecolor="#FA4616", zorder=8))
    ax.text(50, 2.9, caption, ha="center", va="center", fontsize=8.2, color="#11161C",
            fontweight="bold", zorder=9)

    fig.tight_layout(pad=0.3)
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = fig.canvas.buffer_rgba()
    img = Image.frombuffer("RGBA", (w, h), buf, "raw", "RGBA", 0, 1).convert("RGB")
    plt.close(fig)
    return img


def build():
    frames = []
    vis_n, vis_e = set(), set()
    for nodes, edges, caption in STEPS:
        vis_n |= set(nodes)
        vis_e |= set(edges)
        active_n = set(nodes)
        active_e = set(edges)
        reps = PULSE_FRAMES if nodes or edges else HOLD_FRAMES
        for i in range(reps):
            pulse = (i + 1) / max(reps, 1)
            frames.append(draw_frame(vis_n, vis_e, active_n, active_e, pulse, caption))
    # final hold on the full graph, no active highlight
    for _ in range(HOLD_FRAMES):
        frames.append(draw_frame(set(NODES), {_edge_key(e) for e in EDGES}, set(), set(),
                                 0.0, STEPS[-1][2]))

    gif_path = os.path.join(HERE, "deal-desk-flow.gif")
    # quantize each frame to keep the GIF small (<5 MB gallery limit)
    pal_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    pal_frames[0].save(
        gif_path, save_all=True, append_images=pal_frames[1:],
        duration=170, loop=0, optimize=True, disposal=2,
    )

    # crisp static of the full graph
    png = draw_frame(set(NODES), {_edge_key(e) for e in EDGES}, set(), set(),
                     0.0, STEPS[-1][2])
    png = png.resize((1500, 1000), Image.LANCZOS)
    png.save(os.path.join(HERE, "deal-desk-code-graph.png"))

    size_mb = os.path.getsize(gif_path) / 1e6
    print(f"frames={len(frames)}  gif={gif_path}  size={size_mb:.2f} MB")
    print(f"png={os.path.join(HERE, 'deal-desk-code-graph.png')}")


if __name__ == "__main__":
    build()
