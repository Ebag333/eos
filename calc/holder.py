#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from abc import ABCMeta
from abc import abstractmethod

from .affector import Affector
from .info.info import InfoState
from .map import MutableAttributeMap


class MutableAttributeHolder(metaclass=ABCMeta):
    """
    Base attribute holder class inherited by all classes that
    need to keep track of modified attributes.

    Positional arguments:
    type_ -- type (item), on which this holder is based
    """

    def __init__(self, type_):
        # Which fit this holder is bound to
        self.fit = None
        # Which type this holder wraps
        self.item = type_
        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)
        # Keeps current state of the holder
        self.__state = InfoState.offline

    @property
    def state(self):
        """Get state of holder"""
        return self.__state

    @state.setter
    def state(self, newState):
        """Set state of holder"""
        # First, check if holder's item can have this
        # state at all
        if newState > self.item.getMaxState():
            raise RuntimeError("invalid state")
        oldState = self.state
        if newState == oldState:
            return
        # When holder is assigned to some fit, ask fit
        # to perform fit-specific state switch of our
        # holder
        if self.fit is not None:
            self.fit._stateSwitch(self, newState)
        self.__state = newState

    @abstractmethod
    def _getLocation(self):
        """
        Service method which each class must implement, used in
        calculation process
        """
        ...

    def _generateAffectors(self, stateFilter=None, contextFilter=None):
        """
        Get all affectors spawned by holder.

        Keyword arguments:
        stateFilter -- filter results by affector's required state,
        which should be in this iterable; if None, no filtering
        occurs (default None)
        contextFilter -- filter results by affector's required state,
        which should be in this iterable; if None, no filtering
        occurs (default None)

        Return value:
        Set with Affector objects, satisfying passed filters
        """
        affectors = set()
        for info in self.item.getInfos():
            if stateFilter is not None and not info.state in stateFilter:
                continue
            if contextFilter is not None and not info.context in contextFilter:
                continue
            affector = Affector(self, info)
            affectors.add(affector)
        return affectors