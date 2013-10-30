#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


class VolatileProperty:
    """
    Caches attribute on instance and adds note
    about it to special set, which should be added
    by VolatileMixin.
    """

    def __init__(self, func):
        self.method = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.method(instance)
            name = self.method.__name__
            setattr(instance, name, value)
            instance._volatile_attrs.add(name)
            return value


class VolatileMixin:
    """
    Should be added as base class for all
    classes using volatileproperty on them.
    """

    def __init__(self, **kwargs):
        self._volatile_attrs = set()
        super().__init__(**kwargs)

    def _clear_volatile_attrs(self):
        """
        Remove all the caches values which were
        stored since the last cleanup.
        """
        for attr_name in self._volatile_attrs:
            try:
                delattr(self, attr_name)
            except AttributeError:
                pass
        next_in_mro = super()
        try:
            method = next_in_mro._clear_volatile_attrs
        except AttributeError:
            pass
        else:
            method()
