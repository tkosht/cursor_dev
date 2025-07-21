# Hierarchical Persona Generation - Integration Guide

## Quick Start

This guide shows how to integrate the hierarchical persona generation system into the existing Article Market Simulator.

## 1. System Integration Points

### 1.1 Replace Existing Persona Generation

**Current System (from requirements):**
```python
# Old approach - role-based fixed evaluation
personas = generate_fixed_personas(["Tech Expert", "Business User", "General Reader"])
```

**New Hierarchical System:**
```python
# New approach - dynamic hierarchical generation
from app.market_simulator.hierarchical_persona_generator import MarketSimulatorPersonaGenerator

generator = MarketSimulatorPersonaGenerator()
result = await generator.generate_population(
    article=article_content,
    population_size=50,
    quality_threshold=0.85
)

personas = result["personas"]  # Highly detailed, realistic personas
```

### 1.2 Integration with Existing LangGraph Flow

```python
# In your existing market simulation graph
from app.market_simulator.hierarchical_persona_generator import (
    build_hierarchical_persona_graph,
    PersonaGenerationState
)

def build_enhanced_market_simulation_graph():
    """Enhanced market simulation with hierarchical personas"""
    
    workflow = StateGraph(MarketSimulationState)
    
    # Phase 1: Article Analysis (existing)
    workflow.add_node("analyze_article", ArticleAnalyzer())
    
    # Phase 2: Hierarchical Persona Generation (NEW)
    # Instead of simple persona generation, use hierarchical system
    persona_subgraph = build_hierarchical_persona_graph()
    workflow.add_node("generate_personas", persona_subgraph)
    
    # Phase 3: Market Simulation (existing, but enhanced)
    workflow.add_node("simulate_market", MarketSimulator())
    
    # Rest of the workflow remains the same
    workflow.add_edge("analyze_article", "generate_personas")
    workflow.add_edge("generate_personas", "simulate_market")
    
    return workflow.compile()
```

## 2. Data Model Integration

### 2.1 Enhance Existing Persona Model

```python
# Extend your existing persona model
from app.market_simulator.hierarchical_persona_generator import HierarchicalPersonaModel

class EnhancedMarketPersona(HierarchicalPersonaModel):
    """Market simulator persona with hierarchical depth"""
    
    def get_article_relevance(self, article: str) -> float:
        """Calculate relevance using hierarchical attributes"""
        relevance_factors = self.simulation_state.get('article_relationship', {})
        return relevance_factors.get('relevance_factors', {}).get('personal', 0.5)
    
    def predict_sharing_behavior(self, social_context: Dict) -> Dict:
        """Predict sharing using psychological layers and micro-details"""
        # Use deep psychological profile
        if self.psychological_layers.get('unconscious_drives', {}).get('validation_seeking'):
            sharing_probability = 0.8
        else:
            sharing_probability = 0.3
            
        # Modify based on micro-details
        if 'morning' in self.micro_details.get('quirks', {}).get('best_sharing_time', ''):
            if datetime.now().hour < 12:
                sharing_probability *= 1.2
                
        return {
            "probability": min(sharing_probability, 1.0),
            "platform_preference": self.behavioral_model.get('content_sharing', {}).get('platforms', {})
        }
```

### 2.2 Update Simulation State

```python
class EnhancedMarketSimulationState(TypedDict):
    """Enhanced state with hierarchical persona data"""
    
    # Existing fields
    article: str
    article_analysis: Dict
    
    # Enhanced persona fields (NEW)
    persona_generation_context: Dict  # Deep context from hierarchical analysis
    persona_hidden_dimensions: Dict   # Unexpected audience segments
    persona_hierarchy: Dict          # Population architecture
    generated_personas: List[HierarchicalPersonaModel]  # Rich personas
    
    # Existing simulation fields
    simulation_results: Dict
    market_metrics: Dict
```

## 3. Practical Usage Examples

### 3.1 Basic Integration

```python
async def run_enhanced_simulation(article: str):
    """Run market simulation with hierarchical personas"""
    
    # Step 1: Generate hierarchical personas
    persona_gen = MarketSimulatorPersonaGenerator()
    persona_result = await persona_gen.generate_population(article)
    
    # Step 2: Extract rich personas
    personas = persona_result["personas"]
    
    # Step 3: Run simulation with enhanced personas
    simulator = MarketReactionSimulator()
    
    # Each persona now has deep attributes for realistic simulation
    for persona in personas:
        # Access hierarchical attributes
        daily_routine = persona.micro_details.get("daily_routines", {})
        info_pattern = persona.behavioral_model.get("information_seeking", {})
        hidden_motivations = persona.psychological_layers.get("unconscious_drives", {})
        
        # Simulate with much more realistic behavior
        reaction = await simulator.simulate_persona_reaction(
            persona=persona,
            article=article,
            time_of_day=daily_routine.get("peak_activity_time", "morning")
        )
    
    return simulation_results
```

### 3.2 Leveraging Emergent Behaviors

```python
async def simulate_with_emergent_behaviors(personas: List[HierarchicalPersonaModel], article: str):
    """Use emergent behaviors for more realistic simulation"""
    
    emergent_insights = []
    
    for persona in personas:
        # Get emergent behaviors from hierarchical generation
        emergent = persona.simulation_state.get('emergent_behaviors', {})
        
        # Example: Paradoxical sharing behavior
        if emergent.get('paradoxical_behaviors'):
            paradox = emergent['paradoxical_behaviors'][0]
            if paradox['trigger_condition'] in article:
                # This persona acts unexpectedly
                unusual_reaction = await simulate_paradoxical_response(
                    persona, paradox, article
                )
                emergent_insights.append({
                    "persona": persona.id,
                    "unexpected_behavior": paradox['description'],
                    "market_impact": unusual_reaction['impact']
                })
    
    return emergent_insights
```

### 3.3 Network Effects with Rich Personas

```python
async def simulate_network_propagation_enhanced(personas: List[HierarchicalPersonaModel]):
    """Enhanced network simulation using detailed persona relationships"""
    
    # Build network from persona attributes
    network = NetworkBuilder()
    
    for persona in personas:
        # Use network attributes from hierarchical generation
        network_attrs = persona.network_attributes
        
        # Add connections based on detailed attributes
        for connection in network_attrs.get('connections', []):
            # Connection strength based on psychological compatibility
            strength = calculate_psychological_compatibility(
                persona.psychological_layers,
                connection['target_psychology']
            )
            network.add_edge(persona.id, connection['target_id'], weight=strength)
    
    # Simulate with psychologically-informed network
    propagation = await network.simulate_information_spread(
        initial_sharers=[p for p in personas if p.hierarchy['archetype_id'] == 'early_adopter'],
        influence_model='psychological_compatibility'
    )
    
    return propagation
```

## 4. Configuration and Tuning

### 4.1 Environment Variables

```bash
# .env configuration for hierarchical generation
PERSONA_GENERATION_MODE=hierarchical  # or 'simple' for old mode
PERSONA_DETAIL_LEVEL=extreme          # minimal, standard, detailed, extreme
PERSONA_VALIDATION_THRESHOLD=0.85     # Quality threshold
PERSONA_GENERATION_TIMEOUT=300        # Seconds for generation
LLM_TEMPERATURE_PERSONAS=0.8          # Higher for more creative personas
```

### 4.2 Quality vs Performance Trade-offs

```python
# Configuration profiles
GENERATION_PROFILES = {
    "quick_test": {
        "population_size": 10,
        "detail_level": "minimal",
        "refinement_passes": 1,
        "validation_threshold": 0.7
    },
    "standard_simulation": {
        "population_size": 30,
        "detail_level": "detailed",
        "refinement_passes": 2,
        "validation_threshold": 0.85
    },
    "deep_analysis": {
        "population_size": 50,
        "detail_level": "extreme",
        "refinement_passes": 3,
        "validation_threshold": 0.9
    }
}

# Usage
profile = GENERATION_PROFILES["standard_simulation"]
personas = await generator.generate_population(
    article=article,
    population_size=profile["population_size"],
    quality_threshold=profile["validation_threshold"]
)
```

## 5. Migration Strategy

### 5.1 Gradual Migration

```python
class HybridPersonaGenerator:
    """Support both old and new persona generation"""
    
    def __init__(self, use_hierarchical: bool = False):
        self.use_hierarchical = use_hierarchical
        self.hierarchical_gen = MarketSimulatorPersonaGenerator() if use_hierarchical else None
        self.simple_gen = SimplePersonaGenerator()  # Existing generator
    
    async def generate(self, article: str, count: int) -> List[Persona]:
        if self.use_hierarchical:
            result = await self.hierarchical_gen.generate_population(article, count)
            return self._convert_to_simple_format(result["personas"])
        else:
            return await self.simple_gen.generate(article, count)
    
    def _convert_to_simple_format(self, hierarchical_personas: List[HierarchicalPersonaModel]):
        """Convert rich personas to simple format for compatibility"""
        return [self._simplify_persona(p) for p in hierarchical_personas]
```

### 5.2 A/B Testing

```python
async def ab_test_persona_systems(article: str):
    """Compare old vs new persona generation"""
    
    # Generate with both systems
    simple_personas = await SimplePersonaGenerator().generate(article, 30)
    hierarchical_result = await MarketSimulatorPersonaGenerator().generate_population(article, 30)
    hierarchical_personas = hierarchical_result["personas"]
    
    # Run parallel simulations
    simple_sim = await run_simulation(simple_personas, article)
    hierarchical_sim = await run_simulation(hierarchical_personas, article)
    
    # Compare results
    comparison = {
        "behavior_diversity": {
            "simple": calculate_diversity(simple_sim),
            "hierarchical": calculate_diversity(hierarchical_sim)
        },
        "prediction_accuracy": {
            "simple": simple_sim.get("confidence", 0),
            "hierarchical": hierarchical_sim.get("confidence", 0)
        },
        "unexpected_insights": {
            "simple": len(simple_sim.get("insights", [])),
            "hierarchical": len(hierarchical_sim.get("insights", []))
        }
    }
    
    return comparison
```

## 6. Performance Considerations

### 6.1 Caching Strategy

```python
from functools import lru_cache
import hashlib

class CachedHierarchicalGenerator(MarketSimulatorPersonaGenerator):
    """Cached version for repeated simulations"""
    
    def __init__(self):
        super().__init__()
        self._cache = {}
    
    async def generate_population(self, article: str, population_size: int, quality_threshold: float):
        # Cache key based on article content and parameters
        cache_key = hashlib.md5(
            f"{article[:1000]}_{population_size}_{quality_threshold}".encode()
        ).hexdigest()
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = await super().generate_population(article, population_size, quality_threshold)
        self._cache[cache_key] = result
        return result
```

### 6.2 Parallel Processing

```python
async def generate_large_population_efficiently(article: str, size: int = 100):
    """Generate large populations efficiently"""
    
    # Split into batches
    batch_size = 20
    batches = [size // 5] * 5  # 5 batches of 20
    
    # Generate batches in parallel
    tasks = []
    for batch_num, batch_size in enumerate(batches):
        task = generate_batch(article, batch_size, batch_num)
        tasks.append(task)
    
    # Combine results
    batch_results = await asyncio.gather(*tasks)
    all_personas = []
    for batch in batch_results:
        all_personas.extend(batch["personas"])
    
    return {
        "personas": all_personas,
        "population_metrics": calculate_combined_metrics(batch_results)
    }
```

## 7. Monitoring and Debugging

### 7.1 Logging Persona Generation

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hierarchical_personas")

class LoggedPersonaGenerator(MarketSimulatorPersonaGenerator):
    """Generator with detailed logging"""
    
    async def generate_population(self, article: str, population_size: int, quality_threshold: float):
        logger.info(f"Starting hierarchical generation for {population_size} personas")
        
        start_time = time.time()
        result = await super().generate_population(article, population_size, quality_threshold)
        
        logger.info(f"Generation completed in {time.time() - start_time:.2f}s")
        logger.info(f"Quality scores: {result['population_metrics']['quality_scores']}")
        
        # Log interesting personas
        for persona in result["personas"][:3]:
            if persona.hierarchy.get("archetype_id") in ["paradox", "threshold"]:
                logger.info(f"Interesting persona: {persona.id} - {persona.hierarchy['archetype_id']}")
        
        return result
```

## 8. Best Practices

1. **Start with smaller populations** during development (10-20 personas)
2. **Use caching** for repeated simulations with the same article
3. **Monitor quality scores** and adjust thresholds based on your needs
4. **Leverage emergent behaviors** for unexpected insights
5. **Profile performance** to find the right detail/speed balance

## 9. Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Generation timeout | Too many personas or too high detail | Reduce population size or detail level |
| Low quality scores | Inconsistent personas | Increase refinement passes |
| Memory usage | Large populations in memory | Use batching and cleanup |
| Slow simulation | Too much detail processing | Cache computed attributes |

## 10. Next Steps

1. **Review** the full technical design: `hierarchical-persona-generation-system.md`
2. **Explore** the implementation: `app/market_simulator/hierarchical_persona_generator.py`
3. **Try** the demo notebook: `app/notebook/hierarchical_persona_demo.ipynb`
4. **Run** the tests: `pytest tests/unit/test_hierarchical_persona_generator.py`

The hierarchical persona generation system provides a significant upgrade to market simulation realism while maintaining compatibility with existing systems.