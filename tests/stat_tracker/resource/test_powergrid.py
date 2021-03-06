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


from unittest.mock import Mock

from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship, Implant
from tests.stat_tracker.stat_testcase import StatTestCase


class TestPowergrid(StatTestCase):
    """Check functionality of powergrid stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.st.powergrid.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.st.powergrid.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.st.powergrid.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_up(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder.attributes = {Attribute.power: 55.5555555555}
        self.track_holder(holder)
        self.assertEqual(self.st.powergrid.used, 55.56)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_rounding_down(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder.attributes = {Attribute.power: 44.4444444444}
        self.track_holder(holder)
        self.assertEqual(self.st.powergrid.used, 44.44)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder2.attributes = {Attribute.power: -30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 20)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.st.powergrid.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_state(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 50)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_domain(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.character, spec_set=Implant(1))
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.assertEqual(self.st.powergrid.output, 50)
        holder1.attributes[Attribute.power] = 10
        ship_holder.attributes[Attribute.power_output] = 60
        self.assertEqual(self.st.powergrid.used, 80)
        self.assertEqual(self.st.powergrid.output, 50)
        self.set_ship(None)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=Module(1))
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.assertEqual(self.st.powergrid.output, 50)
        holder1.attributes[Attribute.power] = 10
        ship_holder.attributes[Attribute.power_output] = 60
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.powergrid.used, 40)
        self.assertEqual(self.st.powergrid.output, 60)
        self.set_ship(None)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
