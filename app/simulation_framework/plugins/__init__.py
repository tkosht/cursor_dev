"""
Plugin modules for the simulation framework.

This package contains various simulation type plugins that can be used
with the core simulation framework.
"""

from .product_launch import ProductLaunchPlugin
from .pricing_strategy import PricingStrategyPlugin

__all__ = [
    "ProductLaunchPlugin",
    "PricingStrategyPlugin"
]

# Plugin registry for easy discovery
AVAILABLE_PLUGINS = {
    "product_launch": ProductLaunchPlugin,
    "pricing_strategy": PricingStrategyPlugin
}

def get_plugin(plugin_name: str):
    """Get a plugin class by name"""
    if plugin_name not in AVAILABLE_PLUGINS:
        raise ValueError(f"Unknown plugin: {plugin_name}. Available plugins: {list(AVAILABLE_PLUGINS.keys())}")
    return AVAILABLE_PLUGINS[plugin_name]