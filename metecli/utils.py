# from .config import Config (moved to bottom)
from .connection.models import Audit, Barcode, Drink, User
from .connection.connection import Connection
from .connection.config import Config as ConnectionConfig

from functools import partial
from interrogatio import interrogatio
from interrogatio.core.exceptions import ValidationError
from interrogatio.validators import (
    EmailValidator, IntegerValidator, NumberValidator, RequiredValidator,
)
from interrogatio.validators.base import Validator
from tabulate import tabulate
from typing import (
    Any, Tuple, Dict, List, Iterable, NamedTuple, Optional, Type, TypeVar, Union
)

import logging

log = logging.getLogger(__name__)

Thing = TypeVar("Thing", Audit, Barcode, Drink, User)
EMail = type("EMail", (object,), {})


def connect(config: 'Config') -> Connection:
    connection_config = ConnectionConfig(config["connection"], config.save)
    return Connection.new(connection_config)


def print_table(
    config: 'Config', data: Iterable[Tuple[Any, ...]],
    headers: Tuple[str, ...] = tuple(),
) -> None:
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
            if search_for == thing.name:
                selected_thing = thing
                break
            elif search_for.casefold() in thing.name.casefold():
                possible_things.append(thing)
    if not selected_thing and len(possible_things) == 1:
        log.info(
            "No exact match, but %s is the only possibility.",
            possible_things[0].name
        )
        selected_thing = possible_things[0]
    if selected_thing:
        log.debug("Found %s.", selected_thing.name)
        return selected_thing
    elif possible_things:
        print("No exact match was found.")
        print("Possibilities:", [
            "{} ({})".format(thing.name, thing.id)
            for thing in possible_things
        ])
        return None
    else:
        print("No match was found.")
        return None


def find_by_id(things: List[Thing], id: Union[int, str]) -> Optional[Thing]:
    log.debug("Searching for %s in %s...", id, things)
    for thing in things:
        if thing.id == id:
            log.debug("Found %s.", thing)
            return thing
    log.debug("No match.")
    return None


def test_terminal_utf8() -> None:
    """Produces a warning if the system isn't correctly configured to output UTF-8."""
    from sys import stdout
    if stdout.encoding.upper() != "UTF-8":
        log.warn("Your system doesn't seem support UTF-8. Please consider fixing this.")


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


class BooleanValidator(Validator):
    def __init__(self):
        super(BooleanValidator, self).__init__(
            message="this field does not match yes or no"
        )
    
    def validate(self, value, context=None):
        if yes_no_to_true_false(value) is None:
            raise ValidationError(self.message)


class Question(NamedTuple):
    attribute: str
    message: str
    description: Optional[str] = None
    type: Type = str
    required: bool = False

    def to_interrogatio(self, data: Thing) -> Dict[str, Any]:
        d = {
            "name": self.attribute,
            "message": self.message,
            "description": self.description,
            "type": "input",
            "validators": [],
        }
        old_value = getattr(data, self.attribute)
        if self.required:
            d["validators"].append(RequiredValidator())
        if self.type == str:
            d["default"] = old_value
        elif self.type == int:
            d["validators"].append(IntegerValidator())
            d["default"] = str(old_value)
        elif self.type == float:
            d["validators"].append(NumberValidator())
            d["default"] = str(old_value)
        elif self.type == bool:
            d["default"] = true_false_to_yes_no(old_value)
            d["validators"].append(BooleanValidator())
        elif self.type == EMail:
            d["default"] = old_value
            d["validators"].append(EmailValidator())
        else:
            raise Exception(
                "Unknown type {}. (Please report this isssue!)".format(
                    self.type
                )
            )
        return d


def show_edit(thing: Thing, questions: List[Question]) -> None:
    interrogatio_questions = [q.to_interrogatio(thing) for q in questions]
    interrogatio_answers = interrogatio(interrogatio_questions)
    for key, value in interrogatio_answers.items():
        question = list(filter(lambda q: q.attribute == key, questions))[0]
        if question.type == str:
            new_value = value
        elif question.type == int:
            new_value = int(value)
        elif question.type == float:
            new_value = float(value)
        elif question.type == bool:
            new_value = yes_no_to_true_false(value)
        elif question.type == EMail:
            new_value = value
        else:
            raise Exception("Unknown type. (Please report this isssue!)")
        setattr(thing, key, new_value)

from .config import Config
