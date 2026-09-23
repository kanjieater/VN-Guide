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

  function progressValue(progressMap, routeId) {
    if (!progressMap || !routeId) return null;
    const value = progressMap[routeId];
    return Number.isInteger(value) ? value : null;
  }

  function deriveCurrentProgress(routes, progressMap) {
    const orderedRoutes = Array.isArray(routes) ? routes : [];
    let completedAny = false;

    for (const route of orderedRoutes) {
      if (!route || !route.id) continue;
      const count = Array.isArray(route.steps)
        ? route.steps.length
        : (Number.isInteger(route.stepCount) ? route.stepCount : 0);
      if (count <= 0) continue;

      const progress = progressValue(progressMap, route.id);
      if (progress == null) {
        return completedAny ? { [route.id]: -1 } : {};
      }

      const terminalIndex = Math.max(0, count - 1);
      if (progress < terminalIndex) {
        return { [route.id]: Math.max(0, progress) };
      }

      completedAny = true;
    }

    return {};
  }

  function routeTitleHidden(routeId, progressState) {
    if (!progressState || !progressState.hideRouteTitles) return false;
    const progress = progressValue(progressState.routeProgress, routeId);
    return progress == null || progress <= 0;
  }

  function routeTitleFor(route, routeIndex, progressState) {
    if (!routeTitleHidden(route.id, progressState)) return route.title || route.id;
    return `ルート ${routeIndex + 1}`;
  }

  function nodeProgressState(node, progressState) {
    // Sidecar-only synthetic alternatives have navigation coordinates, not
    // proof that the player actually visited that branch. Keep them neutral
    // unless a synthetic construct defines explicit progress evidence
    // (currently groups via seenStepIndex/currentStepIndexes).
    if (node.synthetic && !Number.isInteger(node.seenStepIndex)) {
      return { seen: false, current: false, known: false };
    }

    const seenProgress = progressValue(progressState && progressState.seen, node.routeId);
    const currentProgress = progressValue(progressState && progressState.current, node.routeId);
    const seenTarget = Number.isInteger(node.seenStepIndex)
      ? node.seenStepIndex
      : node.stepIndex;

    const seen = Number.isInteger(seenTarget)
      ? (seenTarget < 0 ? seenProgress != null : seenProgress != null && seenProgress >= seenTarget)
      : false;
    const currentTargets = Array.isArray(node.currentStepIndexes)
      ? node.currentStepIndexes
      : [node.stepIndex];
    const current = currentTargets.some(stepIndex =>
      Number.isInteger(stepIndex) && currentProgress === stepIndex
    );

    return { seen, current, known: true };
  }

  function renderNode(svg, node, onNavigate, progressState) {
    const height = nodeHeight(node);
    const center = nodeCenter(node);
    const x = center.x - NODE_WIDTH / 2;
    const y = center.y - height / 2;
    const navigable =
      typeof onNavigate === "function" &&
      node.routeId &&
      Number.isInteger(node.stepIndex);
    const progress = nodeProgressState(node, progressState);
    const displayLabel = node.kind === "route" && routeTitleHidden(node.routeId, progressState)
      ? (progressState.routePlaceholders && progressState.routePlaceholders[node.routeId]) || "ルート"
      : node.label;
    const progressClass = !progress.known
      ? " flow-node-neutral"
      : progress.current
        ? " flow-node-current"
        : progress.seen
          ? " flow-node-seen"
          : " flow-node-unseen";
    const group = el("g", {
      class: `flow-node flow-node-${node.kind}${navigable ? " flow-node-link" : ""}${progressClass}`,
      transform: `translate(${x} ${y})`,
      ...(navigable ? {
        role: "link",
        tabindex: "0",
        "aria-label": `${displayLabel || node.routeId} をガイドで開く`,
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
        label.textContent = displayLabel;
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
        const lines = wrapLabel(displayLabel, 17);
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
        : displayLabel;
    group.appendChild(title);
    svg.appendChild(group);
  }

  const SIDECAR_TOP_LEVEL_KEYS = new Set([
    "version", "title", "syntheticNodes", "groups", "addEdges", "removeEdges", "routeLinks",
  ]);
  const SYNTHETIC_KINDS = new Set(["step", "detour", "end", "branch"]);
  const EDGE_KINDS = new Set(["normal", "detour", "unlock"]);

  function isPlainObject(value) {
    return !!value && typeof value === "object" && !Array.isArray(value);
  }

  function own(value, key) {
    return Object.prototype.hasOwnProperty.call(value, key);
  }

  function requireAllowedKeys(value, allowed, context) {
    const extra = Object.keys(value).filter(key => !allowed.has(key));
    if (extra.length) {
      throw new Error(`${context} has unsupported field(s): ${extra.join(", ")}`);
    }
  }

  function requireNonEmptyString(value, context) {
    if (typeof value !== "string" || !value.trim()) {
      throw new Error(`${context} must be a non-empty string`);
    }
  }

  function validateOffset(value, context) {
    if (value == null) return;
    if (typeof value !== "number" || !Number.isFinite(value) || Math.abs(value) > 1000) {
      throw new Error(`${context} must be a finite number between -1000 and 1000`);
    }
  }

  function validateRefShape(ref, routeIds, sidecarIds, context) {
    if (!isPlainObject(ref)) throw new Error(`${context} must be an object`);

    if (own(ref, "synthetic")) {
      requireAllowedKeys(ref, new Set(["synthetic"]), context);
      requireNonEmptyString(ref.synthetic, `${context}.synthetic`);
      if (!sidecarIds.has(ref.synthetic)) {
        throw new Error(`${context} references unknown sidecar node ${ref.synthetic}`);
      }
      return;
    }

    requireAllowedKeys(ref, new Set(["route", "start", "save", "step"]), context);
    requireNonEmptyString(ref.route, `${context}.route`);
    if (!routeIds.has(ref.route)) throw new Error(`${context} references unknown route ${ref.route}`);

    const hasStart = own(ref, "start");
    const hasSave = own(ref, "save");
    const hasStep = own(ref, "step");
    if (Number(hasStart) + Number(hasSave) + Number(hasStep) !== 1) {
      throw new Error(`${context} must select exactly one of start, save, or step`);
    }

    if (hasStart) {
      if (ref.start !== true) throw new Error(`${context}.start must be true`);
      return;
    }

    if (hasSave) {
      const slot = String(ref.save);
      if (!/^[0-9０-９]+$/.test(slot)) throw new Error(`${context}.save must be a save-slot number`);
      return;
    }

    if (!isPlainObject(ref.step)) throw new Error(`${context}.step must be an object`);
    requireAllowedKeys(ref.step, new Set(["simpleJp", "occurrence"]), `${context}.step`);
    requireNonEmptyString(ref.step.simpleJp, `${context}.step.simpleJp`);
    if (own(ref.step, "occurrence")) {
      if (!Number.isInteger(ref.step.occurrence) || ref.step.occurrence < 1) {
        throw new Error(`${context}.step.occurrence must be a positive integer`);
      }
    }
  }

  function validateEdge(edge, routeIds, sidecarIds, context, routeLink) {
    if (!isPlainObject(edge)) throw new Error(`${context} must be an object`);
    requireAllowedKeys(edge, new Set(["from", "to", "kind", "label"]), context);
    validateRefShape(edge.from, routeIds, sidecarIds, `${context}.from`);
    validateRefShape(edge.to, routeIds, sidecarIds, `${context}.to`);

    if (own(edge, "kind")) {
      if (typeof edge.kind !== "string" || !EDGE_KINDS.has(edge.kind)) {
        throw new Error(`${context}.kind is unsupported`);
      }
      if (routeLink && edge.kind !== "unlock") {
        throw new Error(`${context}.kind must be unlock for routeLinks`);
      }
    }
    if (own(edge, "label") && typeof edge.label !== "string") {
      throw new Error(`${context}.label must be a string`);
    }
  }

  function validateSidecar(guideData, sidecar) {
    if (!isPlainObject(sidecar) || sidecar.version !== 1) {
      throw new Error("Unsupported flowchart sidecar");
    }
    requireAllowedKeys(sidecar, SIDECAR_TOP_LEVEL_KEYS, "flowchart sidecar");
    if (own(sidecar, "title")) requireNonEmptyString(sidecar.title, "flowchart sidecar.title");

    const routes = Array.isArray(guideData.routes) ? guideData.routes : [];
    const routeIds = new Set(routes.map(route => route && route.id).filter(Boolean));
    const arrays = ["syntheticNodes", "groups", "addEdges", "removeEdges", "routeLinks"];
    for (const key of arrays) {
      if (own(sidecar, key) && !Array.isArray(sidecar[key])) {
        throw new Error(`flowchart sidecar.${key} must be an array`);
      }
    }

    const syntheticNodes = sidecar.syntheticNodes || [];
    const groups = sidecar.groups || [];
    const sidecarIds = new Set();

    for (const [index, node] of syntheticNodes.entries()) {
      const context = `syntheticNodes[${index}]`;
      if (!isPlainObject(node)) throw new Error(`${context} must be an object`);
      requireAllowedKeys(
        node,
        new Set(["id", "route", "kind", "label", "near", "rowOffset", "laneOffset", "jumpTo", "navigable"]),
        context
      );
      requireNonEmptyString(node.id, `${context}.id`);
      if (sidecarIds.has(node.id)) throw new Error(`Duplicate sidecar node id: ${node.id}`);
      sidecarIds.add(node.id);
    }

    for (const [index, group] of groups.entries()) {
      const context = `groups[${index}]`;
      if (!isPlainObject(group)) throw new Error(`${context} must be an object`);
      requireAllowedKeys(group, new Set(["id", "route", "label", "members"]), context);
      requireNonEmptyString(group.id, `${context}.id`);
      if (sidecarIds.has(group.id)) throw new Error(`Duplicate sidecar node id: ${group.id}`);
      sidecarIds.add(group.id);
    }

    for (const [index, node] of syntheticNodes.entries()) {
      const context = `syntheticNodes[${index}]`;
      requireNonEmptyString(node.label, `${context}.label`);
      const kind = node.kind || "step";
      if (!SYNTHETIC_KINDS.has(kind)) throw new Error(`${context}.kind is unsupported`);
      if (own(node, "route")) {
        requireNonEmptyString(node.route, `${context}.route`);
        if (!routeIds.has(node.route)) throw new Error(`${context}.route is unknown`);
      }
      validateOffset(node.rowOffset, `${context}.rowOffset`);
      validateOffset(node.laneOffset, `${context}.laneOffset`);
      if (own(node, "navigable") && typeof node.navigable !== "boolean") {
        throw new Error(`${context}.navigable must be a boolean`);
      }
      validateRefShape(node.near, routeIds, sidecarIds, `${context}.near`);
      if (node.jumpTo != null) {
        validateRefShape(node.jumpTo, routeIds, sidecarIds, `${context}.jumpTo`);
      }
    }

    for (const [index, group] of groups.entries()) {
      const context = `groups[${index}]`;
      if (own(group, "label")) requireNonEmptyString(group.label, `${context}.label`);
      if (!Array.isArray(group.members) || group.members.length < 2) {
        throw new Error(`${context}.members must contain at least two refs`);
      }

      const memberRoutes = [];
      for (const [memberIndex, ref] of group.members.entries()) {
        validateRefShape(ref, routeIds, sidecarIds, `${context}.members[${memberIndex}]`);
        if (!ref.step) throw new Error(`${context}.members must reference concrete route steps`);
        memberRoutes.push(ref.route);
      }
      const memberRoute = memberRoutes[0];
      if (memberRoutes.some(routeId => routeId !== memberRoute)) {
        throw new Error(`${context}.members must all belong to the same route`);
      }
      if (own(group, "route")) {
        requireNonEmptyString(group.route, `${context}.route`);
        if (group.route !== memberRoute) {
          throw new Error(`${context}.route must match its member route`);
        }
      }
    }

    for (const [index, edge] of (sidecar.addEdges || []).entries()) {
      validateEdge(edge, routeIds, sidecarIds, `addEdges[${index}]`, false);
    }
    for (const [index, edge] of (sidecar.removeEdges || []).entries()) {
      validateEdge(edge, routeIds, sidecarIds, `removeEdges[${index}]`, false);
    }
    for (const [index, edge] of (sidecar.routeLinks || []).entries()) {
      validateEdge(edge, routeIds, sidecarIds, `routeLinks[${index}]`, true);
    }

    return sidecar;
  }

  function resolveRef(graph, ref) {
    if (own(ref, "synthetic")) {
      return graph.nodes.find(node => node.id === `sidecar-${ref.synthetic}`) || null;
    }
    const routeNodes = graph.nodes.filter(node => node.routeId === ref.route);
    if (ref.start === true) {
      return routeNodes.find(node => node.kind === "route") || null;
    }
    if (own(ref, "save")) {
      return routeNodes.find(
        node => node.kind === "branch" && String(node.slot) === String(ref.save)
      ) || null;
    }
    const occurrence = ref.step.occurrence || 1;
    const matches = routeNodes.filter(node => node.label === ref.step.simpleJp);
    return matches[occurrence - 1] || null;
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

  function requireContiguousGroup(graph, members, groupId) {
    const memberIds = new Set(members.map(node => node.id));
    const internal = graph.edges.filter(edge =>
      memberIds.has(edge.from) && memberIds.has(edge.to)
    );
    const incoming = graph.edges.filter(edge =>
      memberIds.has(edge.to) && !memberIds.has(edge.from)
    );
    const outgoing = graph.edges.filter(edge =>
      memberIds.has(edge.from) && !memberIds.has(edge.to)
    );

    if (incoming.length !== 1 || outgoing.length !== 1 ||
        internal.length !== members.length - 1) {
      throw new Error(
        `Group ${groupId} must resolve to one contiguous chain with a single entry and exit`
      );
    }

    const inDegree = new Map(members.map(node => [node.id, 0]));
    const outDegree = new Map(members.map(node => [node.id, 0]));
    const nextById = new Map();
    for (const edge of internal) {
      inDegree.set(edge.to, inDegree.get(edge.to) + 1);
      outDegree.set(edge.from, outDegree.get(edge.from) + 1);
      if (nextById.has(edge.from)) {
        throw new Error(`Group ${groupId} contains an internal branch`);
      }
      nextById.set(edge.from, edge.to);
    }

    const starts = members.filter(node => inDegree.get(node.id) === 0);
    const ends = members.filter(node => outDegree.get(node.id) === 0);
    if (starts.length !== 1 || ends.length !== 1 ||
        incoming[0].to !== starts[0].id || outgoing[0].from !== ends[0].id) {
      throw new Error(`Group ${groupId} is not a contiguous rendered chain`);
    }

    const visited = new Set();
    let cursor = starts[0].id;
    while (cursor && !visited.has(cursor)) {
      visited.add(cursor);
      cursor = nextById.get(cursor) || null;
    }
    if (visited.size !== members.length || cursor !== null) {
      throw new Error(`Group ${groupId} is not a simple contiguous chain`);
    }

    return { memberIds, incoming, outgoing };
  }

  function buildEnhancedGraph(guideData, sidecar) {
    validateSidecar(guideData, sidecar);

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
      const near = requireRef(graph, synthetic.near, `synthetic ${synthetic.id} near`);
      if (synthetic.route && synthetic.route !== near.routeId) {
        throw new Error(`Synthetic node ${synthetic.id} route must match its near anchor route`);
      }
      const jump = synthetic.jumpTo
        ? requireRef(graph, synthetic.jumpTo, `synthetic ${synthetic.id} jumpTo`)
        : near;
      graph.nodes.push({
        id: `sidecar-${synthetic.id}`,
        kind: synthetic.kind || "step",
        label: synthetic.label,
        routeId: jump.routeId,
        row: near.row + (synthetic.rowOffset || 0),
        depth: Math.max(0, near.depth + (synthetic.laneOffset == null ? 1 : synthetic.laneOffset)),
        stepIndex: synthetic.navigable === false
          ? null
          : (Number.isInteger(jump.stepIndex) ? jump.stepIndex : null),
        synthetic: true,
      });
    }

    for (const groupDef of sidecar.groups || []) {
      const members = groupDef.members.map((ref, index) =>
        requireRef(graph, ref, `group ${groupDef.id} member ${index + 1}`)
      );
      const routeId = members[0].routeId;
      if (members.some(node => node.routeId !== routeId)) {
        throw new Error(`Group ${groupDef.id} resolved across multiple routes`);
      }

      const { memberIds, incoming, outgoing } =
        requireContiguousGroup(graph, members, groupDef.id);
      graph.edges = graph.edges.filter(edge => !memberIds.has(edge.from) && !memberIds.has(edge.to));
      graph.nodes = graph.nodes.filter(node => !memberIds.has(node.id));

      const navigationTarget = members[0];
      const groupNode = {
        id: `sidecar-${groupDef.id}`,
        kind: "group",
        label: groupDef.label || "順不同（すべて）",
        items: members.map(node => node.label),
        routeId: navigationTarget.routeId,
        row: Math.min(...members.map(node => node.row)),
        depth: Math.min(...members.map(node => node.depth)),
        stepIndex: Number.isInteger(navigationTarget.stepIndex) ? navigationTarget.stepIndex : null,
        seenStepIndex: Math.max(...members.map(node =>
          Number.isInteger(node.stepIndex) ? node.stepIndex : -1
        )),
        currentStepIndexes: members
          .map(node => node.stepIndex)
          .filter(Number.isInteger),
        synthetic: true,
      };
      graph.nodes.push(groupNode);
      incoming.forEach(edge =>
        graph.edges.push({ from: edge.from, to: groupNode.id, kind: edge.kind || "normal" })
      );
      outgoing.forEach(edge =>
        graph.edges.push({ from: groupNode.id, to: edge.to, kind: edge.kind || "normal" })
      );
    }

    for (const edgeDef of sidecar.addEdges || []) {
      const from = requireRef(graph, edgeDef.from, "add edge from");
      const to = requireRef(graph, edgeDef.to, "add edge to");
      graph.edges.push({
        from: from.id,
        to: to.id,
        kind: edgeDef.kind || "normal",
        label: edgeDef.label || "",
      });
    }

    for (const edgeDef of sidecar.routeLinks || []) {
      const from = requireRef(graph, edgeDef.from, "route link from");
      const to = requireRef(graph, edgeDef.to, "route link to");
      graph.edges.push({
        from: from.id,
        to: to.id,
        kind: edgeDef.kind || "unlock",
        label: edgeDef.label || "",
      });
    }

    for (const edgeDef of sidecar.removeEdges || []) {
      const from = requireRef(graph, edgeDef.from, "remove edge from");
      const to = requireRef(graph, edgeDef.to, "remove edge to");
      const before = graph.edges.length;
      graph.edges = graph.edges.filter(edge => !(edge.from === from.id && edge.to === to.id));
      if (graph.edges.length === before) {
        throw new Error(`Flowchart sidecar removeEdges target does not exist: ${from.id} -> ${to.id}`);
      }
    }

    graph.edges = dedupeEdges(graph.edges);
    graph.maxDepth = graph.nodes.reduce((max, node) => Math.max(max, node.depth), 0);
    graph.maxRow = graph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
    return graph;
  }

  function createZoomGroup(container) {
    const controllers = [];
    let multiplier = 1;

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
    container.appendChild(zoomBar);

    function updateReadout() {
      zoomReadout.textContent = `${Math.round(multiplier * 100)}%`;
    }

    function applyAll(focusController, clientX) {
      controllers.forEach(controller => {
        controller.applyMultiplier(
          multiplier,
          controller === focusController ? clientX : undefined
        );
      });
      updateReadout();
    }

    function zoomBy(factor, focusController, clientX) {
      multiplier = Math.max(0.2, Math.min(4, multiplier * factor));
      applyAll(focusController, clientX);
    }

    function fitAll() {
      multiplier = 1;
      controllers.forEach(controller => controller.fit());
      updateReadout();
    }

    zoomOut.addEventListener("click", () => zoomBy(1 / 1.25));
    zoomIn.addEventListener("click", () => zoomBy(1.25));
    fit.addEventListener("click", fitAll);
    updateReadout();

    return {
      register(controller) {
        controllers.push(controller);
      },
      zoomBy,
      multiplier: () => multiplier,
      refresh(controller) {
        controller.applyMultiplier(multiplier);
      },
    };
  }

  function renderGraphSection(titleText, graph, onNavigate, ariaLabel, progressState, zoomGroup) {
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

    let scale = 1;

    function applyScale(nextScale) {
      scale = Math.max(0.15, Math.min(2.5, nextScale));
      svg.style.width = `${Math.round(width * scale)}px`;
      svg.style.height = `${Math.round(height * scale)}px`;
    }

    function fittedScale() {
      const availableWidth = Math.max(1, scroller.clientWidth - 2);
      return Math.min(1, availableWidth / width);
    }

    function zoomAtScale(nextScale, clientX) {
      const rect = scroller.getBoundingClientRect();
      const localX = Number.isFinite(clientX)
        ? clientX - rect.left
        : scroller.clientWidth / 2;
      const contentX = (scroller.scrollLeft + localX) / scale;
      applyScale(nextScale);
      scroller.scrollLeft = Math.max(0, contentX * scale - localX);
    }

    const zoomController = {
      applyMultiplier(multiplier, clientX) {
        zoomAtScale(fittedScale() * multiplier, clientX);
      },
      fit() {
        applyScale(fittedScale());
        scroller.scrollLeft = 0;
      },
    };
    if (zoomGroup) zoomGroup.register(zoomController);

    scroller.addEventListener("wheel", event => {
      event.preventDefault();
      const factor = Math.exp(-event.deltaY * 0.0015);
      if (zoomGroup) {
        zoomGroup.zoomBy(factor, zoomController, event.clientX);
      } else {
        zoomAtScale(scale * factor, event.clientX);
      }
    }, { passive: false });

    let pinchDistance = null;

    function touchDistance(touches) {
      const dx = touches[0].clientX - touches[1].clientX;
      const dy = touches[0].clientY - touches[1].clientY;
      return Math.hypot(dx, dy);
    }

    function touchMidpointX(touches) {
      return (touches[0].clientX + touches[1].clientX) / 2;
    }

    scroller.addEventListener("touchstart", event => {
      if (event.touches.length !== 2) return;
      event.preventDefault();
      pinchDistance = touchDistance(event.touches);
    }, { passive: false });

    scroller.addEventListener("touchmove", event => {
      if (event.touches.length !== 2 || !pinchDistance) return;
      event.preventDefault();
      const nextDistance = touchDistance(event.touches);
      if (nextDistance <= 0) return;
      const factor = nextDistance / pinchDistance;
      if (zoomGroup) {
        zoomGroup.zoomBy(factor, zoomController, touchMidpointX(event.touches));
      } else {
        zoomAtScale(scale * factor, touchMidpointX(event.touches));
      }
      pinchDistance = nextDistance;
    }, { passive: false });

    scroller.addEventListener("touchend", event => {
      if (event.touches.length < 2) pinchDistance = null;
    }, { passive: true });

    scroller.addEventListener("touchcancel", () => {
      pinchDistance = null;
    }, { passive: true });

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
    graph.nodes.forEach(node => renderNode(svg, node, onNavigate, progressState));

    scroller.appendChild(svg);
    section.appendChild(scroller);

    requestAnimationFrame(() => {
      if (zoomGroup) zoomGroup.refresh(zoomController);
      else zoomController.fit();
    });
    if (window.ResizeObserver) {
      const resizeObserver = new ResizeObserver(() => {
        if (!scroller.isConnected) {
          resizeObserver.disconnect();
          return;
        }
        if (zoomGroup) zoomGroup.refresh(zoomController);
        else zoomController.fit();
      });
      resizeObserver.observe(scroller);
    }

    return section;
  }

  function renderRoute(route, routeIndex, onNavigate, progressState, zoomGroup) {
    const graph = buildRouteGraph(route);
    graph.maxRow = graph.nodes.reduce((max, node) => Math.max(max, node.row), 0);
    return renderGraphSection(
      routeTitleFor(route, routeIndex, progressState),
      graph,
      onNavigate,
      `${routeTitleFor(route, routeIndex, progressState)} の自動生成分岐図`,
      progressState,
      zoomGroup
    );
  }

  function render(container, guideData, onNavigate, sidecar, progressState) {
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
      ? "既存ルートに補足トポロジーを重ねた詳細分岐図です。各ノードをタップすると攻略の該当箇所へ移動します。"
      : "既存の攻略ルートから自動生成した推定分岐図です。各ノードをタップすると攻略の該当箇所へ移動します。ゲーム内部の全分岐を保証するものではありません。";
    container.appendChild(note);

    const legend = document.createElement("div");
    legend.className = "flowchart-legend";
    legend.innerHTML =
      '<span><i class="flowchart-legend-seen"></i> 既読</span>' +
      '<span><i class="flowchart-legend-current"></i> 現在位置</span>' +
      '<span><i class="flowchart-legend-unseen"></i> 未読</span>' +
      '<span><i class="flowchart-legend-branch">?</i> 分岐</span>' +
      '<span><i class="flowchart-legend-end"></i> END</span>' +
      (enhancedGraph
        ? '<span><i class="flowchart-legend-group"></i> 順不同</span><span><i class="flowchart-legend-unlock"></i> 解禁</span>'
        : '');
    container.appendChild(legend);

    const zoomGroup = createZoomGroup(container);
    const routes = Array.isArray(guideData.routes) ? guideData.routes : [];
    if (enhancedGraph) {
      container.appendChild(renderGraphSection(
        sidecar.title || guideData.title || "詳細分岐図",
        enhancedGraph,
        onNavigate,
        `${guideData.title || "ゲーム"} の詳細分岐図`,
        progressState,
        zoomGroup
      ));
      return;
    }

    routes.forEach((route, index) => {
      container.appendChild(renderRoute(route, index, onNavigate, progressState, zoomGroup));
      if (index < routes.length - 1) {
        const next = document.createElement("div");
        next.className = "flowchart-next";
        next.textContent = "↓ 次のセクション";
        container.appendChild(next);
      }
    });
  }

  window.VNFlowchart = {
    buildRouteGraph,
    validateSidecar,
    buildEnhancedGraph,
    deriveCurrentProgress,
    nodeProgressState,
    render,
  };
})();
