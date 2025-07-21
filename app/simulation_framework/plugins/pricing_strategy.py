"""
Dynamic Pricing Strategy Simulation Plugin

This plugin simulates competitive pricing dynamics in a multi-retailer market,
including price elasticity, inventory management, and dynamic pricing algorithms.
"""

import random
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import deque

from ..core import (
    IAgent, IAction, IEnvironment, ISimulationPlugin,
    SimulationEvent
)


# ============================================================================
# Pricing Algorithms
# ============================================================================

class PricingAlgorithm:
    """Base class for pricing algorithms"""
    
    def calculate_price(
        self,
        current_price: float,
        demand_history: List[float],
        competitor_prices: List[float],
        inventory_level: float,
        cost: float
    ) -> float:
        """Calculate new price based on inputs"""
        raise NotImplementedError


class RuleBasedPricing(PricingAlgorithm):
    """Simple rule-based pricing"""
    
    def calculate_price(
        self,
        current_price: float,
        demand_history: List[float],
        competitor_prices: List[float],
        inventory_level: float,
        cost: float
    ) -> float:
        avg_competitor = np.mean(competitor_prices) if competitor_prices else current_price
        
        # High inventory -> lower price
        if inventory_level > 0.8:
            target_price = current_price * 0.95
        # Low inventory -> higher price
        elif inventory_level < 0.2:
            target_price = current_price * 1.05
        else:
            # Match market
            target_price = avg_competitor
        
        # Ensure minimum margin
        min_price = cost * 1.1
        return max(min_price, target_price)


class DemandBasedPricing(PricingAlgorithm):
    """Pricing based on demand elasticity"""
    
    def __init__(self, elasticity: float = -1.5):
        self.elasticity = elasticity
    
    def calculate_price(
        self,
        current_price: float,
        demand_history: List[float],
        competitor_prices: List[float],
        inventory_level: float,
        cost: float
    ) -> float:
        if len(demand_history) < 2:
            return current_price
        
        # Calculate demand trend
        recent_demand = np.mean(demand_history[-5:]) if len(demand_history) >= 5 else np.mean(demand_history)
        older_demand = np.mean(demand_history[:-5]) if len(demand_history) > 5 else demand_history[0]
        
        demand_change = (recent_demand - older_demand) / max(older_demand, 1)
        
        # Adjust price based on demand elasticity
        price_adjustment = -demand_change / self.elasticity
        new_price = current_price * (1 + price_adjustment)
        
        # Ensure minimum margin
        min_price = cost * 1.15
        return max(min_price, new_price)


class MLPricing(PricingAlgorithm):
    """Machine learning-based pricing (simplified)"""
    
    def __init__(self):
        # Simplified ML model using weighted features
        self.feature_weights = {
            'demand_trend': 0.3,
            'competitor_gap': 0.25,
            'inventory_pressure': 0.25,
            'margin_target': 0.2
        }
    
    def calculate_price(
        self,
        current_price: float,
        demand_history: List[float],
        competitor_prices: List[float],
        inventory_level: float,
        cost: float
    ) -> float:
        features = {}
        
        # Demand trend feature
        if len(demand_history) >= 2:
            trend = (demand_history[-1] - demand_history[-2]) / max(demand_history[-2], 1)
            features['demand_trend'] = np.clip(trend, -0.5, 0.5)
        else:
            features['demand_trend'] = 0
        
        # Competitor gap feature
        if competitor_prices:
            avg_comp = np.mean(competitor_prices)
            features['competitor_gap'] = (avg_comp - current_price) / current_price
        else:
            features['competitor_gap'] = 0
        
        # Inventory pressure feature
        features['inventory_pressure'] = (0.5 - inventory_level) * 0.2
        
        # Margin target feature
        current_margin = (current_price - cost) / current_price
        target_margin = 0.25
        features['margin_target'] = (target_margin - current_margin) * 0.5
        
        # Calculate price adjustment
        adjustment = sum(
            features[key] * self.feature_weights[key]
            for key in features
        )
        
        new_price = current_price * (1 + np.clip(adjustment, -0.1, 0.1))
        
        # Ensure minimum margin
        min_price = cost * 1.12
        return max(min_price, new_price)


# ============================================================================
# Actions
# ============================================================================

@dataclass
class SetPriceAction(IAction):
    """Set product price action"""
    product_id: str
    new_price: float
    old_price: float
    
    def __init__(self, product_id: str, new_price: float, old_price: float):
        super().__init__("set_price")
        self.product_id = product_id
        self.new_price = new_price
        self.old_price = old_price
    
    def validate(self, agent: IAgent, environment: IEnvironment) -> bool:
        """Validate price is positive and reasonable"""
        return self.new_price > 0 and self.new_price < self.old_price * 2
    
    async def execute(self, agent: IAgent, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute price change"""
        return [SimulationEvent(
            timestamp=datetime.now(),
            source_id=agent.agent_id,
            event_type="price_updated",
            payload={
                "retailer_id": agent.agent_id,
                "product_id": self.product_id,
                "old_price": self.old_price,
                "new_price": self.new_price,
                "change_pct": ((self.new_price - self.old_price) / self.old_price) * 100
            }
        )]


@dataclass
class RestockAction(IAction):
    """Restock inventory action"""
    product_id: str
    quantity: int
    unit_cost: float
    
    def __init__(self, product_id: str, quantity: int, unit_cost: float):
        super().__init__("restock")
        self.product_id = product_id
        self.quantity = quantity
        self.unit_cost = unit_cost
    
    def validate(self, agent: IAgent, environment: IEnvironment) -> bool:
        """Check if retailer has budget for restock"""
        if hasattr(agent, 'cash_balance'):
            return agent.cash_balance >= (self.quantity * self.unit_cost)
        return True
    
    async def execute(self, agent: IAgent, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute restock"""
        return [SimulationEvent(
            timestamp=datetime.now(),
            source_id=agent.agent_id,
            event_type="inventory_restocked",
            payload={
                "retailer_id": agent.agent_id,
                "product_id": self.product_id,
                "quantity": self.quantity,
                "unit_cost": self.unit_cost,
                "total_cost": self.quantity * self.unit_cost
            }
        )]


# ============================================================================
# Agents
# ============================================================================

class PriceSensitiveCustomerAgent(IAgent):
    """Customer agent with price sensitivity"""
    
    def __init__(
        self,
        agent_id: str,
        price_elasticity: float,
        reference_price: float,
        purchase_frequency: float,
        budget: float = 1000.0
    ):
        super().__init__(agent_id)
        self.price_elasticity = price_elasticity
        self.reference_price = reference_price
        self.purchase_frequency = purchase_frequency  # Purchases per time unit
        self.budget = budget
        
        # State
        self.last_purchase_time = 0.0
        self.price_memory = deque(maxlen=10)  # Remember last 10 prices
        self.preferred_retailer = None
        self.purchases = []
        
        self._state = {
            'price_elasticity': price_elasticity,
            'last_purchase_time': self.last_purchase_time,
            'preferred_retailer': self.preferred_retailer
        }
    
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]) -> None:
        """Track price changes"""
        for event in events:
            if event.event_type == "price_updated":
                self.price_memory.append({
                    'retailer': event.payload['retailer_id'],
                    'price': event.payload['new_price'],
                    'timestamp': event.timestamp
                })
    
    async def decide(self) -> List[IAction]:
        """Decide whether and where to purchase"""
        actions = []
        
        # Get current time from environment
        current_time = datetime.now().timestamp()  # Simplified
        
        # Check if it's time to purchase
        time_since_last = current_time - self.last_purchase_time
        purchase_probability = 1 - math.exp(-self.purchase_frequency * time_since_last)
        
        if random.random() < purchase_probability:
            # Find best price from memory
            if self.price_memory:
                best_option = min(self.price_memory, key=lambda x: x['price'])
                
                # Calculate purchase probability based on price
                price_ratio = best_option['price'] / self.reference_price
                elasticity_factor = math.pow(price_ratio, self.price_elasticity)
                
                if random.random() < elasticity_factor and self.budget >= best_option['price']:
                    # Decide to purchase
                    self.preferred_retailer = best_option['retailer']
                    self.last_purchase_time = current_time
                    
                    # Record purchase intent (actual purchase handled by environment)
                    self._action_queue.append({
                        'type': 'purchase',
                        'retailer': best_option['retailer'],
                        'price': best_option['price']
                    })
        
        return actions
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute purchases"""
        events = []
        
        for action in self._action_queue:
            if action['type'] == 'purchase':
                self.budget -= action['price']
                self.purchases.append({
                    'timestamp': datetime.now(),
                    'retailer': action['retailer'],
                    'price': action['price']
                })
                
                events.append(SimulationEvent(
                    timestamp=datetime.now(),
                    source_id=self.agent_id,
                    event_type="customer_purchase",
                    payload={
                        "customer_id": self.agent_id,
                        "retailer_id": action['retailer'],
                        "price": action['price'],
                        "elasticity": self.price_elasticity
                    }
                ))
        
        self._action_queue.clear()
        
        # Update state
        self._state.update({
            'last_purchase_time': self.last_purchase_time,
            'preferred_retailer': self.preferred_retailer,
            'budget': self.budget
        })
        
        return events


class RetailerAgent(IAgent):
    """Retailer with dynamic pricing"""
    
    def __init__(
        self,
        agent_id: str,
        pricing_algorithm: str,
        inventory_capacity: int,
        initial_inventory: int,
        cost_structure: Dict[str, float],
        initial_price: float = 100.0,
        cash_balance: float = 100000.0
    ):
        super().__init__(agent_id)
        
        # Setup pricing algorithm
        self.pricing_algorithm = self._create_pricing_algorithm(pricing_algorithm)
        
        # Inventory management
        self.inventory_capacity = inventory_capacity
        self.current_inventory = initial_inventory
        self.cost_structure = cost_structure
        self.unit_cost = cost_structure.get('unit_cost', 50.0)
        
        # Financial state
        self.current_price = initial_price
        self.cash_balance = cash_balance
        self.revenue = 0.0
        self.costs = 0.0
        
        # History tracking
        self.demand_history = deque(maxlen=50)
        self.competitor_prices = {}
        self.sales_count = 0
        
        self._state = {
            'current_price': self.current_price,
            'inventory_level': self.current_inventory / self.inventory_capacity,
            'revenue': self.revenue,
            'profit_margin': (self.current_price - self.unit_cost) / self.current_price
        }
    
    def _create_pricing_algorithm(self, algorithm_type: str) -> PricingAlgorithm:
        """Create pricing algorithm instance"""
        if algorithm_type == 'rule_based':
            return RuleBasedPricing()
        elif algorithm_type == 'demand_based':
            return DemandBasedPricing()
        elif algorithm_type == 'ml_based':
            return MLPricing()
        else:
            return RuleBasedPricing()  # Default
    
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]) -> None:
        """Monitor market activity"""
        period_demand = 0
        
        for event in events:
            # Track competitor prices
            if event.event_type == "price_updated" and event.source_id != self.agent_id:
                self.competitor_prices[event.payload['retailer_id']] = event.payload['new_price']
            
            # Track own sales
            elif event.event_type == "customer_purchase" and event.payload['retailer_id'] == self.agent_id:
                period_demand += 1
                self.sales_count += 1
                self.current_inventory -= 1
                self.revenue += event.payload['price']
                self.cash_balance += event.payload['price']
        
        # Record demand for this period
        self.demand_history.append(period_demand)
    
    async def decide(self) -> List[IAction]:
        """Make pricing and inventory decisions"""
        actions = []
        
        # Pricing decision
        if len(self.demand_history) >= 2:  # Need history for decision
            new_price = self.pricing_algorithm.calculate_price(
                current_price=self.current_price,
                demand_history=list(self.demand_history),
                competitor_prices=list(self.competitor_prices.values()),
                inventory_level=self.current_inventory / self.inventory_capacity,
                cost=self.unit_cost
            )
            
            # Only update if change is significant (>1%)
            if abs(new_price - self.current_price) / self.current_price > 0.01:
                actions.append(SetPriceAction(
                    product_id="product",
                    new_price=round(new_price, 2),
                    old_price=self.current_price
                ))
                self.current_price = round(new_price, 2)
        
        # Inventory decision
        inventory_ratio = self.current_inventory / self.inventory_capacity
        if inventory_ratio < 0.3 and self.cash_balance > self.unit_cost * 100:
            # Restock
            restock_quantity = int((self.inventory_capacity - self.current_inventory) * 0.7)
            if restock_quantity > 0:
                actions.append(RestockAction(
                    product_id="product",
                    quantity=restock_quantity,
                    unit_cost=self.unit_cost
                ))
                self.current_inventory += restock_quantity
                self.cash_balance -= restock_quantity * self.unit_cost
                self.costs += restock_quantity * self.unit_cost
        
        return actions
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        """Update state"""
        profit = self.revenue - self.costs
        
        self._state.update({
            'current_price': self.current_price,
            'inventory_level': self.current_inventory / self.inventory_capacity,
            'revenue': self.revenue,
            'profit': profit,
            'profit_margin': (self.current_price - self.unit_cost) / self.current_price if self.current_price > 0 else 0,
            'sales_count': self.sales_count,
            'cash_balance': self.cash_balance
        })
        
        return []


# ============================================================================
# Environment
# ============================================================================

class PricingMarketEnvironment(IEnvironment):
    """Market environment for pricing simulation"""
    
    def __init__(
        self,
        base_demand: float = 1000.0,
        demand_volatility: float = 0.1,
        price_transparency: float = 0.8
    ):
        super().__init__()
        self.base_demand = base_demand
        self.demand_volatility = demand_volatility
        self.price_transparency = price_transparency
        
        # Market state
        self.current_demand = base_demand
        self.total_transactions = 0
        self.average_price = 100.0
        self.price_variance = 0.0
        
        # Track retailers and prices
        self.retailer_prices = {}
        self.transaction_history = deque(maxlen=1000)
        
        self._global_state = {
            'current_demand': self.current_demand,
            'average_price': self.average_price,
            'price_variance': self.price_variance,
            'total_transactions': self.total_transactions
        }
    
    async def update(self, timestep: float) -> List[SimulationEvent]:
        """Update market conditions"""
        events = []
        
        # Demand fluctuation
        demand_change = random.gauss(0, self.demand_volatility)
        self.current_demand = max(1, self.current_demand * (1 + demand_change))
        
        # Calculate market statistics
        if self.retailer_prices:
            prices = list(self.retailer_prices.values())
            self.average_price = np.mean(prices)
            self.price_variance = np.var(prices)
        
        # Market events
        if self.price_variance > 100:  # High price dispersion
            events.append(SimulationEvent(
                timestamp=datetime.now(),
                source_id='market_environment',
                event_type='market_alert',
                payload={
                    'alert_type': 'high_price_variance',
                    'variance': self.price_variance,
                    'average_price': self.average_price
                }
            ))
        
        # Update global state
        self._global_state.update({
            'current_demand': self.current_demand,
            'average_price': self.average_price,
            'price_variance': self.price_variance,
            'total_transactions': self.total_transactions
        })
        
        return events
    
    def get_state(self, agent_id: str) -> Dict[str, Any]:
        """Get observable state for agent"""
        base_state = {
            'market_demand_index': self.current_demand / self.base_demand,
            'transaction_volume': len(self.transaction_history)
        }
        
        # Retailers see more information
        if 'retailer' in agent_id:
            visible_prices = {}
            
            # Price transparency determines how many competitor prices are visible
            for retailer_id, price in self.retailer_prices.items():
                if retailer_id != agent_id and random.random() < self.price_transparency:
                    visible_prices[retailer_id] = price
            
            base_state.update({
                'competitor_prices': visible_prices,
                'average_market_price': self.average_price,
                'price_variance': self.price_variance
            })
        
        return base_state
    
    async def apply_action(self, action: IAction, agent: IAgent) -> List[SimulationEvent]:
        """Apply actions to environment"""
        events = await action.execute(agent, self)
        
        # Update environment based on action
        if isinstance(action, SetPriceAction):
            self.retailer_prices[agent.agent_id] = action.new_price
        
        # Track transactions
        for event in events:
            if event.event_type == "customer_purchase":
                self.total_transactions += 1
                self.transaction_history.append({
                    'timestamp': event.timestamp,
                    'price': event.payload['price'],
                    'retailer': event.payload['retailer_id']
                })
        
        return events


# ============================================================================
# Plugin Implementation
# ============================================================================

class PricingStrategyPlugin(ISimulationPlugin):
    """Plugin for dynamic pricing strategy simulation"""
    
    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            'name': 'Dynamic Pricing Strategy Simulator',
            'version': '1.0.0',
            'description': 'Simulates competitive pricing dynamics in a multi-retailer market',
            'author': 'Simulation Framework',
            'parameters': {
                'num_customers': 'Number of customer agents',
                'num_retailers': 'Number of retailer agents',
                'pricing_algorithms': 'List of pricing algorithms for retailers',
                'elasticity_segments': 'Customer price elasticity segments'
            }
        }
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        agents = []
        
        # Customer segments
        elasticity_segments = config.get('elasticity_segments', [
            {'name': 'price_sensitive', 'elasticity': -2.0, 'size_pct': 0.4, 'frequency': 2.0},
            {'name': 'moderate', 'elasticity': -1.0, 'size_pct': 0.4, 'frequency': 1.5},
            {'name': 'premium', 'elasticity': -0.5, 'size_pct': 0.2, 'frequency': 1.0}
        ])
        
        # Create customers
        total_customers = config.get('num_customers', 100)
        initial_price = config.get('initial_price', 100.0)
        
        for segment in elasticity_segments:
            segment_size = int(total_customers * segment['size_pct'])
            
            for i in range(segment_size):
                agents.append(PriceSensitiveCustomerAgent(
                    agent_id=f"customer_{segment['name']}_{i}",
                    price_elasticity=segment['elasticity'],
                    reference_price=initial_price,
                    purchase_frequency=segment['frequency'],
                    budget=random.uniform(500, 2000)
                ))
        
        # Create retailers
        pricing_algorithms = config.get('pricing_algorithms', [
            'rule_based', 'demand_based', 'ml_based', 'rule_based', 'demand_based'
        ])
        
        num_retailers = min(len(pricing_algorithms), config.get('num_retailers', 5))
        
        for i in range(num_retailers):
            cost_structure = {
                'unit_cost': random.uniform(40, 60),
                'fixed_costs': random.uniform(1000, 5000),
                'storage_cost': random.uniform(0.1, 0.5)
            }
            
            agents.append(RetailerAgent(
                agent_id=f"retailer_{i}",
                pricing_algorithm=pricing_algorithms[i],
                inventory_capacity=random.randint(500, 1500),
                initial_inventory=random.randint(300, 800),
                cost_structure=cost_structure,
                initial_price=initial_price + random.uniform(-10, 10),
                cash_balance=random.uniform(50000, 200000)
            ))
        
        return agents
    
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        return PricingMarketEnvironment(
            base_demand=config.get('base_demand', 1000.0),
            demand_volatility=config.get('demand_volatility', 0.1),
            price_transparency=config.get('price_transparency', 0.8)
        )
    
    def get_metrics_definitions(self) -> Dict[str, Any]:
        return {
            'average_price': {
                'calculator': self._calculate_average_price,
                'aggregator': lambda x: x[-1] if x else 0,
                'window_size': 100
            },
            'price_dispersion': {
                'calculator': self._calculate_price_dispersion,
                'aggregator': lambda x: x[-1] if x else 0,
                'window_size': 100
            },
            'market_efficiency': {
                'calculator': self._calculate_market_efficiency,
                'aggregator': lambda x: sum(x) / len(x) if x else 0,
                'window_size': 50
            },
            'total_revenue': {
                'calculator': self._calculate_total_revenue,
                'aggregator': lambda x: x[-1] if x else 0,
                'window_size': 100
            },
            'inventory_turnover': {
                'calculator': self._calculate_inventory_turnover,
                'aggregator': lambda x: sum(x) / len(x) if x else 0,
                'window_size': 50
            }
        }
    
    async def _calculate_average_price(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate average market price"""
        retailers = [a for a in agents if isinstance(a, RetailerAgent)]
        if not retailers:
            return 0.0
        
        prices = [r.current_price for r in retailers]
        return np.mean(prices)
    
    async def _calculate_price_dispersion(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate price dispersion (coefficient of variation)"""
        retailers = [a for a in agents if isinstance(a, RetailerAgent)]
        if not retailers:
            return 0.0
        
        prices = [r.current_price for r in retailers]
        if len(prices) < 2:
            return 0.0
        
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        return (std_price / mean_price) if mean_price > 0 else 0
    
    async def _calculate_market_efficiency(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate market efficiency (how quickly prices converge)"""
        if hasattr(environment, 'price_variance'):
            # Lower variance indicates higher efficiency
            max_variance = 100.0
            efficiency = 1.0 - min(environment.price_variance / max_variance, 1.0)
            return efficiency
        return 0.5
    
    async def _calculate_total_revenue(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate total market revenue"""
        retailers = [a for a in agents if isinstance(a, RetailerAgent)]
        return sum(r.revenue for r in retailers)
    
    async def _calculate_inventory_turnover(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate average inventory turnover rate"""
        retailers = [a for a in agents if isinstance(a, RetailerAgent)]
        if not retailers:
            return 0.0
        
        turnover_rates = []
        for r in retailers:
            if r.sales_count > 0 and r.inventory_capacity > 0:
                # Simplified turnover calculation
                turnover = r.sales_count / r.inventory_capacity
                turnover_rates.append(turnover)
        
        return np.mean(turnover_rates) if turnover_rates else 0.0
    
    def get_visualization_config(self) -> Dict[str, Any]:
        return {
            'default_charts': [
                {
                    'type': 'line',
                    'metrics': ['average_price'],
                    'title': 'Market Price Evolution'
                },
                {
                    'type': 'line',
                    'metrics': ['price_dispersion', 'market_efficiency'],
                    'title': 'Market Dynamics'
                },
                {
                    'type': 'area',
                    'metrics': ['total_revenue'],
                    'title': 'Total Market Revenue'
                },
                {
                    'type': 'bar',
                    'metrics': ['inventory_turnover'],
                    'title': 'Inventory Efficiency'
                }
            ],
            'custom_visualizations': [
                {
                    'type': 'scatter',
                    'data': 'price_vs_demand',
                    'title': 'Price-Demand Relationship'
                },
                {
                    'type': 'heatmap',
                    'data': 'retailer_performance',
                    'title': 'Retailer Performance Matrix'
                }
            ]
        }