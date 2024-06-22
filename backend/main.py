from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from collections import defaultdict, deque

app = FastAPI()


origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000"   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

class Position(BaseModel):
    x: float
    y: float

class NodeData(BaseModel):
    id: str
    nodeType: str

class Node(BaseModel):
    id: str
    type: str
    position: Position
    data: NodeData
    width: Optional[int] = None
    height: Optional[int] = None

class MarkerEnd(BaseModel):
    type: str
    height: str
    width: str

class Edge(BaseModel):
    source: str
    sourceHandle: str
    target: str
    targetHandle: str
    type: str
    animated: bool
    markerEnd: MarkerEnd
    id: str

class GraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


def is_dag(nodes: List[Node], edges: List[Edge]) -> bool:
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    for edge in edges:
        graph[edge.source].append(edge.target)
        in_degree[edge.target] += 1
    zero_in_degree_queue = deque([node.id for node in nodes if in_degree[node.id] == 0])

    visited_count = 0

    while zero_in_degree_queue:
        node = zero_in_degree_queue.popleft()
        visited_count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_in_degree_queue.append(neighbor)

    return visited_count == len(nodes)

@app.post('/pipelines/parse')
def parse_pipeline(data: GraphData):
    # Handle the incoming data
    nodesLength = len(data.nodes);
    edgesLength = len(data.edges);
    dag_status = is_dag(data.nodes, data.edges)
   
    finalObj = {
        "num_nodes":nodesLength,
        "num_edges":edgesLength,
        "is_dag": dag_status
    }

    return {'status': 'parsed', 'data': finalObj}
