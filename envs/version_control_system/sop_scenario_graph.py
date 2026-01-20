#!/usr/bin/env python3
"""
sop_scenario_graph.py

Given:
  1) A DBML-like schema (tables + Ref: lines)
  2) An SOP text (that mentions tools and/or tables)
  3) Tool source code (Python) where each tool reads/writes seeded JSON tables via data.get("<table>", {})

This script:
  - Extracts PKs per table from the schema
  - Extracts FK->PK relationships from `Ref:` lines
  - Extracts which tables each tool touches from tool source code
  - Infers which tools are referenced by the SOP
  - Builds a directed graph parent_table -> child_table (PK referenced by FK)
  - Restricts the graph to tables referenced by (SOP tools) ∪ (tables mentioned explicitly in SOP)
  - Traverses the induced subgraph to count leaf nodes (tables with out_degree == 0)
    Leaf count is reported as "distinct scenarios" per your definition.

Usage examples:
  python sop_scenario_graph.py \
    --schema schema.txt \
    --sop tools/interface_1/policy.md \
    --tools tools/interface_1 \
    --out graph.json

Notes:
  - If --sop is omitted, the graph will be built using all tables referenced by the tools (or all schema tables if no tools provided).
  - If --tools is omitted, the script will rely only on tables mentioned in the SOP, falling back to all schema tables.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


# -----------------------------
# Data model
# -----------------------------

@dataclass(frozen=True)
class ColumnRef:
    table: str
    column: str


@dataclass
class SchemaInfo:
    tables: Set[str]
    pk_by_table: Dict[str, Set[str]]
    # edges: (parent_table, parent_pk_col) -> (child_table, child_fk_col)
    fk_edges: List[Tuple[ColumnRef, ColumnRef]]


@dataclass
class Graph:
    # table-level adjacency: parent_table -> set(child_tables)
    adj: Dict[str, Set[str]]
    # reverse adjacency: child_table -> set(parent_tables)
    radj: Dict[str, Set[str]]

    def nodes(self) -> Set[str]:
        return set(self.adj.keys()) | set(self.radj.keys())

    def out_degree(self, node: str) -> int:
        return len(self.adj.get(node, set()))

    def in_degree(self, node: str) -> int:
        return len(self.radj.get(node, set()))


# -----------------------------
# Parsing helpers
# -----------------------------

_TABLE_BLOCK_RE = re.compile(
    r"Table\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>.*?)\}",
    re.DOTALL,
)

# Matches column definition lines like: "user_id string [primary key]"
# Captures: name, type, bracket content (optional)
_COL_LINE_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_()'\",\s-]*)\s*(\[[^\]]*\])?\s*$"
)

# Matches ref lines like: Ref: branches.repository_id > repositories.repository_id
_REF_RE = re.compile(
    r"Ref:\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*>\s*([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)"
)

# Tool class name and get_info "function" name patterns
_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_GET_INFO_NAME_RE = re.compile(r'"name"\s*:\s*"([^"]+)"')

# Typical table access patterns in tools:
#   data.get("repositories", {})
#   repositories = data.get("repositories", {})
_DATA_GET_TABLE_RE = re.compile(r'data\.get\(\s*"([A-Za-z_][A-Za-z0-9_]*)"\s*,\s*\{\s*\}\s*\)')

# Table names in SOP (best-effort)
_WORD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_many_files(paths: List[str]) -> str:
    chunks: List[str] = []
    for p in paths:
        if os.path.isdir(p):
            # read all .py or .txt files in directory
            for root, _, files in os.walk(p):
                for fn in files:
                    if fn.endswith((".py", ".txt")):
                        chunks.append(read_text_file(os.path.join(root, fn)))
        else:
            chunks.append(read_text_file(p))
    return "\n\n".join(chunks)


# -----------------------------
# Schema parsing
# -----------------------------

def parse_schema(schema_text: str) -> SchemaInfo:
    tables: Set[str] = set()
    pk_by_table: Dict[str, Set[str]] = {}
    fk_edges: List[Tuple[ColumnRef, ColumnRef]] = []

    # Parse table blocks and PK columns
    for m in _TABLE_BLOCK_RE.finditer(schema_text):
        table = m.group(1)
        tables.add(table)
        body = m.group("body") or ""
        pk_by_table.setdefault(table, set())

        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            colm = _COL_LINE_RE.match(line)
            if not colm:
                continue
            col_name = colm.group(1)
            bracket = colm.group(3) or ""
            if "primary key" in bracket.lower():
                pk_by_table[table].add(col_name)

    # Parse explicit refs
    for rm in _REF_RE.finditer(schema_text):
        child_table, child_fk = rm.group(1), rm.group(2)
        parent_table, parent_pk = rm.group(3), rm.group(4)
        # Convention in your schema: "Ref: child.fk > parent.pk"
        fk_edges.append((ColumnRef(parent_table, parent_pk), ColumnRef(child_table, child_fk)))
        tables.add(child_table)
        tables.add(parent_table)
        pk_by_table.setdefault(child_table, set())
        pk_by_table.setdefault(parent_table, set())

    return SchemaInfo(tables=tables, pk_by_table=pk_by_table, fk_edges=fk_edges)


# -----------------------------
# Tool parsing (tables touched + tool names)
# -----------------------------

def parse_tools(tool_text: str) -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    """
    Returns:
      tool_to_tables: maps tool identifier -> set of JSON tables touched
      tool_aliases: maps "function name" (from get_info) -> tool identifier
    """
    # Strategy:
    #  - Identify class names; within each class block, collect data.get("<table>", {}) occurrences
    #  - Also collect function names from get_info() blocks and map them to class
    tool_to_tables: Dict[str, Set[str]] = {}
    tool_aliases: Dict[str, str] = {}

    # Split into class blocks by "class X("
    class_positions = [(m.start(), m.group(1)) for m in _CLASS_RE.finditer(tool_text)]
    if not class_positions:
        # fallback: global scan
        tables = set(_DATA_GET_TABLE_RE.findall(tool_text))
        if tables:
            tool_to_tables["<global>"] = tables
        return tool_to_tables, tool_aliases

    # Add sentinel end
    class_positions.append((len(tool_text), "<END>"))

    for i in range(len(class_positions) - 1):
        start, cls = class_positions[i]
        end, _ = class_positions[i + 1]
        block = tool_text[start:end]

        tables = set(_DATA_GET_TABLE_RE.findall(block))
        if tables:
            tool_to_tables[cls] = tables
        else:
            tool_to_tables.setdefault(cls, set())

        # Attempt to map get_info function name to class
        # (There may be multiple get_info blocks; we map any discovered names)
        for nm in _GET_INFO_NAME_RE.findall(block):
            tool_aliases[nm] = cls

    return tool_to_tables, tool_aliases


def infer_tools_from_sop(sop_text: str, tool_aliases: Dict[str, str], tool_classes: Set[str]) -> Set[str]:
    """
    Best-effort:
      - If SOP mentions function names (e.g., create_branch), resolve via tool_aliases
      - If SOP mentions class names (e.g., CreateBranch), match directly
    """
    used: Set[str] = set()

    # Tokenize SOP for words
    words = set(_WORD_RE.findall(sop_text))

    # Direct class hits
    for cls in tool_classes:
        if cls in words:
            used.add(cls)

    # Function name hits
    for fn, cls in tool_aliases.items():
        if fn in words:
            used.add(cls)

    return used


def tables_mentioned_in_text(text: str, known_tables: Set[str]) -> Set[str]:
    words = set(_WORD_RE.findall(text))
    return {t for t in known_tables if t in words}


# -----------------------------
# Graph build + analysis
# -----------------------------

def build_table_graph(schema: SchemaInfo) -> Graph:
    adj: Dict[str, Set[str]] = {t: set() for t in schema.tables}
    radj: Dict[str, Set[str]] = {t: set() for t in schema.tables}

    for parent_ref, child_ref in schema.fk_edges:
        p, c = parent_ref.table, child_ref.table
        adj.setdefault(p, set()).add(c)
        radj.setdefault(c, set()).add(p)
        # ensure nodes exist
        adj.setdefault(c, set())
        radj.setdefault(p, set())

    return Graph(adj=adj, radj=radj)


def induced_subgraph(g: Graph, keep_nodes: Set[str]) -> Graph:
    adj: Dict[str, Set[str]] = {}
    radj: Dict[str, Set[str]] = {}

    for n in keep_nodes:
        adj[n] = set()
        radj[n] = set()

    for p in keep_nodes:
        for c in g.adj.get(p, set()):
            if c in keep_nodes:
                adj[p].add(c)
                radj[c].add(p)

    return Graph(adj=adj, radj=radj)


def reachable_from_roots(g: Graph) -> Set[str]:
    nodes = g.nodes()
    if not nodes:
        return set()

    roots = {n for n in nodes if g.in_degree(n) == 0}
    # If no roots (cycle-only graph), treat all nodes as "reachable"
    if not roots:
        return nodes

    seen: Set[str] = set()
    stack: List[str] = list(roots)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        for nxt in g.adj.get(n, set()):
            if nxt not in seen:
                stack.append(nxt)
    return seen


def leaf_nodes(g: Graph, within: Optional[Set[str]] = None) -> Set[str]:
    nodes = within if within is not None else g.nodes()
    return {n for n in nodes if len(g.adj.get(n, set()) & nodes) == 0}


def edges_as_dicts(schema: SchemaInfo, tables_filter: Optional[Set[str]] = None) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for parent_ref, child_ref in schema.fk_edges:
        if tables_filter is not None and (parent_ref.table not in tables_filter or child_ref.table not in tables_filter):
            continue
        out.append(
            {
                "parent_table": parent_ref.table,
                "parent_pk": parent_ref.column,
                "child_table": child_ref.table,
                "child_fk": child_ref.column,
            }
        )
    return out


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, help="Path to schema text file")
    ap.add_argument("--sop", required=False, help="Path to SOP text file")
    ap.add_argument(
        "--tools",
        required=False,
        nargs="*",
        help="Path(s) to tool source file(s) or directory(ies) containing tools",
    )
    ap.add_argument("--out", required=False, help="Write JSON output to this path")
    ap.add_argument(
        "--mode",
        choices=["leaf_count", "details"],
        default="details",
        help="Output mode: leaf_count (minimal) or details (default)",
    )
    args = ap.parse_args()

    schema_text = read_text_file(args.schema)
    schema = parse_schema(schema_text)
    full_graph = build_table_graph(schema)

    sop_text = read_text_file(args.sop) if args.sop else ""
    tools_text = read_many_files(args.tools) if args.tools else ""

    tool_to_tables: Dict[str, Set[str]] = {}
    tool_aliases: Dict[str, str] = {}

    if tools_text.strip():
        tool_to_tables, tool_aliases = parse_tools(tools_text)

    tool_classes = set(tool_to_tables.keys())

    # Determine tables of interest
    tables_of_interest: Set[str] = set()

    # Tables mentioned explicitly in SOP
    if sop_text.strip():
        tables_of_interest |= tables_mentioned_in_text(sop_text, schema.tables)

    # Tables touched by SOP-mentioned tools
    used_tools: Set[str] = set()
    if sop_text.strip() and tool_classes:
        used_tools = infer_tools_from_sop(sop_text, tool_aliases, tool_classes)
        for tname in used_tools:
            tables_of_interest |= tool_to_tables.get(tname, set())

    # Fallbacks if SOP did not identify anything
    if not tables_of_interest:
        # If SOP absent/empty or doesn't mention tools/tables, use all tool-touched tables
        if tool_to_tables:
            for tset in tool_to_tables.values():
                tables_of_interest |= set(tset)

    # Final fallback: if still empty, use all schema tables
    if not tables_of_interest:
        tables_of_interest = set(schema.tables)

    # Induce subgraph + compute leaves
    sub_g = induced_subgraph(full_graph, tables_of_interest)
    reachable = reachable_from_roots(sub_g)
    leaves = leaf_nodes(sub_g, within=reachable)

    result = {
        "inputs": {
            "schema_file": os.path.abspath(args.schema),
            "sop_file": os.path.abspath(args.sop) if args.sop else None,
            "tools_paths": [os.path.abspath(p) for p in (args.tools or [])],
        },
        "selection": {
            "used_tools_inferred_from_sop": sorted(used_tools),
            "tables_of_interest": sorted(tables_of_interest),
            "reachable_from_roots": sorted(reachable),
        },
        "primary_keys": {t: sorted(list(schema.pk_by_table.get(t, set()))) for t in sorted(tables_of_interest)},
        "relationships": edges_as_dicts(schema, tables_filter=tables_of_interest),
        "graph": {
            "adjacency": {t: sorted(list(sub_g.adj.get(t, set()))) for t in sorted(sub_g.nodes())},
            "reverse_adjacency": {t: sorted(list(sub_g.radj.get(t, set()))) for t in sorted(sub_g.nodes())},
        },
        "analysis": {
            "leaf_nodes": sorted(leaves),
            "leaf_count": len(leaves),
            "distinct_scenarios_assumption": "leaf_count",
        },
    }

    if args.mode == "leaf_count":
        minimal = {"leaf_count": result["analysis"]["leaf_count"], "leaf_nodes": result["analysis"]["leaf_nodes"]}
        out_str = json.dumps(minimal, indent=2)
    else:
        out_str = json.dumps(result, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_str + "\n")
    else:
        print(out_str)


if __name__ == "__main__":
    main()
