(function () {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const NODE_WIDTH = 216;
  const NODE_HEIGHT = 58;
  const ROW_GAP = 86;
  const LANE_GAP = 244;
  const PADDING_X = 34;
  const PADDING_Y = 28;

  function text(value) {
    return String(value || "").trim();
  }

  function saveSlot(step) {
    const match = text(step && step.simpleJp).match(/^セーブ\s*([0-9０-９]+)$/);
    return match ? match[1] : null;
  }

  function loadSlot(step) {
    const match = text(step && step.simpleJp).match(/^セーブ\s*([0-9０-９]+)にロード$/);
    return match ? match[1] : null;
  }

  function isEnd(step) {
    const label = text(step && step.simpleJp);
    return /^【.+】END$/i.test(label) || /(?:^|\s)END$/i.test(label);
  }

  function wrapLabel(label, maxChars) {
    const chars = Array.from(text(label));
    if (!chars.length) return ["—"];
    const lines = [];
    for (let i = 0; i < chars.length; i += maxChars) {
      lines.push(chars.slice(i, i + maxChars).join(""));
      if (lines.length === 3 && i + maxChars < chars.length) {
        lines[2] = lines[2].slice(0, Math.max(1, maxChars - 1)) + "…";
        break;
      }
    }
    return lines;
  }

  function buildRouteGraph(route) {
    const steps = Array.isArray(route.steps) ? route.steps : [];
    const nodes = [];
    const edges = [];
    const branchBySlot = new Map();
    let previousNodeId = null;
    let currentDepth = 0;
    let maxDepth = 0;
    let row = 0;

    function addNode(kind, label, depth, stepIndex, extra) {
      const id = `${route.id}-${nodes.length}`;
      const node = {
        id,
        kind,
        label: text(label),
        depth,
        row: row++,
        stepIndex,
        ...(extra || {}),
      };
      nodes.push(node);
      maxDepth = Math.max(maxDepth, depth);
      return node;
    }

    function addEdge(from, to, kind) {
      if (!from || !to || from === to) return;
      edges.push({ from, to, kind: kind || "normal" });
    }

    const start = addNode("route", route.title || route.id, 0, -1);
    previousNodeId = start.id;

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i] || {};
      const slot = saveSlot(step);

      if (slot) {
        const hasReturn = steps.slice(i + 1).some(s => s && s.isLoad === true && loadSlot(s) === slot);
        if (!hasReturn) continue;

        const branch = addNode("branch", "分岐", currentDepth, i, { slot });
        addEdge(previousNodeId, branch.id);
        branchBySlot.set(slot, {
          nodeId: branch.id,
          baseDepth: currentDepth,
          branchDepth: currentDepth + 1,
        });
        previousNodeId = branch.id;
        currentDepth += 1;
        maxDepth = Math.max(maxDepth, currentDepth);
        continue;
      }

      if (step.isLoad === true) {
        const target = branchBySlot.get(loadSlot(step));
        if (target) {
          previousNodeId = target.nodeId;
          currentDepth = target.baseDepth;
        }
        continue;
      }

      if (!text(step.simpleJp)) continue;

      let kind = "step";
      if (isEnd(step)) kind = "end";
      else if (step.badEndPath) kind = "detour";

      const node = addNode(kind, step.simpleJp, currentDepth, i, {
        badEndPath: step.badEndPath || null,
      });
      addEdge(previousNodeId, node.id, step.badEndPath ? "detour" : "normal");
      previousNodeId = node.id;

      // Structural rules also allow a documented ending that must be replayed
      // from the beginning when no usable save exists. In that shape there is
      // no isLoad marker, so treat a non-final END as terminal and start the
      // following walkthrough pass from the route root instead of drawing an
      // impossible END -> next-choice edge.
      const nextStep = steps[i + 1];
      if (kind === "end" && nextStep && nextStep.isLoad !== true) {
        previousNodeId = start.id;
        currentDepth = 0;
      }
    }

    return { nodes, edges, maxDepth };
  }

  function el(name, attrs) {
    const node = document.createElementNS(SVG_NS, name);
    Object.entries(attrs || {}).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function nodeCenter(node) {
    return {
      x: PADDING_X + node.depth * LANE_GAP + NODE_WIDTH / 2,
      y: PADDING_Y + node.row * ROW_GAP + NODE_HEIGHT / 2,
    };
  }

  function renderEdge(svg, fromNode, toNode, kind) {
    const from = nodeCenter(fromNode);
    const to = nodeCenter(toNode);
    const startY = from.y + NODE_HEIGHT / 2;
    const endY = to.y - NODE_HEIGHT / 2;
    const midY = Math.min(endY - 12, startY + Math.max(22, (endY - startY) / 2));
    const path = el("path", {
      d: `M ${from.x} ${startY} V ${midY} H ${to.x} V ${endY}`,
      class: `flow-edge ${kind === "detour" ? "flow-edge-detour" : ""}`,
      "marker-end": "url(#flow-arrow)",
    });
    svg.appendChild(path);
  }

  function renderNode(svg, node, route, onNavigate) {
    const center = nodeCenter(node);
    const x = center.x - NODE_WIDTH / 2;
    const y = center.y - NODE_HEIGHT / 2;
    const navigable = typeof onNavigate === "function";
    const group = el("g", {
      class: `flow-node flow-node-${node.kind}${navigable ? " flow-node-link" : ""}`,
      transform: `translate(${x} ${y})`,
      ...(navigable ? {
        role: "link",
        tabindex: "0",
        "aria-label": `${node.label || route.title || route.id} をガイドで開く`,
      } : {}),
    });

    if (navigable) {
      const navigate = () => onNavigate(route.id, node.stepIndex);
      group.addEventListener("click", navigate);
      group.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          navigate();
        }
      });
    }

    if (node.kind === "branch") {
      const cx = NODE_WIDTH / 2;
      const cy = NODE_HEIGHT / 2;
      const size = 24;
      group.appendChild(el("polygon", {
        points: `${cx},${cy-size} ${cx+size},${cy} ${cx},${cy+size} ${cx-size},${cy}`,
        class: "flow-node-shape",
      }));
      const label = el("text", {
        x: cx,
        y: cy + 4,
        "text-anchor": "middle",
        class: "flow-node-text flow-node-branch-text",
      });
      label.textContent = "?";
      group.appendChild(label);
    } else {
      group.appendChild(el("rect", {
        x: 0,
        y: 0,
        width: NODE_WIDTH,
        height: NODE_HEIGHT,
        rx: node.kind === "end" ? 20 : 9,
        class: "flow-node-shape",
      }));
      const lines = wrapLabel(node.label, 17);
      const lineHeight = 16;
      const firstY = NODE_HEIGHT / 2 - ((lines.length - 1) * lineHeight) / 2 + 5;
      lines.forEach((lineText, index) => {
        const label = el("text", {
          x: NODE_WIDTH / 2,
          y: firstY + index * lineHeight,
          "text-anchor": "middle",
          class: "flow-node-text",
        });
        label.textContent = lineText;
        group.appendChild(label);
      });
    }

    const title = el("title");
    title.textContent = node.kind === "branch" ? "セーブ/ロード構造から推定した分岐" : node.label;
    group.appendChild(title);
    svg.appendChild(group);
  }

  function renderRoute(route, onNavigate) {
    const graph = buildRouteGraph(route);
    const section = document.createElement("section");
    section.className = "flowchart-route";

    const heading = document.createElement("h4");
    heading.textContent = route.title || route.id;
    section.appendChild(heading);

    if (!Array.isArray(route.steps) || route.steps.length === 0) {
      const empty = document.createElement("p");
      empty.className = "flowchart-empty";
      empty.textContent = "ルートデータを読み込めませんでした。";
      section.appendChild(empty);
      return section;
    }

    const width = PADDING_X * 2 + NODE_WIDTH + graph.maxDepth * LANE_GAP;
    const height = PADDING_Y * 2 + Math.max(1, graph.nodes.length) * ROW_GAP;
    const scroller = document.createElement("div");
    scroller.className = "flowchart-canvas";
    const svg = el("svg", {
      viewBox: `0 0 ${width} ${height}`,
      width,
      height,
      role: "img",
      "aria-label": `${route.title || route.id} の自動生成分岐図`,
    });

    const defs = el("defs");
    const marker = el("marker", {
      id: "flow-arrow",
      markerWidth: 8,
      markerHeight: 8,
      refX: 7,
      refY: 4,
      orient: "auto",
      markerUnits: "strokeWidth",
    });
    marker.appendChild(el("path", { d: "M 0 0 L 8 4 L 0 8 z", class: "flow-arrow" }));
    defs.appendChild(marker);
    svg.appendChild(defs);

    const byId = new Map(graph.nodes.map(node => [node.id, node]));
    graph.edges.forEach(edge => {
      const from = byId.get(edge.from);
      const to = byId.get(edge.to);
      if (from && to) renderEdge(svg, from, to, edge.kind);
    });
    graph.nodes.forEach(node => renderNode(svg, node, route, onNavigate));

    scroller.appendChild(svg);
    section.appendChild(scroller);
    return section;
  }

  function render(container, guideData, onNavigate) {
    container.replaceChildren();

    const note = document.createElement("div");
    note.className = "flowchart-note";
    note.textContent = "既存の攻略ルートから自動生成した推定分岐図です。各ノードをタップすると攻略の該当箇所へ移動します。ゲーム内部の全分岐を保証するものではありません。";
    container.appendChild(note);

    const legend = document.createElement("div");
    legend.className = "flowchart-legend";
    legend.innerHTML = '<span><i class="flowchart-legend-branch">?</i> 分岐</span><span><i class="flowchart-legend-end"></i> END</span>';
    container.appendChild(legend);

    const routes = Array.isArray(guideData.routes) ? guideData.routes : [];
    routes.forEach((route, index) => {
      container.appendChild(renderRoute(route, onNavigate));
      if (index < routes.length - 1) {
        const next = document.createElement("div");
        next.className = "flowchart-next";
        next.textContent = "↓ 次のセクション";
        container.appendChild(next);
      }
    });
  }

  window.VNFlowchart = { buildRouteGraph, render };
})();
