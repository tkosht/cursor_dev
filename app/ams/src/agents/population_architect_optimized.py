"""Optimized Population Architect for Article Market Simulator.

This module designs population hierarchies for realistic article distribution.
Optimized version reduces prompt size and improves performance.
"""

import asyncio
from typing import Any, cast

from src.utils.json_parser import parse_llm_json_response
from src.utils.llm_factory import create_llm


class PopulationArchitect:
    """Design population hierarchies and network structures.

    Optimized to reduce prompt sizes and improve performance.
    """

    def __init__(self) -> None:
        self.llm = create_llm()

    async def design_population_hierarchy(
        self, context: dict[str, Any], target_size: int = 10
    ) -> dict[str, Any]:
        """Design a hierarchical population structure.

        Args:
            context: Analysis context from DeepContextAnalyzer
            target_size: Target number of personas

        Returns:
            Dict containing:
                - hierarchy: Major segments, sub-segments, micro-clusters
                - network_topology: Network structure
                - influence_map: Influence patterns
        """
        try:
            # Extract only essential context info
            essential_context = self._extract_essential_context(context)

            # Design major segments (3-5)
            major_segments = await self._design_major_segments(essential_context)

            # Design sub-segments concurrently
            sub_segments = await self._design_sub_segments_parallel(
                major_segments, essential_context
            )

            # Design micro-clusters based on segments
            micro_clusters = self._design_micro_clusters(major_segments, sub_segments, target_size)

            # Allocate personas to slots
            persona_slots = self._allocate_persona_slots(
                major_segments, sub_segments, micro_clusters, target_size
            )

            return {
                "hierarchy": {
                    "major_segments": major_segments,
                    "sub_segments": sub_segments,
                    "micro_clusters": micro_clusters,
                    "persona_slots": persona_slots,
                },
                "network_topology": self._design_network_topology(persona_slots),
                "influence_map": self._design_influence_patterns(persona_slots),
            }

        except Exception:
            # Return default structure on error
            return {
                "hierarchy": {
                    "major_segments": [],
                    "sub_segments": {},
                    "micro_clusters": {},
                    "persona_slots": [],
                },
                "network_topology": {"type": "random", "density": 0.1},
                "influence_map": {
                    "influencer_nodes": [],
                    "influence_paths": [],
                },
            }

    def _extract_essential_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract only essential information from context to reduce prompt size."""
        core_context = context.get("core_context", {})

        return {
            "domain": core_context.get("domain_analysis", {}).get("primary_domain", "general"),
            "complexity": core_context.get("domain_analysis", {}).get("technical_complexity", 5),
            "stakeholders": core_context.get("stakeholder_mapping", {}).get("beneficiaries", [])[
                :3
            ],
            "emotional_tone": core_context.get("emotional_landscape", {}).get(
                "controversy_potential", "medium"
            ),
            "time_sensitivity": core_context.get("temporal_aspects", {}).get(
                "time_sensitivity", "medium"
            ),
            "complexity_score": context.get("complexity_score", 0.5),
            "reach_potential": context.get("reach_potential", 0.5),
        }

    async def _design_major_segments(
        self, essential_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Design major population segments based on essential context."""
        # Much shorter prompt with only essential context
        segment_prompt = f"""
        Article domain: {essential_context['domain']}
        Complexity level: {essential_context['complexity']}/10
        Key stakeholders: {', '.join(essential_context['stakeholders'][:3])}
        Emotional tone: {essential_context['emotional_tone']}

        Design 3-5 major population segments considering:
        - Unexpected intersections and bridge populations
        - Temporal relationships (early adopters, etc.)
        - Emotional and professional stakes
        - Different cognitive styles

        Return JSON array with segments containing:
        - id, name, percentage (total 100)
        - characteristics (3-5 key traits)
        - relationship_to_article
        - unexpected_traits (1-2 non-obvious traits)
        """

        try:
            response = await self.llm.ainvoke(segment_prompt)
            segments = parse_llm_json_response(str(response.content))

            if isinstance(segments, dict):
                segments = segments.get("segments", [])

            # Normalize percentages
            total_percentage = sum(s.get("percentage", 0) for s in segments)
            if total_percentage > 0:
                for segment in segments:
                    segment["percentage"] = (segment.get("percentage", 0) / total_percentage) * 100

            return cast(list[dict[str, Any]], segments)

        except Exception:
            return []

    async def _design_sub_segments_parallel(
        self, major_segments: list[dict[str, Any]], essential_context: dict[str, Any]
    ) -> dict[str, list[dict[str, Any]]]:
        """Design sub-segments for all major segments in parallel."""
        tasks = []
        for segment in major_segments:
            task = self._design_sub_segments_for_one(segment, essential_context)
            tasks.append(task)

        # Execute all sub-segment designs in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        sub_segments: dict[str, list[dict[str, Any]]] = {}
        for i, segment in enumerate(major_segments):
            if isinstance(results[i], list):
                sub_segments[segment["id"]] = results[i]
            else:
                sub_segments[segment["id"]] = []

        return sub_segments

    async def _design_sub_segments_for_one(
        self, segment: dict[str, Any], essential_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Design sub-segments within a major segment."""
        # Minimal prompt without full context
        sub_segment_prompt = f"""
        Major segment: {segment['name']} ({segment.get('percentage', 25):.0f}%)
        Characteristics: {', '.join(segment.get('characteristics', [])[:3])}
        Article domain: {essential_context['domain']}

        Create 2-4 sub-segments with variations in:
        - Experience levels
        - Information sources
        - Network positions
        - Action likelihood

        Return JSON array with: id, name, percentage_of_segment, characteristics (2-3 traits)
        """

        try:
            response = await self.llm.ainvoke(sub_segment_prompt)
            sub_segs = parse_llm_json_response(str(response.content))

            if isinstance(sub_segs, dict):
                sub_segs = sub_segs.get("sub_segments", [])

            return cast(list[dict[str, Any]], sub_segs)

        except Exception:
            return []

    def _design_micro_clusters(
        self,
        major_segments: list[dict[str, Any]],
        sub_segments: dict[str, list[dict[str, Any]]],
        target_size: int,
    ) -> dict[str, list[dict[str, Any]]]:
        """Design micro-clusters based on segments."""
        micro_clusters = {}

        for segment in major_segments:
            segment_id = segment["id"]
            sub_segs = sub_segments.get(segment_id, [])

            clusters = []
            for sub_seg in sub_segs:
                # Create 1-2 micro clusters per sub-segment
                cluster_count = min(2, max(1, target_size // 10))
                for i in range(cluster_count):
                    clusters.append(
                        {
                            "id": f"{sub_seg['id']}_cluster_{i}",
                            "name": f"{sub_seg['name']} Group {i+1}",
                            "size": 1 + (i % 2),  # Alternate between 1-2 people
                            "sub_segment_id": sub_seg["id"],
                            "characteristics": sub_seg.get("characteristics", []),
                        }
                    )

            micro_clusters[segment_id] = clusters

        return micro_clusters

    def _allocate_persona_slots(
        self,
        major_segments: list[dict[str, Any]],
        sub_segments: dict[str, list[dict[str, Any]]],
        micro_clusters: dict[str, list[dict[str, Any]]],
        target_size: int,
    ) -> list[dict[str, Any]]:
        """Allocate personas to specific slots in the hierarchy."""
        slots = []
        persona_id = 0

        for segment in major_segments:
            segment_id = segment["id"]
            segment_percentage = segment.get("percentage", 25) / 100
            segment_personas = int(target_size * segment_percentage)

            sub_segs = sub_segments.get(segment_id, [])
            clusters = micro_clusters.get(segment_id, [])

            # Distribute personas across sub-segments
            for i in range(segment_personas):
                if sub_segs:
                    sub_seg = sub_segs[i % len(sub_segs)]
                    cluster = clusters[i % len(clusters)] if clusters else None

                    slots.append(
                        {
                            "id": f"persona_{persona_id}",
                            "major_segment": segment_id,
                            "sub_segment": sub_seg["id"],
                            "micro_cluster": (cluster["id"] if cluster else None),
                            "network_position": self._assign_network_position(i, segment_personas),
                        }
                    )
                    persona_id += 1

        # Ensure we have exactly target_size personas
        while len(slots) < target_size:
            slots.append(
                {
                    "id": f"persona_{len(slots)}",
                    "major_segment": major_segments[0]["id"],
                    "sub_segment": None,
                    "micro_cluster": None,
                    "network_position": {"type": "peripheral"},
                }
            )

        return slots[:target_size]

    def _assign_network_position(self, index: int, total_in_segment: int) -> dict[str, Any]:
        """Assign network position based on index."""
        if index == 0:
            return {"type": "hub", "influence": 0.9}
        elif index < total_in_segment * 0.2:
            return {"type": "connector", "influence": 0.7}
        elif index < total_in_segment * 0.5:
            return {"type": "active", "influence": 0.5}
        else:
            return {"type": "peripheral", "influence": 0.3}

    def _design_network_topology(self, persona_slots: list[dict[str, Any]]) -> dict[str, Any]:
        """Design the network topology."""
        hub_count = sum(
            1 for p in persona_slots if p.get("network_position", {}).get("type") == "hub"
        )

        return {
            "type": "scale-free",
            "density": 0.15,
            "clustering_coefficient": 0.3,
            "hub_nodes": hub_count,
            "average_path_length": 3.5,
        }

    def _design_influence_patterns(self, persona_slots: list[dict[str, Any]]) -> dict[str, Any]:
        """Design influence patterns."""
        influencers = [
            p["id"]
            for p in persona_slots
            if p.get("network_position", {}).get("influence", 0) > 0.7
        ]

        return {
            "influencer_nodes": influencers,
            "influence_paths": [
                {"from": influencers[i], "to": f"persona_{i+5}", "weight": 0.8}
                for i in range(min(3, len(influencers)))
            ],
            "cascade_probability": 0.6,
        }
