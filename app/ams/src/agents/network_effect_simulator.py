"""
Network Effect Simulator for Article Market Simulator
Simulates how information spreads through social networks and influence patterns
"""

import logging
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import numpy as np

from src.utils.llm_factory import create_llm
from src.utils.json_parser import parse_llm_json_response

logger = logging.getLogger(__name__)


class InfluenceType(Enum):
    """Types of influence in the network"""
    AUTHORITY = "authority"  # Expert influence
    PEER = "peer"  # Same-level influence
    ASPIRATIONAL = "aspirational"  # Looking up to someone
    VIRAL = "viral"  # Mass spread influence
    NICHE = "niche"  # Specialized community influence


@dataclass
class NetworkNode:
    """Represents a persona in the network"""
    persona_id: str
    influence_score: float  # 0.0 to 1.0
    connectivity: int  # Number of connections
    influence_type: InfluenceType
    interests: List[str]
    engagement_threshold: float  # Minimum score to engage
    amplification_factor: float  # How much they amplify when sharing
    position: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))  # Network position


@dataclass
class NetworkEdge:
    """Represents a connection between personas"""
    source_id: str
    target_id: str
    influence_weight: float  # 0.0 to 1.0
    interaction_frequency: str  # "high", "medium", "low"
    relationship_type: str  # "professional", "social", "follower", etc.


@dataclass
class PropagationEvent:
    """Represents an information propagation event"""
    timestamp: int
    source_node: str
    target_nodes: List[str]
    content_score: float
    propagation_probability: float
    actual_propagation: bool


@dataclass
class NetworkSimulationResult:
    """Results from network simulation"""
    total_reach: int
    propagation_waves: List[List[str]]  # Nodes reached in each wave
    influence_map: Dict[str, float]  # Node ID to influence score
    key_influencers: List[str]  # Most influential nodes
    network_velocity: float  # Speed of spread
    saturation_point: int  # Time step when growth slows
    community_clusters: List[List[str]]  # Detected communities
    propagation_events: List[PropagationEvent]


class NetworkEffectSimulator:
    """
    Simulates network effects and information propagation
    Models how content spreads through social networks
    """
    
    def __init__(self):
        self.llm = create_llm()
        self.network_graph: Dict[str, NetworkNode] = {}
        self.edges: List[NetworkEdge] = []
        self.propagation_history: List[PropagationEvent] = []
    
    async def build_network(
        self,
        personas: List[Any],  # PersonaAttributes objects
        article_analysis: Dict[str, Any]
    ) -> None:
        """
        Build network structure from personas
        
        Args:
            personas: List of persona objects
            article_analysis: Analysis results for context
        """
        # Create network nodes from personas
        for i, persona in enumerate(personas):
            node = await self._create_network_node(persona, i, article_analysis)
            self.network_graph[node.persona_id] = node
        
        # Generate network edges based on similarities and influence patterns
        await self._generate_network_edges(article_analysis)
        
        # Detect and mark community clusters
        self._detect_communities()
    
    async def simulate_propagation(
        self,
        initial_seeds: List[str],
        content_score: float,
        max_timesteps: int = 10,
        propagation_threshold: float = 0.3
    ) -> NetworkSimulationResult:
        """
        Simulate content propagation through the network
        
        Args:
            initial_seeds: Initial personas who see the content
            content_score: Quality/virality score of content (0-1)
            max_timesteps: Maximum simulation steps
            propagation_threshold: Minimum score for propagation
        
        Returns:
            Simulation results with propagation patterns
        """
        propagation_waves = []
        current_wave = set(initial_seeds)
        all_reached = set(initial_seeds)
        influence_map = {node_id: 0.0 for node_id in self.network_graph}
        
        # Initialize influence for seed nodes
        for seed in initial_seeds:
            if seed in self.network_graph:
                influence_map[seed] = self.network_graph[seed].influence_score
        
        # Simulate propagation waves
        for timestep in range(max_timesteps):
            next_wave = set()
            
            for node_id in current_wave:
                if node_id not in self.network_graph:
                    continue
                
                node = self.network_graph[node_id]
                
                # Find all connections from this node
                for edge in self.edges:
                    if edge.source_id != node_id:
                        continue
                    
                    target_id = edge.target_id
                    if target_id in all_reached:
                        continue
                    
                    # Calculate propagation probability
                    prob = self._calculate_propagation_probability(
                        node, 
                        self.network_graph.get(target_id),
                        edge,
                        content_score
                    )
                    
                    # Record propagation event
                    propagated = random.random() < prob
                    event = PropagationEvent(
                        timestamp=timestep,
                        source_node=node_id,
                        target_nodes=[target_id],
                        content_score=content_score,
                        propagation_probability=prob,
                        actual_propagation=propagated
                    )
                    self.propagation_history.append(event)
                    
                    if propagated and prob >= propagation_threshold:
                        next_wave.add(target_id)
                        influence_map[target_id] = (
                            influence_map[node_id] * edge.influence_weight * 
                            self.network_graph[target_id].amplification_factor
                        )
            
            if next_wave:
                propagation_waves.append(list(next_wave))
                all_reached.update(next_wave)
                current_wave = next_wave
            else:
                break  # No more propagation
        
        # Calculate network metrics
        velocity = self._calculate_network_velocity(propagation_waves)
        saturation = self._find_saturation_point(propagation_waves)
        key_influencers = self._identify_key_influencers(influence_map)
        clusters = self._get_activated_clusters(all_reached)
        
        return NetworkSimulationResult(
            total_reach=len(all_reached),
            propagation_waves=propagation_waves,
            influence_map=influence_map,
            key_influencers=key_influencers,
            network_velocity=velocity,
            saturation_point=saturation,
            community_clusters=clusters,
            propagation_events=self.propagation_history
        )
    
    async def _create_network_node(
        self,
        persona: Any,
        index: int,
        article_analysis: Dict[str, Any]
    ) -> NetworkNode:
        """Create a network node from a persona"""
        # Determine influence type based on persona characteristics
        influence_type = await self._determine_influence_type(persona)
        
        # Calculate influence score based on persona attributes
        influence_score = self._calculate_influence_score(persona)
        
        # Determine connectivity based on persona type
        connectivity = self._determine_connectivity(persona, influence_type)
        
        # Set engagement threshold based on persona
        engagement_threshold = self._calculate_engagement_threshold(persona)
        
        # Calculate amplification factor
        amplification = self._calculate_amplification_factor(persona, influence_type)
        
        # Assign network position (for visualization)
        position = self._calculate_network_position(index, influence_score)
        
        return NetworkNode(
            persona_id=getattr(persona, 'id', f"persona_{index}"),
            influence_score=influence_score,
            connectivity=connectivity,
            influence_type=influence_type,
            interests=getattr(persona, 'interests', []),
            engagement_threshold=engagement_threshold,
            amplification_factor=amplification,
            position=position
        )
    
    async def _determine_influence_type(self, persona: Any) -> InfluenceType:
        """Determine the influence type of a persona"""
        # Analyze persona to determine influence type
        occupation = getattr(persona, 'occupation', '')
        values = getattr(persona, 'values', [])
        
        prompt = f"""
        Based on this persona profile, determine their influence type:
        Occupation: {occupation}
        Values: {values}
        
        Choose from: authority, peer, aspirational, viral, niche
        
        Return JSON with:
        - influence_type: the chosen type
        - reasoning: brief explanation
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            data = parse_llm_json_response(str(response.content))
            type_str = data.get("influence_type", "peer")
            return InfluenceType(type_str)
        except Exception:
            return InfluenceType.PEER
    
    async def _generate_network_edges(self, article_analysis: Dict[str, Any]) -> None:
        """Generate edges between network nodes"""
        node_ids = list(self.network_graph.keys())
        
        for i, source_id in enumerate(node_ids):
            source_node = self.network_graph[source_id]
            
            # Connect to a subset of other nodes based on connectivity
            num_connections = min(source_node.connectivity, len(node_ids) - 1)
            
            # Use interest similarity and influence patterns to determine connections
            potential_targets = [
                nid for nid in node_ids 
                if nid != source_id
            ]
            
            # Sort by compatibility
            target_scores = []
            for target_id in potential_targets:
                target_node = self.network_graph[target_id]
                score = self._calculate_connection_score(source_node, target_node)
                target_scores.append((target_id, score))
            
            target_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Create edges to top connections
            for target_id, score in target_scores[:num_connections]:
                edge = NetworkEdge(
                    source_id=source_id,
                    target_id=target_id,
                    influence_weight=score,
                    interaction_frequency=self._determine_interaction_frequency(score),
                    relationship_type=self._determine_relationship_type(
                        source_node, 
                        self.network_graph[target_id]
                    )
                )
                self.edges.append(edge)
    
    def _calculate_influence_score(self, persona: Any) -> float:
        """Calculate influence score for a persona"""
        # Base influence on persona attributes
        base_score = 0.5
        
        # Adjust based on occupation and other factors
        occupation = getattr(persona, 'occupation', '').lower()
        if any(term in occupation for term in ['ceo', 'director', 'manager', 'lead']):
            base_score += 0.2
        if any(term in occupation for term in ['influencer', 'journalist', 'analyst']):
            base_score += 0.15
        
        # Consider personality traits if available
        personality = getattr(persona, 'personality_traits', {})
        if personality.get('openness', 0) > 0.7:
            base_score += 0.1
        if personality.get('extraversion', 0) > 0.7:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _determine_connectivity(self, persona: Any, influence_type: InfluenceType) -> int:
        """Determine number of connections for a persona"""
        base_connections = {
            InfluenceType.AUTHORITY: 15,
            InfluenceType.VIRAL: 20,
            InfluenceType.PEER: 8,
            InfluenceType.ASPIRATIONAL: 12,
            InfluenceType.NICHE: 6
        }
        
        connections = base_connections.get(influence_type, 8)
        
        # Add some randomness
        connections += random.randint(-2, 3)
        
        return max(1, connections)
    
    def _calculate_engagement_threshold(self, persona: Any) -> float:
        """Calculate engagement threshold for a persona"""
        # Base threshold
        threshold = 0.5
        
        # Adjust based on persona characteristics
        info_behavior = getattr(persona, 'information_seeking_behavior', '')
        if info_behavior == 'active':
            threshold -= 0.2
        elif info_behavior == 'passive':
            threshold += 0.2
        
        return max(0.1, min(0.9, threshold))
    
    def _calculate_amplification_factor(
        self, 
        persona: Any, 
        influence_type: InfluenceType
    ) -> float:
        """Calculate how much a persona amplifies content when sharing"""
        base_amplification = {
            InfluenceType.AUTHORITY: 1.5,
            InfluenceType.VIRAL: 2.0,
            InfluenceType.PEER: 1.0,
            InfluenceType.ASPIRATIONAL: 1.3,
            InfluenceType.NICHE: 1.2
        }
        
        return base_amplification.get(influence_type, 1.0)
    
    def _calculate_network_position(self, index: int, influence_score: float) -> Tuple[float, float]:
        """Calculate position in network visualization"""
        # Use influence score to determine radial distance
        radius = 1.0 - (influence_score * 0.7)  # High influence = closer to center
        
        # Distribute nodes around circle
        angle = (index * 2 * np.pi) / 20  # Assume max 20 nodes for distribution
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        
        return (x, y)
    
    def _calculate_connection_score(
        self, 
        source: NetworkNode, 
        target: NetworkNode
    ) -> float:
        """Calculate connection strength between two nodes"""
        # Interest similarity
        shared_interests = set(source.interests) & set(target.interests)
        interest_score = len(shared_interests) / max(1, len(source.interests))
        
        # Influence compatibility
        influence_diff = abs(source.influence_score - target.influence_score)
        influence_compat = 1.0 - influence_diff
        
        # Type compatibility
        type_compat = 0.5  # Default
        if source.influence_type == target.influence_type:
            type_compat = 0.8
        elif source.influence_type == InfluenceType.AUTHORITY and target.influence_type == InfluenceType.ASPIRATIONAL:
            type_compat = 0.9
        
        # Weighted combination
        score = (interest_score * 0.4 + influence_compat * 0.3 + type_compat * 0.3)
        
        return min(1.0, score)
    
    def _determine_interaction_frequency(self, connection_score: float) -> str:
        """Determine interaction frequency based on connection score"""
        if connection_score > 0.7:
            return "high"
        elif connection_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _determine_relationship_type(
        self, 
        source: NetworkNode, 
        target: NetworkNode
    ) -> str:
        """Determine relationship type between nodes"""
        if source.influence_type == InfluenceType.AUTHORITY and target.influence_type == InfluenceType.ASPIRATIONAL:
            return "mentor-follower"
        elif source.influence_type == target.influence_type:
            return "peer"
        elif source.influence_score > target.influence_score + 0.3:
            return "influencer-audience"
        else:
            return "social"
    
    def _calculate_propagation_probability(
        self,
        source: NetworkNode,
        target: Optional[NetworkNode],
        edge: NetworkEdge,
        content_score: float
    ) -> float:
        """Calculate probability of content propagating from source to target"""
        if not target:
            return 0.0
        
        # Base probability from content score
        base_prob = content_score
        
        # Adjust for edge strength
        base_prob *= edge.influence_weight
        
        # Adjust for source influence
        base_prob *= source.influence_score
        
        # Adjust for target engagement threshold
        if base_prob < target.engagement_threshold:
            base_prob *= 0.5  # Reduced but not zero probability
        
        # Adjust for interaction frequency
        freq_multiplier = {"high": 1.2, "medium": 1.0, "low": 0.7}
        base_prob *= freq_multiplier.get(edge.interaction_frequency, 1.0)
        
        return min(1.0, base_prob)
    
    def _calculate_network_velocity(self, propagation_waves: List[List[str]]) -> float:
        """Calculate speed of propagation through network"""
        if not propagation_waves:
            return 0.0
        
        # Calculate average growth rate
        growth_rates = []
        for i in range(1, len(propagation_waves)):
            prev_size = len(propagation_waves[i-1])
            curr_size = len(propagation_waves[i])
            if prev_size > 0:
                growth_rate = curr_size / prev_size
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return 1.0
        
        return sum(growth_rates) / len(growth_rates)
    
    def _find_saturation_point(self, propagation_waves: List[List[str]]) -> int:
        """Find the point where propagation starts to slow down"""
        if len(propagation_waves) < 2:
            return len(propagation_waves)
        
        # Find where growth rate drops below 50% of initial
        initial_size = len(propagation_waves[0]) if propagation_waves else 1
        
        for i, wave in enumerate(propagation_waves[1:], 1):
            if len(wave) < initial_size * 0.5:
                return i
        
        return len(propagation_waves)
    
    def _identify_key_influencers(self, influence_map: Dict[str, float]) -> List[str]:
        """Identify the most influential nodes in propagation"""
        sorted_nodes = sorted(
            influence_map.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Return top 20% or top 5, whichever is smaller
        num_influencers = min(5, max(1, len(sorted_nodes) // 5))
        return [node_id for node_id, _ in sorted_nodes[:num_influencers]]
    
    def _detect_communities(self) -> None:
        """Detect community clusters in the network"""
        # Simple community detection based on connection density
        # This is a placeholder for more sophisticated algorithms
        self.communities = []
        
        visited = set()
        for node_id in self.network_graph:
            if node_id in visited:
                continue
            
            # Find all nodes reachable from this node
            community = self._find_connected_component(node_id, visited)
            if len(community) > 1:
                self.communities.append(community)
    
    def _find_connected_component(self, start_node: str, visited: set) -> List[str]:
        """Find all nodes connected to start_node"""
        component = []
        queue = [start_node]
        
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            
            visited.add(node)
            component.append(node)
            
            # Add all neighbors
            for edge in self.edges:
                if edge.source_id == node and edge.target_id not in visited:
                    queue.append(edge.target_id)
                elif edge.target_id == node and edge.source_id not in visited:
                    queue.append(edge.source_id)
        
        return component
    
    def _get_activated_clusters(self, reached_nodes: set) -> List[List[str]]:
        """Get community clusters that were activated"""
        activated_clusters = []
        
        for community in getattr(self, 'communities', []):
            activated = [node for node in community if node in reached_nodes]
            if len(activated) > len(community) * 0.3:  # At least 30% activated
                activated_clusters.append(activated)
        
        return activated_clusters