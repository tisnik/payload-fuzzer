#!/usr/bin/env python3

# Copyright © 2019, 2020, 2021 Pavel Tisnovsky

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

"""Generate modified/mutated JSON file from the provided source file."""

import json
import os
import sys
import copy
import itertools
import random

from random_payload_generator import RandomPayloadGenerator


output_num = 0


def load_json(filename):
    """Load and decode JSON file."""
    with open(filename) as fin:
        return json.load(fin)


def generate_output(payload):
    """Generate output JSON file with a proper indentation."""
    # we have to use global counter
    global output_num
    filename = "generated_{}.json".format(output_num)
    with open(filename, 'w') as f:
        json.dump(payload, f, indent=4)
        # prepare counter for the next file
        output_num += 1


def remove_items_one_iter(original_payload, items_count, remove_flags):
    """Remove items from the original payload, produce new one."""
    keys = list(original_payload.keys())
    # deep copy
    new_payload = copy.deepcopy(original_payload)
    # try to remove items_count items from the payload
    for i in range(items_count):
        remove_flag = remove_flags[i]
        if remove_flag:
            key = keys[i]
            del new_payload[key]

    # generate output with the updated payload
    generate_output(new_payload)


def fuzz_remove_items(original_payload):
    """Fuzzy remove items from the original payload."""
    items_count = len(original_payload)
    # lexicographics ordering
    remove_flags_list = list(itertools.product([True, False],
                             repeat=items_count))
    # the last item contains (False, False, False...) and we are not interested
    # in removing ZERO items
    remove_flags_list = remove_flags_list[:-1]

    # try to remove items from the payload
    for remove_flags in remove_flags_list:
        remove_items_one_iter(original_payload, items_count, remove_flags)


def add_items_one_iter(original_payload, how_many):
    """Add new items into the original payload, produce new one."""
    # deep copy
    new_payload = copy.deepcopy(original_payload)
    rpg = RandomPayloadGenerator()

    for i in range(how_many):
        new_key = rpg.generate_random_key_for_dict(new_payload)
        new_value = rpg.generate_random_payload()
        new_payload[new_key] = new_value

    # generate output with the updated payload
    generate_output(new_payload)


def fuzz_add_items(original_payload, min, max, mutations):
    """Fuzzy add items into the original payload."""
    for how_many in range(min, max):
        for i in range(1, mutations):
            add_items_one_iter(original_payload, how_many)


def change_items_one_iteration(original_payload, how_many):
    """Change items in the original payload, produce new one."""
    # deep copy
    new_payload = copy.deepcopy(original_payload)
    rpg = RandomPayloadGenerator()

    # try to change how_many items in the payload
    for i in range(how_many):
        selected_key = random.choice(list(original_payload.keys()))
        new_value = rpg.generate_random_payload()
        # update data in payload
        new_payload[selected_key] = new_value

    # generate output with the updated payload
    generate_output(new_payload)


def fuzz_change_items(original_payload, min, max):
    """Fuzzy change items in the original payload."""
    for how_many in range(1, len(original_payload)):
        for i in range(min, max):
            change_items_one_iteration(original_payload, how_many)


def main(filename):
    """Entry point to this script."""
    original_payload = load_json(filename)
    fuzz_remove_items(original_payload)
    fuzz_add_items(original_payload, 1, 4, 2)
    fuzz_change_items(original_payload, 1, 4)


if len(sys.argv) < 2:
    print("Usage: python json_fuzzer.py input_file.json")
    sys.exit(1)

# start the fuzzer
main(sys.argv[1])
