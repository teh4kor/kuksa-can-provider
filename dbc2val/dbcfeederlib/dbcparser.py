#!/usr/bin/python3

########################################################################
# Copyright (c) 2023 Robert Bosch GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
########################################################################

import logging
from typing import Set, Optional, Dict
import cantools

log = logging.getLogger(__name__)


class DBCParser:
    def __init__(self, dbcfile: str, use_strict_parsing: bool = True):

        # Read DBC file
        log.info("Reading DBC file {}".format(dbcfile))
        self.db = cantools.database.load_file(dbcfile, strict=use_strict_parsing)

        # Init some dictionaries to speed up search
        self.signal_to_canid: Dict[str, Optional[int]] = {}
        self.canid_to_signals: Dict[int, Set[str]] = {}

    def get_canid_for_signal(self, sig_to_find: str) -> Optional[int]:
        if sig_to_find in self.signal_to_canid:
            return self.signal_to_canid[sig_to_find]

        for msg in self.db.messages:
            for signal in msg.signals:
                if signal.name == sig_to_find:
                    frame_id = msg.frame_id
                    log.info(
                        "Found signal in DBC file {} in CAN frame id 0x{:02x}".format(
                            signal.name, frame_id
                        )
                    )
                    self.signal_to_canid[sig_to_find] = frame_id
                    return frame_id
        log.warning("Signal {} not found in DBC file".format(sig_to_find))
        self.signal_to_canid[sig_to_find] = None
        return None

    def get_signals_for_canid(self, canid: int) -> Set[str]:

        if canid in self.canid_to_signals:
            return self.canid_to_signals[canid]

        for msg in self.db.messages:
            if canid == msg.frame_id:
                names = set()
                for signal in msg.signals:
                    names.add(signal.name)
                self.canid_to_signals[canid] = names
                return names
        log.warning(f"CAN id {canid} not found in DBC file")
        self.canid_to_signals[canid] = []
        return []
