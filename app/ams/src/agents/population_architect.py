"""Population Architect for hierarchical persona generation.

This module designs the hierarchical structure of persona populations
based on article context analysis.
"""
import json
from typing import Dict, List, Any, Optional
import random
import math

from src.utils.llm_factory import create_llm
from src.utils.json_parser import parse_llm_json_response


class PopulationArchitect:
    """Design the hierarchical structure of the persona population."""
    
    def __init__(self):
        """Initialize the PopulationArchitect."""
        self.llm = create_llm()
        
    async def design_population_hierarchy(
        self, 
        context: Dict[str, Any],
        target_size: int = 50
    ) -> Dict[str, Any]:
        """Create a hierarchical population structure.
        
        Args:
            context: Article context analysis results
            target_size: Target number of personas to generate
            
        Returns:
            Dict containing:
                - hierarchy: Hierarchical population structure
                - network_topology: Network relationship design
                - influence_map: Influence patterns between personas
        """
        try:
            # Level 1: Major segments
            major_segments = await self._design_major_segments(context)
            
            # Level 2: Sub-segments within each major segment
            sub_segments = {}
            for segment in major_segments:
                sub_segments[segment['id']] = await self._design_sub_segments(
                    segment, context
                )
            
            # Level 3: Micro-clusters for nuanced behaviors
            micro_clusters = await self._design_micro_clusters(
                sub_segments, context
            )
            
            # Level 4: Individual persona slots with relationships
            persona_slots = await self._allocate_persona_slots(
                major_segments, sub_segments, micro_clusters, target_size
            )
            
            return {
                "hierarchy": {
                    "major_segments": major_segments,
                    "sub_segments": sub_segments,
                    "micro_clusters": micro_clusters,
                    "persona_slots": persona_slots
                },
                "network_topology": self._design_network_topology(persona_slots),
                "influence_map": self._design_influence_patterns(persona_slots)
            }
            
        except Exception as e:
            # Return default structure on error
            return {
                "hierarchy": {
                    "major_segments": [],
                    "sub_segments": {},
                    "micro_clusters": {},
                    "persona_slots": []
                },
                "network_topology": {"type": "random", "density": 0.1},
                "influence_map": {"influencer_nodes": [], "influence_paths": []}
            }
    
    async def _design_major_segments(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design major population segments based on context."""
        segment_prompt = f"""
        Context: {json.dumps(context, indent=2)}
        
        Design 3-5 major population segments for this article.
        Go beyond obvious categories. Consider:
        
        1. UNEXPECTED INTERSECTIONS:
           - People at the intersection of multiple interests
           - Those with contradictory positions
           - Bridge populations between communities
        
        2. TEMPORAL RELATIONSHIPS:
           - Early adopters vs late majority
           - Those who knew "before it was cool"
           - People waiting for this information
        
        3. EMOTIONAL STAKES:
           - High emotional investment
           - Professional stakes
           - Personal history connections
        
        4. COGNITIVE STYLES:
           - Analytical vs intuitive processors
           - Visual vs textual learners
           - Systems vs detail thinkers
        
        For each segment, provide JSON array with:
        - id: unique identifier
        - name: segment name
        - percentage: population percentage (total should be 100)
        - characteristics: key traits (array)
        - relationship_to_article: how they relate to content
        - unexpected_traits: non-obvious characteristics (array)
        """
        
        try:
            response = await self.llm.ainvoke(segment_prompt)
            segments = parse_llm_json_response(response.content)
            
            # Ensure it's a list
            if isinstance(segments, dict):
                segments = segments.get("segments", [])
            
            # Normalize percentages to sum to 100
            total_percentage = sum(s.get("percentage", 0) for s in segments)
            if total_percentage > 0:
                for segment in segments:
                    segment["percentage"] = (segment.get("percentage", 0) / total_percentage) * 100
            
            return segments
            
        except Exception:
            return []
    
    async def _design_sub_segments(
        self, 
        segment: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Design sub-segments within a major segment."""
        sub_segment_prompt = f"""
        Major segment: {json.dumps(segment, indent=2)}
        Article context: {json.dumps(context.get('core_context', {}), indent=2)}
        
        Create 2-4 sub-segments within this major segment.
        Consider variations in:
        - Experience levels
        - Specific interests within the segment
        - Demographic variations
        - Behavioral patterns
        
        Return JSON array with:
        - id: unique identifier
        - parent_segment: {segment['id']}
        - characteristics: specific traits (array)
        - percentage_of_parent: percentage within parent segment (total 100)
        """
        
        try:
            response = await self.llm.ainvoke(sub_segment_prompt)
            sub_segments = parse_llm_json_response(response.content)
            
            if isinstance(sub_segments, dict):
                sub_segments = sub_segments.get("sub_segments", [])
                
            # Normalize percentages
            total = sum(s.get("percentage_of_parent", 0) for s in sub_segments)
            if total > 0:
                for sub in sub_segments:
                    sub["percentage_of_parent"] = (sub.get("percentage_of_parent", 0) / total) * 100
                    
            return sub_segments
            
        except Exception:
            return []
    
    async def _design_micro_clusters(
        self, 
        sub_segments: Dict[str, List[Dict]], 
        context: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Design micro-clusters for nuanced behaviors."""
        # Simplified implementation - create 2-3 micro-clusters per sub-segment
        micro_clusters = {}
        
        cluster_types = [
            "innovators", "pragmatists", "skeptics", "enthusiasts",
            "connectors", "mavens", "salespeople", "early_users",
            "influencers", "followers", "critics", "observers"
        ]
        
        for segment_id, sub_segs in sub_segments.items():
            for sub_seg in sub_segs:
                # Randomly assign 2-3 cluster types
                num_clusters = random.randint(2, 3)
                selected_clusters = random.sample(cluster_types, num_clusters)
                micro_clusters[sub_seg['id']] = selected_clusters
                
        return micro_clusters
    
    async def _allocate_persona_slots(
        self,
        major_segments: List[Dict],
        sub_segments: Dict[str, List[Dict]],
        micro_clusters: Dict[str, List[str]],
        target_size: int
    ) -> List[Dict[str, Any]]:
        """Allocate individual persona slots across the hierarchy."""
        persona_slots = []
        
        # Calculate slots per major segment
        for major_seg in major_segments:
            segment_size = int(target_size * major_seg["percentage"] / 100)
            
            # Get sub-segments for this major segment
            sub_segs = sub_segments.get(major_seg["id"], [])
            
            if not sub_segs:
                # No sub-segments, create slots directly
                for i in range(segment_size):
                    persona_slots.append({
                        "id": f"persona_{len(persona_slots)}",
                        "major_segment": major_seg["id"],
                        "sub_segment": None,
                        "micro_cluster": None,
                        "network_position": self._calculate_network_position(i, major_seg)
                    })
            else:
                # Distribute across sub-segments
                for sub_seg in sub_segs:
                    sub_size = int(segment_size * sub_seg["percentage_of_parent"] / 100)
                    clusters = micro_clusters.get(sub_seg["id"], [])
                    
                    for i in range(sub_size):
                        # Assign to a micro-cluster
                        cluster = clusters[i % len(clusters)] if clusters else None
                        
                        persona_slots.append({
                            "id": f"persona_{len(persona_slots)}",
                            "major_segment": major_seg["id"],
                            "sub_segment": sub_seg["id"],
                            "micro_cluster": cluster,
                            "network_position": self._calculate_network_position(i, sub_seg)
                        })
        
        # Ensure we hit target size
        while len(persona_slots) < target_size:
            # Add to largest segment
            persona_slots.append({
                "id": f"persona_{len(persona_slots)}",
                "major_segment": major_segments[0]["id"],
                "sub_segment": None,
                "micro_cluster": None,
                "network_position": self._calculate_network_position(len(persona_slots), {})
            })
        
        # Trim if over
        return persona_slots[:target_size]
    
    def _design_network_topology(self, persona_slots: List[Dict]) -> Dict[str, Any]:
        """Design the network topology for persona connections."""
        num_personas = len(persona_slots)
        
        # Choose network type based on population characteristics
        if num_personas < 20:
            network_type = "fully-connected"
            density = 0.8
        elif num_personas < 50:
            network_type = "small-world"
            density = 0.3
        else:
            network_type = "scale-free"
            density = 0.2
        
        # Calculate basic network metrics
        avg_connections = int(density * (num_personas - 1))
        clustering_coefficient = 0.4 + (0.3 * random.random())
        
        # Create connection matrix (simplified)
        connections = []
        for i, persona in enumerate(persona_slots):
            # Connect to others in same segment
            same_segment = [
                j for j, p in enumerate(persona_slots)
                if p["major_segment"] == persona["major_segment"] and i != j
            ]
            
            # Connect to some random others
            others = [j for j in range(num_personas) if j != i and j not in same_segment]
            
            # Make connections
            num_connections = min(avg_connections, len(same_segment) + len(others))
            segment_connections = min(int(num_connections * 0.7), len(same_segment))
            other_connections = num_connections - segment_connections
            
            connected_to = (
                random.sample(same_segment, segment_connections) +
                random.sample(others, min(other_connections, len(others)))
            )
            
            connections.append({
                "node": i,
                "connected_to": connected_to,
                "strength": [0.5 + 0.5 * random.random() for _ in connected_to]
            })
        
        return {
            "network_type": network_type,
            "density": density,
            "clustering_coefficient": clustering_coefficient,
            "average_connections": avg_connections,
            "connections": connections
        }
    
    def _design_influence_patterns(self, persona_slots: List[Dict]) -> Dict[str, Any]:
        """Design influence patterns between personas."""
        # Identify potential influencers
        influencer_nodes = []
        
        for i, persona in enumerate(persona_slots):
            # Check if persona has influencer characteristics
            if persona.get("micro_cluster") in ["influencers", "connectors", "mavens"]:
                influence_score = 0.7 + 0.3 * random.random()
            elif persona.get("micro_cluster") in ["innovators", "early_users"]:
                influence_score = 0.5 + 0.3 * random.random()
            else:
                influence_score = 0.1 + 0.3 * random.random()
            
            if influence_score > 0.6:
                influencer_nodes.append({
                    "id": persona["id"],
                    "index": i,
                    "influence_score": influence_score,
                    "influence_radius": int(5 + 10 * influence_score)
                })
        
        # Create influence paths
        influence_paths = []
        for influencer in influencer_nodes:
            # Create paths to nearby nodes
            for target in range(len(persona_slots)):
                if target != influencer["index"]:
                    distance = abs(target - influencer["index"])
                    if distance <= influencer["influence_radius"]:
                        influence_strength = influencer["influence_score"] * (1 - distance / influencer["influence_radius"])
                        influence_paths.append({
                            "from": influencer["index"],
                            "to": target,
                            "strength": influence_strength
                        })
        
        return {
            "influencer_nodes": influencer_nodes,
            "influence_paths": influence_paths,
            "influence_strength": {
                node["index"]: node["influence_score"] 
                for node in influencer_nodes
            }
        }
    
    def _calculate_network_position(self, index: int, segment_info: Dict) -> Dict[str, float]:
        """Calculate network position metrics for a persona."""
        # Simple calculation based on index and segment
        base_centrality = 0.3 + 0.4 * random.random()
        
        # Adjust based on segment characteristics
        if "leader" in str(segment_info).lower() or "influencer" in str(segment_info).lower():
            base_centrality += 0.2
        
        return {
            "centrality": min(base_centrality, 1.0),
            "clustering": 0.2 + 0.6 * random.random(),
            "bridge_score": 0.1 + 0.3 * random.random()
        }