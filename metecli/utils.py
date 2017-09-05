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