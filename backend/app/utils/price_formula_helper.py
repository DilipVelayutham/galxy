"""
GALXY E-Commerce Customization Platform
Price Formula Helper Utility

Provides formula-based pricing calculations for numerical/slider customization attributes.
"""

from typing import Tuple, Union, Any


def calculate_formula_price(
    value: Any,
    base_included_units: Any,
    rate_per_unit: Any
) -> Tuple[Union[int, float], Union[int, float]]:
    """
    Calculate the extra units and extra cost for numerical/slider attributes
    when the selected value exceeds the base included units threshold.

    Args:
        value (Any): Customer-selected numerical value (e.g., length, size).
        base_included_units (Any): Number of units included without extra charge.
        rate_per_unit (Any): Cost per additional unit above the base threshold.

    Returns:
        Tuple[Union[int, float], Union[int, float]]: A tuple of (extra_units, extra_cost).
        If value <= base_included_units or inputs are invalid, returns (0, 0).
    """
    if isinstance(value, bool) or isinstance(base_included_units, bool) or isinstance(rate_per_unit, bool):
        return 0, 0

    try:
        val_num = float(value)
        base_num = float(base_included_units)
        rate_num = float(rate_per_unit)
    except (ValueError, TypeError):
        return 0, 0

    if val_num > base_num:
        extra_units = val_num - base_num
        extra_cost = extra_units * rate_num

        # Preserve integer representation if values have no fractional part
        if extra_units.is_integer():
            extra_units = int(extra_units)
        if extra_cost.is_integer():
            extra_cost = int(extra_cost)

        return extra_units, extra_cost

    return 0, 0
