"""
Product Launch Simulation Plugin

This plugin simulates the market dynamics of launching a new product,
including consumer adoption, competitor responses, and market evolution.
"""

import random
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ..core import (
    IAgent, IAction, IEnvironment, ISimulationPlugin,
    SimulationEvent
)


# ============================================================================
# Actions
# ============================================================================

@dataclass
class PurchaseAction(IAction):
    """Consumer purchase action"""
    product_id: str
    quantity: int
    price: float
    
    def __init__(self, product_id: str, quantity: int, price: float):
        super().__init__("purchase")
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def validate(self, agent: IAgent, environment: IEnvironment) -> bool:
        """Check if purchase is valid"""
        if isinstance(agent, ConsumerAgent):
            return agent.budget >= (self.price * self.quantity)
        return False
    
    async def execute(self, agent: IAgent, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute purchase"""
        return [SimulationEvent(
            timestamp=datetime.now(),
            source_id=agent.agent_id,
            event_type="product_purchased",
            payload={
                "product_id": self.product_id,
                "quantity": self.quantity,
                "price": self.price,
                "total_value": self.price * self.quantity,
                "consumer_segment": getattr(agent, 'segment', 'unknown')
            }
        )]


@dataclass
class MarketingCampaignAction(IAction):
    """Marketing campaign action"""
    campaign_type: str
    budget: float
    target_segment: Optional[str]
    
    def __init__(self, campaign_type: str, budget: float, target_segment: Optional[str] = None):
        super().__init__("marketing_campaign")
        self.campaign_type = campaign_type
        self.budget = budget
        self.target_segment = target_segment
    
    def validate(self, agent: IAgent, environment: IEnvironment) -> bool:
        """Check if campaign is valid"""
        if hasattr(agent, 'marketing_budget'):
            return agent.marketing_budget >= self.budget
        return False
    
    async def execute(self, agent: IAgent, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute marketing campaign"""
        # Calculate reach based on budget and campaign type
        reach_multiplier = {
            'social_media': 1.5,
            'traditional': 1.0,
            'influencer': 2.0,
            'targeted': 1.8
        }.get(self.campaign_type, 1.0)
        
        estimated_reach = int(self.budget * reach_multiplier / 10)  # Simple model
        
        return [SimulationEvent(
            timestamp=datetime.now(),
            source_id=agent.agent_id,
            event_type="marketing_campaign_launched",
            payload={
                "campaign_type": self.campaign_type,
                "budget": self.budget,
                "target_segment": self.target_segment,
                "estimated_reach": estimated_reach
            }
        )]


@dataclass
class PriceChangeAction(IAction):
    """Price change action"""
    product_id: str
    new_price: float
    old_price: float
    
    def __init__(self, product_id: str, new_price: float, old_price: float):
        super().__init__("price_change")
        self.product_id = product_id
        self.new_price = new_price
        self.old_price = old_price
    
    def validate(self, agent: IAgent, environment: IEnvironment) -> bool:
        """Price changes are always valid"""
        return True
    
    async def execute(self, agent: IAgent, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute price change"""
        price_change_pct = ((self.new_price - self.old_price) / self.old_price) * 100
        
        return [SimulationEvent(
            timestamp=datetime.now(),
            source_id=agent.agent_id,
            event_type="price_changed",
            payload={
                "product_id": self.product_id,
                "old_price": self.old_price,
                "new_price": self.new_price,
                "change_percentage": price_change_pct
            }
        )]


# ============================================================================
# Agents
# ============================================================================

class ConsumerAgent(IAgent):
    """Consumer agent with adoption behavior"""
    
    def __init__(
        self,
        agent_id: str,
        segment: str,
        adoption_threshold: float,
        budget: float,
        social_influence: float = 0.5,
        price_sensitivity: float = 1.0
    ):
        super().__init__(agent_id)
        self.segment = segment
        self.adoption_threshold = adoption_threshold
        self.budget = budget
        self.initial_budget = budget
        self.social_influence = social_influence
        self.price_sensitivity = price_sensitivity
        
        # State
        self.awareness = 0.0
        self.interest = 0.0
        self.has_purchased = False
        self.purchases = []
        self.influenced_by = []
        self.satisfaction = 0.0
        
        self._state = {
            'segment': segment,
            'awareness': self.awareness,
            'has_purchased': self.has_purchased,
            'budget_remaining': self.budget
        }
    
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]) -> None:
        """Process marketing and social influence"""
        for event in events:
            if event.event_type == "marketing_campaign_launched":
                # Check if targeted
                if event.payload.get('target_segment') in [None, self.segment]:
                    # Increase awareness based on campaign
                    awareness_boost = min(0.2, event.payload['budget'] / 50000)
                    self.awareness = min(1.0, self.awareness + awareness_boost)
            
            elif event.event_type == "product_purchased":
                # Social influence from other purchases
                if event.source_id != self.agent_id:
                    influence = self.social_influence * 0.1
                    self.interest = min(1.0, self.interest + influence)
                    self.influenced_by.append(event.source_id)
            
            elif event.event_type == "price_changed":
                # React to price changes
                if event.payload['change_percentage'] < 0:  # Price decrease
                    self.interest += 0.1 * self.price_sensitivity
                else:  # Price increase
                    self.interest -= 0.05 * self.price_sensitivity
                self.interest = max(0, min(1.0, self.interest))
    
    async def decide(self) -> List[IAction]:
        """Decide whether to purchase"""
        actions = []
        
        # Calculate purchase probability
        purchase_score = (self.awareness * 0.3 + self.interest * 0.7)
        
        # Add randomness for realistic behavior
        if random.random() < 0.1:  # 10% random factor
            purchase_score += random.uniform(-0.2, 0.2)
        
        # Check if should purchase
        if purchase_score >= self.adoption_threshold and not self.has_purchased:
            # Get current price from environment
            env_state = self._state  # In real implementation, get from environment
            current_price = 100.0  # Default price, should come from environment
            
            if self.budget >= current_price:
                actions.append(PurchaseAction(
                    product_id="new_product",
                    quantity=1,
                    price=current_price
                ))
        
        return actions
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute purchase actions"""
        events = []
        
        for action in self._action_queue:
            if isinstance(action, PurchaseAction):
                # Update budget
                self.budget -= action.price * action.quantity
                self.has_purchased = True
                self.purchases.append({
                    'timestamp': datetime.now(),
                    'price': action.price,
                    'quantity': action.quantity
                })
                
                # Generate satisfaction
                self.satisfaction = random.uniform(0.6, 1.0)  # Simple model
        
        # Update observable state
        self._state.update({
            'awareness': self.awareness,
            'interest': self.interest,
            'has_purchased': self.has_purchased,
            'budget_remaining': self.budget,
            'satisfaction': self.satisfaction
        })
        
        self._action_queue.clear()
        return events


class CompetitorAgent(IAgent):
    """Competitor company agent"""
    
    def __init__(
        self,
        agent_id: str,
        market_share: float,
        response_strategy: str = 'moderate',
        resources: float = 1000000
    ):
        super().__init__(agent_id)
        self.market_share = market_share
        self.response_strategy = response_strategy
        self.resources = resources
        
        # State
        self.threat_level = 0.0
        self.current_price = 100.0
        self.campaigns_launched = 0
        
        self._state = {
            'market_share': market_share,
            'current_price': self.current_price,
            'threat_level': self.threat_level
        }
    
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]) -> None:
        """Monitor market activity"""
        for event in events:
            if event.event_type == "product_purchased" and event.payload.get('product_id') == 'new_product':
                # Increase threat perception
                self.threat_level = min(1.0, self.threat_level + 0.01)
            
            elif event.event_type == "marketing_campaign_launched" and event.source_id != self.agent_id:
                # React to competitor marketing
                self.threat_level = min(1.0, self.threat_level + 0.05)
    
    async def decide(self) -> List[IAction]:
        """Decide competitive response"""
        actions = []
        
        # Response based on strategy and threat level
        if self.response_strategy == 'aggressive' and self.threat_level > 0.3:
            # Price reduction
            if random.random() < 0.3:
                new_price = self.current_price * 0.95
                actions.append(PriceChangeAction(
                    product_id=f"{self.agent_id}_product",
                    new_price=new_price,
                    old_price=self.current_price
                ))
                self.current_price = new_price
            
            # Marketing campaign
            if random.random() < 0.4 and self.resources > 50000:
                campaign_budget = min(100000, self.resources * 0.1)
                actions.append(MarketingCampaignAction(
                    campaign_type='targeted',
                    budget=campaign_budget,
                    target_segment='price_sensitive'
                ))
                self.resources -= campaign_budget
        
        elif self.response_strategy == 'moderate' and self.threat_level > 0.5:
            # Moderate response
            if random.random() < 0.2:
                campaign_budget = min(50000, self.resources * 0.05)
                actions.append(MarketingCampaignAction(
                    campaign_type='traditional',
                    budget=campaign_budget
                ))
                self.resources -= campaign_budget
        
        return actions
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        """Execute competitive actions"""
        self._state.update({
            'market_share': self.market_share,
            'current_price': self.current_price,
            'threat_level': self.threat_level,
            'resources': self.resources
        })
        return []


class LaunchingCompanyAgent(IAgent):
    """The company launching the new product"""
    
    def __init__(
        self,
        agent_id: str,
        marketing_budget: float,
        pricing_strategy: str = 'penetration',
        initial_price: float = 100.0
    ):
        super().__init__(agent_id)
        self.marketing_budget = marketing_budget
        self.initial_marketing_budget = marketing_budget
        self.pricing_strategy = pricing_strategy
        self.current_price = initial_price
        
        # State tracking
        self.units_sold = 0
        self.revenue = 0.0
        self.campaign_count = 0
        self.market_phase = 'launch'  # launch, growth, maturity
        
        self._state = {
            'units_sold': self.units_sold,
            'revenue': self.revenue,
            'current_price': self.current_price,
            'market_phase': self.market_phase
        }
    
    async def perceive(self, environment: IEnvironment, events: List[SimulationEvent]) -> None:
        """Track sales and market response"""
        for event in events:
            if event.event_type == "product_purchased" and event.payload.get('product_id') == 'new_product':
                self.units_sold += event.payload['quantity']
                self.revenue += event.payload['total_value']
        
        # Update market phase based on sales
        if self.units_sold < 100:
            self.market_phase = 'launch'
        elif self.units_sold < 1000:
            self.market_phase = 'growth'
        else:
            self.market_phase = 'maturity'
    
    async def decide(self) -> List[IAction]:
        """Decide marketing and pricing strategy"""
        actions = []
        
        # Marketing decisions based on phase
        if self.market_phase == 'launch' and self.marketing_budget > 100000:
            # Heavy marketing during launch
            campaign_budget = min(200000, self.marketing_budget * 0.3)
            actions.append(MarketingCampaignAction(
                campaign_type='influencer',
                budget=campaign_budget,
                target_segment='early_adopters'
            ))
            self.marketing_budget -= campaign_budget
            self.campaign_count += 1
        
        elif self.market_phase == 'growth' and self.marketing_budget > 50000:
            # Targeted marketing during growth
            if self.campaign_count % 3 == 0:  # Every third decision cycle
                campaign_budget = min(100000, self.marketing_budget * 0.2)
                actions.append(MarketingCampaignAction(
                    campaign_type='social_media',
                    budget=campaign_budget,
                    target_segment='mass_market'
                ))
                self.marketing_budget -= campaign_budget
                self.campaign_count += 1
        
        # Pricing decisions
        if self.pricing_strategy == 'penetration' and self.market_phase == 'growth':
            # Gradually increase price
            if random.random() < 0.1:  # 10% chance per cycle
                new_price = self.current_price * 1.05
                actions.append(PriceChangeAction(
                    product_id='new_product',
                    new_price=new_price,
                    old_price=self.current_price
                ))
                self.current_price = new_price
        
        return actions
    
    async def act(self, environment: IEnvironment) -> List[SimulationEvent]:
        """Update state"""
        self._state.update({
            'units_sold': self.units_sold,
            'revenue': self.revenue,
            'current_price': self.current_price,
            'market_phase': self.market_phase,
            'marketing_budget': self.marketing_budget
        })
        return []


# ============================================================================
# Environment
# ============================================================================

class MarketEnvironment(IEnvironment):
    """Market environment for product launch simulation"""
    
    def __init__(
        self,
        market_size: int = 1000000,
        growth_rate: float = 0.05,
        seasonality: Optional[Dict[int, float]] = None
    ):
        super().__init__()
        self.market_size = market_size
        self.growth_rate = growth_rate
        self.seasonality = seasonality or {}
        
        # Market state
        self.current_market_size = market_size
        self.total_sales = 0
        self.market_saturation = 0.0
        self.competitor_activity = 0.0
        
        # Product tracking
        self.products = {}
        self.product_prices = {'new_product': 100.0}
        
        self._global_state = {
            'market_size': self.current_market_size,
            'total_sales': self.total_sales,
            'market_saturation': self.market_saturation,
            'average_price': 100.0
        }
    
    async def update(self, timestep: float) -> List[SimulationEvent]:
        """Update market conditions"""
        events = []
        
        # Market growth
        self.current_market_size = int(self.current_market_size * (1 + self.growth_rate * timestep))
        
        # Calculate market saturation
        if self.current_market_size > 0:
            self.market_saturation = self.total_sales / self.current_market_size
        
        # Market events
        if self.market_saturation > 0.5 and random.random() < 0.1:
            events.append(SimulationEvent(
                timestamp=datetime.now(),
                source_id='market_environment',
                event_type='market_milestone',
                payload={
                    'milestone': 'majority_adoption',
                    'saturation': self.market_saturation
                }
            ))
        
        # Update global state
        self._global_state.update({
            'market_size': self.current_market_size,
            'total_sales': self.total_sales,
            'market_saturation': self.market_saturation
        })
        
        return events
    
    def get_state(self, agent_id: str) -> Dict[str, Any]:
        """Get observable market state for an agent"""
        base_state = {
            'market_saturation': self.market_saturation,
            'competitor_activity': self.competitor_activity,
            'product_prices': self.product_prices.copy()
        }
        
        # Add agent-specific information
        if 'consumer' in agent_id:
            # Consumers see less detailed information
            base_state['market_buzz'] = min(1.0, self.total_sales / 1000)
        else:
            # Companies see more detailed information
            base_state.update({
                'total_sales': self.total_sales,
                'market_size': self.current_market_size
            })
        
        return base_state
    
    async def apply_action(self, action: IAction, agent: IAgent) -> List[SimulationEvent]:
        """Apply agent actions to environment"""
        events = await action.execute(agent, self)
        
        # Update environment based on action
        if isinstance(action, PurchaseAction):
            self.total_sales += action.quantity
            
        elif isinstance(action, PriceChangeAction):
            if action.product_id in self.product_prices:
                self.product_prices[action.product_id] = action.new_price
            
        elif isinstance(action, MarketingCampaignAction):
            self.competitor_activity = min(1.0, self.competitor_activity + 0.1)
        
        return events


# ============================================================================
# Plugin Implementation
# ============================================================================

class ProductLaunchPlugin(ISimulationPlugin):
    """Plugin for product launch market simulation"""
    
    def get_plugin_info(self) -> Dict[str, Any]:
        return {
            'name': 'Product Launch Simulator',
            'version': '1.0.0',
            'description': 'Simulates market dynamics of launching a new product',
            'author': 'Simulation Framework',
            'parameters': {
                'num_consumers': 'Number of consumer agents',
                'num_competitors': 'Number of competitor companies',
                'market_size': 'Total addressable market size',
                'consumer_segments': 'Configuration for consumer segments'
            }
        }
    
    def create_agents(self, config: Dict[str, Any]) -> List[IAgent]:
        agents = []
        
        # Consumer segments configuration
        segments = config.get('consumer_segments', [
            {
                'name': 'early_adopters',
                'size_pct': 0.1,
                'adoption_threshold': 0.3,
                'budget_range': (500, 2000),
                'social_influence': 0.8,
                'price_sensitivity': 0.5
            },
            {
                'name': 'mass_market',
                'size_pct': 0.6,
                'adoption_threshold': 0.6,
                'budget_range': (200, 1000),
                'social_influence': 0.6,
                'price_sensitivity': 1.2
            },
            {
                'name': 'laggards',
                'size_pct': 0.3,
                'adoption_threshold': 0.8,
                'budget_range': (100, 500),
                'social_influence': 0.4,
                'price_sensitivity': 1.5
            }
        ])
        
        # Create consumers
        total_consumers = config.get('num_consumers', 1000)
        
        for segment in segments:
            segment_size = int(total_consumers * segment['size_pct'])
            
            for i in range(segment_size):
                budget = random.uniform(*segment['budget_range'])
                
                agents.append(ConsumerAgent(
                    agent_id=f"consumer_{segment['name']}_{i}",
                    segment=segment['name'],
                    adoption_threshold=segment['adoption_threshold'],
                    budget=budget,
                    social_influence=segment['social_influence'],
                    price_sensitivity=segment['price_sensitivity']
                ))
        
        # Create competitors
        competitor_configs = config.get('competitors', [
            {'name': 'BigCorp', 'market_share': 0.3, 'strategy': 'aggressive', 'resources': 5000000},
            {'name': 'MediumCo', 'market_share': 0.2, 'strategy': 'moderate', 'resources': 2000000},
            {'name': 'SmallBiz', 'market_share': 0.1, 'strategy': 'passive', 'resources': 500000}
        ])
        
        for i, comp_config in enumerate(competitor_configs):
            agents.append(CompetitorAgent(
                agent_id=f"competitor_{comp_config['name']}",
                market_share=comp_config['market_share'],
                response_strategy=comp_config['strategy'],
                resources=comp_config['resources']
            ))
        
        # Create launching company
        agents.append(LaunchingCompanyAgent(
            agent_id='launching_company',
            marketing_budget=config.get('marketing_budget', 1000000),
            pricing_strategy=config.get('pricing_strategy', 'penetration'),
            initial_price=config.get('initial_price', 100.0)
        ))
        
        return agents
    
    def create_environment(self, config: Dict[str, Any]) -> IEnvironment:
        return MarketEnvironment(
            market_size=config.get('market_size', 1000000),
            growth_rate=config.get('market_growth_rate', 0.05),
            seasonality=config.get('seasonality_factors', {})
        )
    
    def get_metrics_definitions(self) -> Dict[str, Any]:
        return {
            'adoption_rate': {
                'calculator': self._calculate_adoption_rate,
                'aggregator': lambda x: x[-1] if x else 0,  # Latest value
                'window_size': 100
            },
            'market_penetration': {
                'calculator': self._calculate_market_penetration,
                'aggregator': lambda x: x[-1] if x else 0,
                'window_size': 100
            },
            'revenue': {
                'calculator': self._calculate_revenue,
                'aggregator': lambda x: x[-1] if x else 0,
                'window_size': 50
            },
            'competitor_response_index': {
                'calculator': self._calculate_competitor_response,
                'aggregator': lambda x: sum(x) / len(x) if x else 0,  # Average
                'window_size': 50
            },
            'customer_satisfaction': {
                'calculator': self._calculate_satisfaction,
                'aggregator': lambda x: sum(x) / len(x) if x else 0,
                'window_size': 100
            }
        }
    
    async def _calculate_adoption_rate(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate product adoption rate"""
        consumers = [a for a in agents if isinstance(a, ConsumerAgent)]
        if not consumers:
            return 0.0
        
        adopted = sum(1 for c in consumers if c.has_purchased)
        return adopted / len(consumers)
    
    async def _calculate_market_penetration(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate market penetration"""
        if hasattr(environment, 'market_saturation'):
            return environment.market_saturation
        return 0.0
    
    async def _calculate_revenue(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate total revenue"""
        for agent in agents:
            if isinstance(agent, LaunchingCompanyAgent):
                return agent.revenue
        return 0.0
    
    async def _calculate_competitor_response(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate competitor response intensity"""
        competitors = [a for a in agents if isinstance(a, CompetitorAgent)]
        if not competitors:
            return 0.0
        
        avg_threat = sum(c.threat_level for c in competitors) / len(competitors)
        return avg_threat
    
    async def _calculate_satisfaction(self, agents: List[IAgent], environment: IEnvironment, events: List[SimulationEvent]) -> float:
        """Calculate average customer satisfaction"""
        consumers = [a for a in agents if isinstance(a, ConsumerAgent) and a.has_purchased]
        if not consumers:
            return 0.0
        
        avg_satisfaction = sum(c.satisfaction for c in consumers) / len(consumers)
        return avg_satisfaction
    
    def get_visualization_config(self) -> Dict[str, Any]:
        return {
            'default_charts': [
                {
                    'type': 'line',
                    'metrics': ['adoption_rate', 'market_penetration'],
                    'title': 'Market Adoption Over Time'
                },
                {
                    'type': 'line',
                    'metrics': ['revenue'],
                    'title': 'Revenue Growth'
                },
                {
                    'type': 'gauge',
                    'metrics': ['customer_satisfaction'],
                    'title': 'Customer Satisfaction'
                },
                {
                    'type': 'bar',
                    'metrics': ['competitor_response_index'],
                    'title': 'Competitor Activity'
                }
            ],
            'custom_visualizations': [
                {
                    'type': 'heatmap',
                    'data': 'consumer_segments',
                    'title': 'Adoption by Segment'
                },
                {
                    'type': 'network',
                    'data': 'social_influence',
                    'title': 'Social Influence Network'
                }
            ]
        }