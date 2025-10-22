from typing import Dict, Any, List, Optional
from neo4j import AsyncGraphDatabase
import os
from datetime import datetime

class KnowledgeGraphManager:
    """
    Manages Neo4j knowledge graph for EE research findings
    
    Stores relationships between:
    - Papers ↔ Technologies ↔ Components
    - Patents ↔ Applications ↔ Manufacturers
    - Components ↔ Supply Chain ↔ Lifecycle
    """
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "changeme")
        self.driver = None
    
    async def connect(self):
        """Initialize Neo4j connection"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
    
    async def add_research_session(
        self,
        query: str,
        papers: List[Dict[str, Any]],
        patents: List[Dict[str, Any]],
        components: List[Dict[str, Any]],
        cross_references: Dict[str, Any]
    ):
        """
        Add a complete research session to knowledge graph
        """
        await self.connect()
        
        async with self.driver.session() as session:
            # Create query node
            query_id = await self._create_query_node(session, query)
            
            # Add papers
            for paper in papers[:20]:  # Limit to top 20
                paper_id = await self._create_paper_node(session, paper)
                await self._link_nodes(session, query_id, paper_id, "FOUND_PAPER")
            
            # Add patents
            for patent in patents[:20]:
                patent_id = await self._create_patent_node(session, patent)
                await self._link_nodes(session, query_id, patent_id, "FOUND_PATENT")
            
            # Add components
            for component in components[:30]:
                comp_id = await self._create_component_node(session, component)
                await self._link_nodes(session, query_id, comp_id, "FOUND_COMPONENT")
            
            # Add cross-references
            await self._add_cross_references(session, cross_references)
        
        print(f"✅ Knowledge graph updated for query: {query[:50]}...")
    
    async def _create_query_node(self, session, query: str) -> str:
        """Create a query node"""
        result = await session.run(
            """
            CREATE (q:Query {
                text: $query,
                timestamp: $timestamp,
                id: $id
            })
            RETURN q.id as id
            """,
            query=query,
            timestamp=datetime.utcnow().isoformat(),
            id=f"query_{hash(query)}"
        )
        record = await result.single()
        return record["id"]
    
    async def _create_paper_node(self, session, paper: Dict[str, Any]) -> str:
        """Create a paper node"""
        paper_id = paper.get("doi") or f"paper_{hash(paper.get('title', ''))}"
        
        await session.run(
            """
            MERGE (p:Paper {id: $id})
            SET p.title = $title,
                p.authors = $authors,
                p.year = $year,
                p.abstract = $abstract,
                p.url = $url
            """,
            id=paper_id,
            title=paper.get("title", ""),
            authors=paper.get("authors", []),
            year=paper.get("year"),
            abstract=paper.get("abstract", ""),
            url=paper.get("url", "")
        )
        
        return paper_id
    
    async def _create_patent_node(self, session, patent: Dict[str, Any]) -> str:
        """Create a patent node"""
        patent_id = patent.get("patent_number", f"patent_{hash(patent.get('title', ''))}")
        
        await session.run(
            """
            MERGE (p:Patent {id: $id})
            SET p.patent_number = $patent_number,
                p.title = $title,
                p.applicant = $applicant,
                p.filing_date = $filing_date,
                p.status = $status,
                p.region = $region
            """,
            id=patent_id,
            patent_number=patent.get("patent_number", ""),
            title=patent.get("title", ""),
            applicant=patent.get("applicant", ""),
            filing_date=patent.get("filing_date", ""),
            status=patent.get("status", ""),
            region=patent.get("region", "")
        )
        
        return patent_id
    
    async def _create_component_node(self, session, component: Dict[str, Any]) -> str:
        """Create a component node"""
        comp_id = component.get("part_number", f"comp_{hash(str(component))}")
        
        await session.run(
            """
            MERGE (c:Component {id: $id})
            SET c.part_number = $part_number,
                c.manufacturer = $manufacturer,
                c.category = $category,
                c.trl = $trl,
                c.lifecycle = $lifecycle,
                c.specifications = $specifications
            """,
            id=comp_id,
            part_number=component.get("part_number", ""),
            manufacturer=component.get("manufacturer", ""),
            category=component.get("category", ""),
            trl=component.get("trl"),
            lifecycle=component.get("lifecycle", ""),
            specifications=str(component.get("specs", {}))
        )
        
        return comp_id
    
    async def _link_nodes(self, session, from_id: str, to_id: str, relationship: str):
        """Create relationship between nodes"""
        await session.run(
            f"""
            MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
            MERGE (a)-[r:{relationship}]->(b)
            """,
            from_id=from_id,
            to_id=to_id
        )
    
    async def _add_cross_references(self, session, cross_refs: Dict[str, Any]):
        """Add cross-reference relationships"""
        # Paper → Patent links
        for link in cross_refs.get("paper_to_patent", []):
            paper_id = f"paper_{hash(link.get('paper', ''))}"
            patent_id = link.get("patent", "")
            await self._link_nodes(session, paper_id, patent_id, "CITES")
        
        # Patent → Component links
        for link in cross_refs.get("patent_to_component", []):
            patent_id = link.get("patent", "")
            comp_id = link.get("component", "")
            await self._link_nodes(session, patent_id, comp_id, "IMPLEMENTS")
        
        # Paper → Component links
        for link in cross_refs.get("paper_to_component", []):
            paper_id = f"paper_{hash(link.get('paper', ''))}"
            comp_id = link.get("component", "")
            await self._link_nodes(session, paper_id, comp_id, "DISCUSSES")
    
    async def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve component with all relationships"""
        await self.connect()
        
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Component {id: $id})
                OPTIONAL MATCH (c)<-[:FOUND_COMPONENT]-(q:Query)
                OPTIONAL MATCH (c)<-[:IMPLEMENTS]-(p:Patent)
                OPTIONAL MATCH (c)<-[:DISCUSSES]-(paper:Paper)
                RETURN c, collect(DISTINCT q) as queries, 
                       collect(DISTINCT p) as patents,
                       collect(DISTINCT paper) as papers
                """,
                id=component_id
            )
            
            record = await result.single()
            if record:
                return {
                    "component": dict(record["c"]),
                    "related_queries": [dict(q) for q in record["queries"]],
                    "related_patents": [dict(p) for p in record["patents"]],
                    "related_papers": [dict(p) for p in record["papers"]]
                }
        
        return None
    
    async def get_graph_subset(
        self,
        node_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get subset of graph for visualization"""
        await self.connect()
        
        async with self.driver.session() as session:
            if node_type:
                query = f"""
                MATCH (n:{node_type})
                OPTIONAL MATCH (n)-[r]-(m)
                RETURN n, collect(r) as relationships, collect(m) as connected
                LIMIT $limit
                """
            else:
                query = """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-(m)
                RETURN n, collect(r) as relationships, collect(m) as connected
                LIMIT $limit
                """
            
            result = await session.run(query, limit=limit)
            
            nodes = []
            edges = []
            
            async for record in result:
                node = dict(record["n"])
                nodes.append(node)
                
                for rel in record["relationships"]:
                    if rel:
                        edges.append({
                            "from": node.get("id"),
                            "to": rel.end_node.get("id"),
                            "type": rel.type
                        })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "count": len(nodes)
            }