import logging

log = logging.getLogger(__name__)

def fuzzy_search(conn, what, search_for):
    if what == "drink":
        things = conn.drinks()
    elif what == "user":
        things = conn.users()
    possible_things = list()
    selected_thing = None
    for thing in things:
        if search_for.isdecimal():
            if int(search_for) == thing["id"]:
                selected_thing = thing
                break
        if search_for == thing["name"]:
            selected_thing = thing
            break
        elif search_for in thing["name"]:
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

def test_terminal_utf8():
    """Produces a warning if the system isn't correctly configured to output UTF-8."""
    from sys import stdout
    if stdout.encoding != "UTF-8":
        log.warning("Your system doesn't seem support UTF-8. Please consider fixing this.")

def true_false_to_yes_no(value):
    return "yes" if value else "no"

def yn(prompt):
    while True:
        entered = input("{} (y/n) ".format(prompt))
        if entered in ("yes", "y"):
            return True
        if entered in ("no", "n"):
            return False
        print("Please enter 'yes' or 'no'.")

def show_edit(dict, key, prompt, type):
    old_value = dict[key]
    if type == bool:
        old_value = true_false_to_yes_no(old_value)
    final_prompt = "{} [{}]: ".format(prompt, old_value)
    if type == bool:
        given = yn(final_prompt)
        dict[key] = given
        return
    else:
        given = input(final_prompt)
    if not given:
        given = old_value
    while True:
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
        elif type == "email":
            if "@" in given:
                new_value = given
                break
            else:
                print("This is not a valid email adress.")
                continue
        else:
            raise Exception("Unknown type. (Please report this isssue!)")
    dict[key] = new_value
