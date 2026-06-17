from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


class Node(BaseModel):
    id: str


class Edge(BaseModel):
    source: str
    target: str


class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


def _check_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    adj: dict[str, list[str]] = {n.id: [] for n in nodes}
    for e in edges:
        if e.source in adj:
            adj[e.source].append(e.target)

    visited: set[str] = set()
    rec_stack: set[str] = set()

    def has_cycle(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        for neighbor in adj.get(node_id, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.discard(node_id)
        return False

    return not any(has_cycle(n.id) for n in nodes if n.id not in visited)


@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    return {
        'num_nodes': len(pipeline.nodes),
        'num_edges': len(pipeline.edges),
        'is_dag': _check_dag(pipeline.nodes, pipeline.edges),
    }
