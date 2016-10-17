# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================


from collections import namedtuple

from eos.const.eos import Domain, Restriction
from eos.const.eve import Type, Attribute
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


# Capital items are exactly 4000 or 8000 in size
# with the exception of a few officer modules
# (which this validation will not catch)
Minimum_Capital_Item_Volume_Size = 4000

CapitalItemErrorData = namedtuple('CapitalItemErrorData', ('holder_volume', 'minimum_capital_item_volume', 'ship_is_capital'))


class CapitalItemRegister(RestrictionRegister):
    """
    Implements restriction:
    To fit holders with volume bigger than
    Minimum_Capital_Item_Volume_Size,
    ship must have Capital Ships attribute.

    Details:
    Only holders belonging to ship are tracked.
    For validation, unmodified volume value is taken. If
    volume attribute is absent, holder is not validated.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for all tracked holders
        self.__capital_holders = set()

    def register_holder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._domain != Domain.ship:
            return
        # Ignore holders with no volume attribute and holders with
        # volume which satisfies us regardless of ship type
        try:
            holder_volume = holder.item.attributes[Attribute.volume]
        except KeyError:
            return
        if holder_volume < Minimum_Capital_Item_Volume_Size:
            return
        self.__capital_holders.add(holder)

    def unregister_holder(self, holder):
        self.__capital_holders.discard(holder)

    def validate(self):

        ship_holder = self._fit.ship
        try:
            ship_item = ship_holder.item
            try:
                if ship_item.attributes[Attribute.is_capital_size]:
                    # Skip validation if ship is flagged as a capital
                    # Capital modules are allowed
                    return
            except KeyError:
                # Attribute doesn't exist,
                # so not a capital
                pass
        except AttributeError:
            # Ship doesn't exist on the fit.
            pass

        # If we got here, then we're dealing with non-capital
        # ship, and all registered holders are tainted
        if self.__capital_holders:
            tainted_holders = {}
            for holder in self.__capital_holders:
                holder_volume = holder.item.attributes[Attribute.volume]
                tainted_holders[holder] = CapitalItemErrorData(
                    holder_volume=holder_volume,
                    minimum_capital_item_volume=Minimum_Capital_Item_Volume_Size,
                    ship_is_capital = "false"
                )
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.capital_item
