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
        routeId: route.id,
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

  function nodeHeight(node) {
    if (node.kind === "group") {
      return Math.max(NODE_HEIGHT, 44 + (node.items || []).length * 18);
    }
    return NODE_HEIGHT;
  }

  function nodeCenter(node) {
    return {
      x: PADDING_X + node.depth * LANE_GAP + NODE_WIDTH / 2,
      y: PADDING_Y + node.row * ROW_GAP + nodeHeight(node) / 2,
    };
  }

  function renderEdge(svg, fromNode, toNode, kind) {
    const from = nodeCenter(fromNode);
    const to = nodeCenter(toNode);
    const startY = from.y + nodeHeight(fromNode) / 2;
    const endY = to.y - nodeHeight(toNode) / 2;
    const midY = Math.min(endY - 12, startY + Math.max(22, (endY - startY) / 2));
    const edgeKind = kind && kind !== "normal" ? ` flow-edge-${kind}` : "";
    const path = el("path", {
      d: `M ${from.x} ${startY} V ${midY} H ${to.x} V ${endY}`,
      class: `flow-edge${edgeKind}`,
      "marker-end": "url(#flow-arrow)",
    });
    svg.appendChild(path);
  }

  function renderNode(svg, node, onNavigate) {
    const height = nodeHeight(node);
    const center = nodeCenter(node);
    const x = center.x - NODE_WIDTH / 2;
    const y = center.y - height / 2;
    const navigable =
      typeof onNavigate === "function" &&
      node.routeId &&
      Number.isInteger(node.stepIndex);
    const group = el("g", {
      class: `flow-node flow-node-${node.kind}${navigable ? " flow-node-link" : ""}`,
      transform: `translate(${x} ${y})`,
      ...(navigable ? {
        role: "link",
        tabindex: "0",
        "aria-label": `${node.label || node.routeId} をガイドで開く`,
      } : {}),
    });

    if (navigable) {
      const navigate = () => onNavigate(node.routeId, node.stepIndex);
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
      const cy = height / 2;
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
        height,
        rx: node.kind === "end" ? 20 : 9,
        class: "flow-node-shape",
      }));

      if (node.kind === "group") {
        const label = el("text", {
          x: NODE_WIDTH / 2,
          y: 22,
          "text-anchor": "middle",
          class: "flow-node-text flow-node-group-title",
        });
        label.textContent = node.label;
        group.appendChild(label);
        (node.items || []).forEach((item, index) => {
          const itemLabel = el("text", {
            x: 12,
            y: 44 + index * 18,
            class: "flow-node-text flow-node-group-item",
          });
          itemLabel.textContent = `• ${item}`;
          group.appendChild(itemLabel);
        });
      } else {
        const lines = wrapLabel(node.label, 17);
        const lineHeight = 16;
        const firstY = height / 2 - ((lines.length - 1) * lineHeight) / 2 + 5;
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
    }

    const title = el("title");
    title.textContent = node.kind === "branch"
      ? "セーブ/ロード構造から推定した分岐"
      : node.kind === "group"
        ? `${node.label}: ${(node.items || []).join(" / ")}`
        : node.label;
    group.appendChild(title);
    svg.appendChild(group);
  }

  function resolveRef(graph, ref) {
    if (!ref || typeof ref !== "object") return null;
    if (ref.synthetic) {
      return graph.nodes.find(node => node.id === `sidecar-${ref.synthetic}`) || null;
    }
    const routeNodes = graph.nodes.filter(node => node.routeId === ref.route);
    if (ref.start === true) {
      return routeNodes.find(node => node.kind === "route") || null;
    }
    if (ref.save != null) {
      return routeNodes.find(node => node.kind === "branch" && String(node.slot) === String(ref.save)) || null;
    }
    if (ref.step && ref.step.simpleJp) {
      const occurrence = Math.max(1, Number(ref.step.occurrence || 1));
      const matches = routeNodes.filter(node => node.label === ref.step.simpleJp);
      return matches[occurrence - 1] || null;
    }
    return null;
  }

  function requireRef(graph, ref, context) {
    const node = resolveRef(graph, ref);
    if (!node) throw new Error(`Unresolved flowchart sidecar ref: ${context}`);
    return node;
  }

  function dedupeEdges(edges) {
    const seen = new Set();
    return edges.filter(edge => {
      const key = `${edge.from}|${edge.to}|${edge.kind || "normal"}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function buildEnhancedGraph(guideData, sidecar) {
    if (!sidecar || sidecar.version !== 1) throw new Error("Unsupported flowchart sidecar");

    const nodes = [];
    let edges = [];
    let rowOffset = 0;
    const routes = Array.isArray(guideData.routes) ? guideData.routes : [];

    routes.forEach(route => {
      const routeGraph = buildRouteGraph(route);
      const localMaxRow = routeGraph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
      routeGraph.nodes.forEach(node => nodes.push({ ...node, row: node.row + rowOffset }));
      routeGraph.edges.forEach(edge => edges.push({ ...edge }));
      rowOffset += localMaxRow + 3;
    });

    const graph = { nodes, edges, maxDepth: 0, maxRow: 0, enhanced: true };

    for (const synthetic of sidecar.syntheticNodes || []) {
      if (!synthetic.id || !synthetic.label) throw new Error("Invalid synthetic flowchart node");
      const near = requireRef(graph, synthetic.near, `synthetic ${synthetic.id} near`);
      const jump = synthetic.jumpTo ? requireRef(graph, synthetic.jumpTo, `synthetic ${synthetic.id} jumpTo`) : null;
      graph.nodes.push({
        id: `sidecar-${synthetic.id}`,
        kind: synthetic.kind || "step",
        label: synthetic.label,
        routeId: synthetic.route || near.routeId,
        row: near.row + Number(synthetic.rowOffset || 0),
        depth: Math.max(0, near.depth + Number(synthetic.laneOffset == null ? 1 : synthetic.laneOffset)),
        stepIndex: jump ? jump.stepIndex : null,
        synthetic: true,
      });
    }

    for (const groupDef of sidecar.groups || []) {
      if (!groupDef.id || !Array.isArray(groupDef.members) || groupDef.members.length < 2) {
        throw new Error("Invalid flowchart group");
      }
      const members = groupDef.members.map((ref, index) =>
        requireRef(graph, ref, `group ${groupDef.id} member ${index + 1}`)
      );
      const memberIds = new Set(members.map(node => node.id));
      const incoming = graph.edges.filter(edge => memberIds.has(edge.to) && !memberIds.has(edge.from));
      const outgoing = graph.edges.filter(edge => memberIds.has(edge.from) && !memberIds.has(edge.to));
      graph.edges = graph.edges.filter(edge => !memberIds.has(edge.from) && !memberIds.has(edge.to));
      graph.nodes = graph.nodes.filter(node => !memberIds.has(node.id));

      const groupNode = {
        id: `sidecar-${groupDef.id}`,
        kind: "group",
        label: groupDef.label || "順不同（すべて）",
        items: members.map(node => node.label),
        routeId: groupDef.route || members[0].routeId,
        row: Math.min(...members.map(node => node.row)),
        depth: Math.min(...members.map(node => node.depth)),
        stepIndex: members[0].stepIndex,
        synthetic: true,
      };
      graph.nodes.push(groupNode);
      incoming.forEach(edge => graph.edges.push({ from: edge.from, to: groupNode.id, kind: edge.kind || "normal" }));
      outgoing.forEach(edge => graph.edges.push({ from: groupNode.id, to: edge.to, kind: edge.kind || "normal" }));
    }

    const extraEdges = [
      ...(sidecar.addEdges || []),
      ...(sidecar.routeLinks || []),
    ];
    for (const edgeDef of extraEdges) {
      const from = requireRef(graph, edgeDef.from, "edge from");
      const to = requireRef(graph, edgeDef.to, "edge to");
      graph.edges.push({
        from: from.id,
        to: to.id,
        kind: edgeDef.kind || "normal",
        label: edgeDef.label || "",
      });
    }

    for (const edgeDef of sidecar.removeEdges || []) {
      const from = requireRef(graph, edgeDef.from, "remove edge from");
      const to = requireRef(graph, edgeDef.to, "remove edge to");
      graph.edges = graph.edges.filter(edge => !(edge.from === from.id && edge.to === to.id));
    }

    graph.edges = dedupeEdges(graph.edges);
    graph.maxDepth = graph.nodes.reduce((max, node) => Math.max(max, node.depth), 0);
    graph.maxRow = graph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
    return graph;
  }

  function renderGraphSection(titleText, graph, onNavigate, ariaLabel) {
    const section = document.createElement("section");
    section.className = "flowchart-route";

    const heading = document.createElement("h4");
    heading.textContent = titleText;
    section.appendChild(heading);

    if (!graph.nodes.length) {
      const empty = document.createElement("p");
      empty.className = "flowchart-empty";
      empty.textContent = "ルートデータを読み込めませんでした。";
      section.appendChild(empty);
      return section;
    }

    const width = PADDING_X * 2 + NODE_WIDTH + graph.maxDepth * LANE_GAP;
    const maxRow = graph.maxRow != null
      ? graph.maxRow
      : graph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
    const height = PADDING_Y * 2 + (maxRow + 1) * ROW_GAP + 80;
    const scroller = document.createElement("div");
    scroller.className = "flowchart-canvas";
    const svg = el("svg", {
      viewBox: `0 0 ${width} ${height}`,
      width,
      height,
      role: "img",
      "aria-label": ariaLabel,
    });

    const zoomBar = document.createElement("div");
    zoomBar.className = "flowchart-zoom";
    const zoomOut = document.createElement("button");
    zoomOut.type = "button";
    zoomOut.textContent = "−";
    zoomOut.setAttribute("aria-label", "縮小");
    const fit = document.createElement("button");
    fit.type = "button";
    fit.textContent = "全体";
    fit.setAttribute("aria-label", "幅に合わせて全体表示");
    const zoomIn = document.createElement("button");
    zoomIn.type = "button";
    zoomIn.textContent = "＋";
    zoomIn.setAttribute("aria-label", "拡大");
    const zoomReadout = document.createElement("span");
    zoomReadout.className = "flowchart-zoom-readout";
    zoomBar.append(zoomOut, fit, zoomIn, zoomReadout);

    let scale = 1;
    let fitMode = true;

    function applyScale(nextScale) {
      scale = Math.max(0.15, Math.min(2.5, nextScale));
      svg.style.width = `${Math.round(width * scale)}px`;
      svg.style.height = `${Math.round(height * scale)}px`;
      zoomReadout.textContent = `${Math.round(scale * 100)}%`;
    }

    function fitToWidth() {
      const availableWidth = Math.max(1, scroller.clientWidth - 2);
      applyScale(Math.min(1, availableWidth / width));
      scroller.scrollLeft = 0;
    }

    zoomOut.addEventListener("click", () => {
      fitMode = false;
      applyScale(scale / 1.25);
    });
    zoomIn.addEventListener("click", () => {
      fitMode = false;
      applyScale(scale * 1.25);
    });
    fit.addEventListener("click", () => {
      fitMode = true;
      fitToWidth();
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
    graph.nodes.forEach(node => renderNode(svg, node, onNavigate));

    scroller.appendChild(svg);
    section.appendChild(zoomBar);
    section.appendChild(scroller);

    requestAnimationFrame(fitToWidth);
    if (window.ResizeObserver) {
      const resizeObserver = new ResizeObserver(() => {
        if (!scroller.isConnected) {
          resizeObserver.disconnect();
          return;
        }
        if (fitMode) fitToWidth();
      });
      resizeObserver.observe(scroller);
    }

    return section;
  }

  function renderRoute(route, onNavigate) {
    const graph = buildRouteGraph(route);
    graph.maxRow = graph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
    return renderGraphSection(
      route.title || route.id,
      graph,
      onNavigate,
      `${route.title || route.id} の自動生成分岐図`
    );
  }

  function render(container, guideData, onNavigate, sidecar) {
    container.replaceChildren();

    let enhancedGraph = null;
    if (sidecar) {
      try {
        enhancedGraph = buildEnhancedGraph(guideData, sidecar);
      } catch (error) {
        console.warn("Flowchart sidecar rejected; falling back to inferred graph.", error);
      }
    }

    const note = document.createElement("div");
    note.className = "flowchart-note";
    note.textContent = enhancedGraph
      ? "既存ルートに検証済みの補足トポロジーを重ねた詳細分岐図です。各ノードをタップすると攻略の該当箇所へ移動します。"
      : "既存の攻略ルートから自動生成した推定分岐図です。各ノードをタップすると攻略の該当箇所へ移動します。ゲーム内部の全分岐を保証するものではありません。";
    container.appendChild(note);

    const legend = document.createElement("div");
    legend.className = "flowchart-legend";
    legend.innerHTML =
      '<span><i class="flowchart-legend-branch">?</i> 分岐</span>' +
      '<span><i class="flowchart-legend-end"></i> END</span>' +
      (enhancedGraph
        ? '<span><i class="flowchart-legend-group"></i> 順不同</span><span><i class="flowchart-legend-unlock"></i> 解禁</span>'
        : '');
    container.appendChild(legend);

    const routes = Array.isArray(guideData.routes) ? guideData.routes : [];
    if (enhancedGraph) {
      container.appendChild(renderGraphSection(
        sidecar.title || guideData.title || "詳細分岐図",
        enhancedGraph,
        onNavigate,
        `${guideData.title || "ゲーム"} の詳細分岐図`
      ));
      return;
    }

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

  window.VNFlowchart = { buildRouteGraph, buildEnhancedGraph, render };
})();
