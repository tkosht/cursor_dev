"""
Comprehensive usage examples for the Multi-Agent Simulation Framework.

This module demonstrates various ways to use the framework for different
market simulation scenarios.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import numpy as np

# Import the simulation framework
from simulation_framework import (
    SimulationEngine,
    SimulationController,
    VisualizationBridge,
    VisualizationServer,
    DataExporter,
    SimulationEvent
)

from simulation_framework.plugins import (
    ProductLaunchPlugin,
    PricingStrategyPlugin,
    get_plugin
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Basic Product Launch Simulation
# ============================================================================

async def run_product_launch_simulation():
    """Run a basic product launch simulation"""
    
    logger.info("Starting Product Launch Simulation")
    
    # Configuration
    config = {
        # Simulation settings
        'tick_rate': 0.1,  # 100ms per tick
        'time_scale': 10.0,  # 10x speed (1 tick = 1 hour simulated)
        'real_time': False,  # Run as fast as possible
        
        # Plugin-specific settings
        'num_consumers': 500,
        'consumer_segments': [
            {
                'name': 'innovators',
                'size_pct': 0.05,
                'adoption_threshold': 0.2,
                'budget_range': (1000, 3000),
                'social_influence': 0.9,
                'price_sensitivity': 0.3
            },
            {
                'name': 'early_adopters',
                'size_pct': 0.15,
                'adoption_threshold': 0.4,
                'budget_range': (500, 2000),
                'social_influence': 0.7,
                'price_sensitivity': 0.6
            },
            {
                'name': 'early_majority',
                'size_pct': 0.35,
                'adoption_threshold': 0.6,
                'budget_range': (300, 1500),
                'social_influence': 0.5,
                'price_sensitivity': 1.0
            },
            {
                'name': 'late_majority',
                'size_pct': 0.35,
                'adoption_threshold': 0.8,
                'budget_range': (200, 1000),
                'social_influence': 0.3,
                'price_sensitivity': 1.3
            },
            {
                'name': 'laggards',
                'size_pct': 0.10,
                'adoption_threshold': 0.9,
                'budget_range': (100, 500),
                'social_influence': 0.1,
                'price_sensitivity': 1.5
            }
        ],
        'marketing_budget': 2000000,
        'pricing_strategy': 'penetration',
        'initial_price': 99.99,
        'market_size': 100000,
        'market_growth_rate': 0.02
    }
    
    # Create simulation
    plugin = ProductLaunchPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Setup visualization bridge
    bridge = VisualizationBridge(engine)
    
    # Setup data exporter
    exporter = DataExporter(bridge)
    
    # Add custom event handlers
    viral_moments = []
    
    async def track_viral_moments(event: SimulationEvent):
        if event.event_type == 'product_purchased':
            # Check if purchase rate is increasing rapidly
            viral_moments.append({
                'time': engine.clock.current_time,
                'source': event.source_id
            })
    
    engine.event_bus.subscribe('product_purchased', track_viral_moments)
    
    # Run simulation
    logger.info("Running simulation for 30 days (simulated time)")
    final_state = await engine.run(duration=720)  # 720 hours = 30 days
    
    # Get final metrics
    metrics = engine.get_metrics()
    
    # Export data
    exporter.export_to_json('product_launch_results.json')
    exporter.export_metrics_to_csv('product_launch_metrics.csv')
    
    # Print results
    print("\n=== Product Launch Simulation Results ===")
    print(f"Total simulation time: {engine.clock.current_time:.1f} hours")
    print(f"Final adoption rate: {metrics['adoption_rate']['current']:.2%}")
    print(f"Total revenue: ${metrics['revenue']['current']:,.2f}")
    print(f"Customer satisfaction: {metrics['customer_satisfaction']['current']:.2f}/1.0")
    print(f"Viral moments captured: {len(viral_moments)}")
    
    return metrics, bridge


# ============================================================================
# Example 2: Competitive Pricing Simulation
# ============================================================================

async def run_pricing_competition():
    """Run a competitive pricing simulation"""
    
    logger.info("Starting Competitive Pricing Simulation")
    
    # Configuration
    config = {
        'tick_rate': 0.05,  # 50ms per tick
        'time_scale': 1.0,
        'real_time': False,
        
        # Market configuration
        'num_customers': 200,
        'num_retailers': 5,
        'pricing_algorithms': [
            'ml_based',      # Advanced ML pricing
            'demand_based',  # Demand elasticity based
            'rule_based',    # Simple rules
            'ml_based',      # Another ML competitor
            'demand_based'   # Another demand-based
        ],
        'initial_price': 100.0,
        'base_demand': 1000.0,
        'demand_volatility': 0.15,
        'price_transparency': 0.7  # 70% price visibility
    }
    
    # Create simulation
    plugin = PricingStrategyPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Track price convergence
    price_history = []
    
    async def track_prices(event: SimulationEvent):
        if event.event_type == 'metrics_update':
            price_history.append({
                'time': engine.clock.current_time,
                'avg_price': event.payload.get('average_price', 0),
                'dispersion': event.payload.get('price_dispersion', 0)
            })
    
    engine.event_bus.subscribe('metrics_update', track_prices)
    
    # Run simulation
    await engine.run(max_ticks=1000)
    
    # Analyze results
    metrics = engine.get_metrics()
    
    print("\n=== Pricing Competition Results ===")
    print(f"Final average price: ${metrics['average_price']['current']:.2f}")
    print(f"Price dispersion: {metrics['price_dispersion']['current']:.3f}")
    print(f"Market efficiency: {metrics['market_efficiency']['aggregated']:.2%}")
    print(f"Total market revenue: ${metrics['total_revenue']['current']:,.2f}")
    
    # Plot price convergence
    if price_history:
        times = [p['time'] for p in price_history]
        prices = [p['avg_price'] for p in price_history]
        dispersions = [p['dispersion'] for p in price_history]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(times, prices)
        ax1.set_title('Average Market Price Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Price ($)')
        ax1.grid(True)
        
        ax2.plot(times, dispersions)
        ax2.set_title('Price Dispersion Over Time')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Coefficient of Variation')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('price_convergence.png')
        logger.info("Saved price convergence plot to price_convergence.png")
    
    return metrics


# ============================================================================
# Example 3: Parameter Sweep Experiment
# ============================================================================

async def run_parameter_sweep():
    """Run parameter sweep to find optimal marketing budget"""
    
    logger.info("Starting Parameter Sweep Experiment")
    
    # Base configuration
    base_config = {
        'tick_rate': 0.1,
        'time_scale': 20.0,  # Faster simulation
        'real_time': False,
        'num_consumers': 200,  # Smaller for faster runs
        'initial_price': 100.0,
        'pricing_strategy': 'penetration'
    }
    
    # Marketing budgets to test
    marketing_budgets = [100000, 500000, 1000000, 2000000, 5000000]
    
    # Run sweep
    plugin = ProductLaunchPlugin()
    base_engine = SimulationEngine(plugin, base_config)
    controller = SimulationController(base_engine)
    
    results = await controller.run_parameter_sweep(
        parameter_name='marketing_budget',
        values=marketing_budgets,
        base_config=base_config
    )
    
    # Analyze results
    print("\n=== Parameter Sweep Results ===")
    print("Marketing Budget -> Final Revenue (ROI)")
    print("-" * 40)
    
    best_roi = -float('inf')
    best_budget = None
    
    for budget, state in results.items():
        # Get final metrics from state
        revenue = state.custom_state.get('final_revenue', 0)
        roi = (revenue - budget) / budget if budget > 0 else 0
        
        print(f"${budget:,} -> ${revenue:,.0f} (ROI: {roi:.1%})")
        
        if roi > best_roi:
            best_roi = roi
            best_budget = budget
    
    print(f"\nOptimal marketing budget: ${best_budget:,} with ROI of {best_roi:.1%}")
    
    return results


# ============================================================================
# Example 4: A/B Testing Different Strategies
# ============================================================================

async def run_ab_test():
    """Run A/B test comparing pricing strategies"""
    
    logger.info("Starting A/B Test")
    
    # Configuration A: Aggressive penetration pricing
    config_a = {
        'tick_rate': 0.1,
        'time_scale': 10.0,
        'num_consumers': 300,
        'marketing_budget': 1000000,
        'pricing_strategy': 'penetration',
        'initial_price': 79.99,
        'name': 'Aggressive Penetration'
    }
    
    # Configuration B: Premium pricing
    config_b = {
        'tick_rate': 0.1,
        'time_scale': 10.0,
        'num_consumers': 300,
        'marketing_budget': 1000000,
        'pricing_strategy': 'premium',
        'initial_price': 149.99,
        'name': 'Premium Strategy'
    }
    
    # Run A/B test
    plugin = ProductLaunchPlugin()
    engine = SimulationEngine(plugin, config_a)
    controller = SimulationController(engine)
    
    results = await controller.run_ab_test(config_a, config_b, num_runs=5)
    
    # Analyze results
    print("\n=== A/B Test Results (5 runs each) ===")
    
    # Calculate statistics for each configuration
    for config_name, config_results in [('A: Aggressive', results['config_a']), 
                                        ('B: Premium', results['config_b'])]:
        revenues = [state.custom_state.get('final_revenue', 0) for state in config_results]
        adoptions = [state.custom_state.get('final_adoption', 0) for state in config_results]
        
        print(f"\n{config_name}:")
        print(f"  Avg Revenue: ${np.mean(revenues):,.2f} (±${np.std(revenues):,.2f})")
        print(f"  Avg Adoption: {np.mean(adoptions):.1%} (±{np.std(adoptions):.1%})")
    
    return results


# ============================================================================
# Example 5: Real-time Visualization with WebSocket
# ============================================================================

async def run_with_visualization():
    """Run simulation with real-time visualization server"""
    
    logger.info("Starting Simulation with Real-time Visualization")
    
    # Configuration
    config = {
        'tick_rate': 0.5,  # Slower for visualization
        'real_time': True,  # Run in real-time
        'num_consumers': 1000,
        'num_retailers': 8,
        'pricing_algorithms': ['ml_based'] * 4 + ['demand_based'] * 4,
        'initial_price': 100.0
    }
    
    # Create simulation
    plugin = PricingStrategyPlugin()
    engine = SimulationEngine(plugin, config)
    
    # Setup visualization
    bridge = VisualizationBridge(engine, {
        'sample_rate': 1,  # Sample every tick
        'buffer_size': 500
    })
    
    viz_server = VisualizationServer(bridge, port=8765)
    
    # Print connection info
    print("\n=== Visualization Server Started ===")
    print("WebSocket URL: ws://localhost:8765")
    print("Open your browser and connect to visualize in real-time")
    print("Press Ctrl+C to stop\n")
    
    # Run simulation and server concurrently
    try:
        await asyncio.gather(
            engine.run(duration=300),  # Run for 5 minutes
            viz_server.start()
        )
    except KeyboardInterrupt:
        logger.info("Stopping simulation...")
    
    return engine.get_metrics()


# ============================================================================
# Example 6: Custom Plugin Creation
# ============================================================================

async def demonstrate_custom_plugin():
    """Demonstrate how to create a custom plugin"""
    
    from simulation_framework.core import IAgent, IEnvironment, ISimulationPlugin
    
    class SimpleSupplyChainPlugin(ISimulationPlugin):
        """Simple supply chain simulation plugin"""
        
        def get_plugin_info(self) -> Dict[str, Any]:
            return {
                'name': 'Simple Supply Chain',
                'version': '0.1.0',
                'description': 'Basic supply chain simulation'
            }
        
        def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
            # Create suppliers, manufacturers, and retailers
            agents = []
            
            # Implementation would go here...
            # This is just a demonstration of the structure
            
            return agents
        
        def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
            # Create supply chain environment
            # Implementation would go here...
            pass
        
        def get_metrics_definitions(self) -> Dict[str, Any]:
            return {
                'supply_chain_efficiency': {
                    'calculator': lambda a, e, h: 0.85,  # Placeholder
                    'aggregator': lambda x: np.mean(x) if x else 0
                },
                'inventory_costs': {
                    'calculator': lambda a, e, h: 10000,  # Placeholder
                    'aggregator': lambda x: sum(x) if x else 0
                }
            }
    
    print("\n=== Custom Plugin Example ===")
    print("Created custom SimpleSupplyChainPlugin")
    print("This demonstrates the plugin interface structure")
    print("Full implementation would include agent behaviors and environment dynamics")
    
    # You would then use it like any other plugin:
    # plugin = SimpleSupplyChainPlugin()
    # engine = SimulationEngine(plugin, config)
    # await engine.run()


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Run all examples"""
    
    print("=" * 60)
    print("Multi-Agent Simulation Framework Examples")
    print("=" * 60)
    
    # Example 1: Product Launch
    print("\n1. Running Product Launch Simulation...")
    metrics1, bridge1 = await run_product_launch_simulation()
    
    # Example 2: Pricing Competition
    print("\n2. Running Pricing Competition...")
    metrics2 = await run_pricing_competition()
    
    # Example 3: Parameter Sweep
    print("\n3. Running Parameter Sweep...")
    sweep_results = await run_parameter_sweep()
    
    # Example 4: A/B Testing
    print("\n4. Running A/B Test...")
    ab_results = await run_ab_test()
    
    # Example 5: Custom Plugin Demo
    print("\n5. Custom Plugin Demonstration...")
    await demonstrate_custom_plugin()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    
    # Note: Example 5 (real-time visualization) is not run automatically
    # as it requires manual interaction. To run it:
    # await run_with_visualization()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or run specific examples:
    # asyncio.run(run_product_launch_simulation())
    # asyncio.run(run_pricing_competition())
    # asyncio.run(run_with_visualization())