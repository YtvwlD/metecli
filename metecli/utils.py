# from .config import Config (moved to bottom)

from tabulate import tabulate
from typing import Tuple, Dict, List, Iterable, Optional, Union

import logging

log = logging.getLogger(__name__)

Thing = Dict[str, object]

def print_table(config: 'Config', data: Iterable[Tuple[object, ...]], headers: Tuple[str, ...] = tuple()) -> None:
    print(tabulate(
        data,
        headers=headers,
        tablefmt=config["display"]["table_format"],
    ))

def fuzzy_search(things: List[Thing], search_for: str) -> Optional[Thing]:
    possible_things = list()
    selected_thing = None
    if search_for.isdecimal():
        selected_thing = find_by_id(things, int(search_for))
    else:
        for thing in things:
            if search_for == thing["name"]:
                selected_thing = thing
                break
            elif search_for.casefold() in thing["name"].casefold():
                possible_things.append(thing)
    if not selected_thing and len(possible_things) == 1:
        log.info("No exact match, but %s is the only possibility.", possible_things[0]["name"])
        selected_thing = possible_things[0]
    if selected_thing:
        log.debug("Found %s.", selected_thing["name"])
        return selected_thing
    elif possible_things:
        print("No exact match was found.")
        print("Possibilities:", ["{} ({})".format(thing["name"], thing["id"]) for thing in possible_things])
        return None
    else:
        print("No match was found.")
        return None

def find_by_id(things: List[Thing], id: Union[int, str]) -> Optional[Thing]:
    log.debug("Searching for %s in %s...", id, things)
    for thing in things:
        if thing["id"] == id:
            log.debug("Found %s.", thing)
            return thing
    log.debug("No match.")
    return None

def test_terminal_utf8() -> None:
    """Produces a warning if the system isn't correctly configured to output UTF-8."""
    from sys import stdout
    if stdout.encoding.upper() != "UTF-8":
        log.warning("Your system doesn't seem support UTF-8. Please consider fixing this.")

def true_false_to_yes_no(value: bool) -> str:
    return "yes" if value else "no"

def yes_no_to_true_false(value: str) -> Optional[bool]:
    if value in ("yes", "y"):
        return True
    if value in ("no", "n"):
        return False
    return None

def yn(prompt: str) -> bool:
    while True:
        entered = yes_no_to_true_false(input("{} (y/n) ".format(prompt)))
        if entered is not None:
            return entered
        print("Please enter 'yes' or 'no'.")

def show_edit(dict: Thing, key: str, prompt: str, type: object) -> None:
    old_value = dict[key]
    if type == bool:
        old_value = true_false_to_yes_no(old_value)
    final_prompt = "{} [{}]: ".format(prompt, old_value)
    while True:
        given = input(final_prompt)
        if not given:
            given = old_value
            if old_value is None:
                new_value = old_value
                break
        if type == str:
            if given.strip():
                new_value = given
                break
            else:
                print("Please type something.")
                continue
        elif type == int:
            try:
                new_value = int(given)
                break
            except ValueError:
                print("Please enter a number.")
                continue
        elif type == float:
            try:
                new_value = float(given)
                break
            except ValueError:
                print("Please enter a number.")
        elif type == bool:
            new_value = yes_no_to_true_false(given)
            if new_value is not None:
                break
            else:
                print("Please enter yes or no.")
        elif type == "email":
            if "@" in given:
                new_value = given
                break
            elif not given: # empty address
                new_value = given
                break
            else:
                print("This is not a valid email adress.")
                continue
        else:
            raise Exception("Unknown type. (Please report this isssue!)")
    dict[key] = new_value

from .config import Config
