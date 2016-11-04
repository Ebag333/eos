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

from eos.const.eos import Restriction
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister
from eos.const.eve import Effect

ModuleSlotErrorData = namedtuple('ModuleSlotErrorData', ('module_slot', 'matching_slot'))


class ModuleSlotRegister(RestrictionRegister):
    """
    Class which implements common functionality for all
    registers, which track amount of occupied ship slots
    against number of available ship slots.
    """

    def __init__(self, fit, stat_name, restriction_type):
        self.__restrictionType = restriction_type
        self._fit = fit
        # Use this stat name to get numbers from stats tracker
        self.__stat_name = stat_name
        self._slot_consumers = set()

    def register_holder(self, holder):
        self._slot_consumers.add(holder)

    def unregister_holder(self, holder):
        self._slot_consumers.discard(holder)

    def validate(self):
        stat_name = self.__stat_name
        tainted_holders = {}
        # Loop through the module registered to the slot
        for idx, module in enumerate(self._slot_consumers):
            hipower = medpower = lowpower = False

            # Loop through the effects on each module
            for module_effect in module.item.effects:
                if module_effect.id == Effect.low_power and stat_name == 'high_slots':  # hiPower Effect
                    hipower = True
                    break
                elif module_effect.id == Effect.med_power and stat_name == 'med_slots':  # medPower Effect
                    medpower = True
                    break
                elif module_effect.id == Effect.lo_power and stat_name == 'low_slots':  # lowPower Effect
                    lowpower = True
                    break

            # Continue to the next module if we could not find a
            # matching slot and restriction type
            if hipower or medpower or lowpower:
                continue
            else:
                tainted_holders[module] = ModuleSlotErrorData(
                    module_slot=stat_name,
                    matching_slot=False
                )

        # If number of holders which take this slot is bigger
        # than number of available slots, then at least some
        # holders in container are tainted
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return self.__restrictionType


class ModuleHighSlotRegister(ModuleSlotRegister):
    """
    Implements restriction:
    Number of high-slot holders should not exceed number of
    high slots ship provides.

    Details:
    Only holders placed to fit.modules.high are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ModuleSlotRegister.__init__(self, fit, 'high_slots', id(Restriction.high_slot))

    def register_holder(self, holder):
        if holder in self._fit.modules.high:
            ModuleSlotRegister.register_holder(self, holder)

    def _get_tainted_holders(self, module_index):
        return self._fit.modules.high[module_index:]


class ModuleMediumSlotRegister(ModuleSlotRegister):
    """
    Implements restriction:
    Number of medium-slot holders should not exceed number of
    medium slots ship provides.

    Details:
    Only holders placed to fit.modules.med are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ModuleSlotRegister.__init__(self, fit, 'med_slots', Restriction.medium_slot)

    def register_holder(self, holder):
        if holder in self._fit.modules.med:
            ModuleSlotRegister.register_holder(self, holder)

    def _get_tainted_holders(self, module_index):
        return self._fit.modules.med[module_index:]


class ModuleLowSlotRegister(ModuleSlotRegister):
    """
    Implements restriction:
    Number of low-slot holders should not exceed number of
    low slots ship provides.

    Details:
    Only holders placed to fit.modules.low are tracked.
    For validation, stats module data is used.
    """

    def __init__(self, fit):
        ModuleSlotRegister.__init__(self, fit, 'low_slots', Restriction.low_slot)

    def register_holder(self, holder):
        if holder in self._fit.modules.low:
            ModuleSlotRegister.register_holder(self, holder)

    def _get_tainted_holders(self, module_index):
        return self._fit.modules.low[module_index:]
