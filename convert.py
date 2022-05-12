#!/usr/bin/env python

import sqlite3

# Open the places.sqlite in the current working directory
db_connection = sqlite3.connect("./places.sqlite")

# Query the database for required fields. End up with a list of tuples.
data = db_connection.execute(
    "%s%s%s"
    % (
        "SELECT  moz_bookmarks.id, moz_bookmarks.parent, moz_bookmarks.type, ",
        "moz_bookmarks.title, moz_places.url from moz_bookmarks left join ",
        "moz_places on fk=moz_places.id ORDER BY moz_bookmarks.parent",
    )
).fetchall()

"""
A dictionary to store sorted bookmarks and directories. Each directory
represents a key value pair. The key is the unique moz_bookmarks.id from the
database. The value is a child dictionary.

In the child dictionary:
- data is the tuple extracted from the database for the directory
-  child_directories are a list of moz_bookmarks.id of all child directories
- child_items are a list of the child bookmark tuples
"""
bookmarks = {
    1: {"data": ("", "", "", "Bookmarks"), "child_directories": [], "child_items": []}
}


def insert_display_names(query_text: str):
    # Mapping of underlying identifiers in the databse to display names
    rename = {"toolbar": "Bookmarks Toolbar", "unfiled": "Other Bookmarks"}

    if query_text in rename.keys():
        query_text = rename[query_text]
    return query_text


def escape_markdown(str_to_escape: str):
    escape_mappings = {"[": "\\[", "]": "\\]", "<": "\\<", ">": "\\>", "|": "\\|"}
    for char_to_escape, escape_with in escape_mappings.items():
        str_to_escape = str_to_escape.replace(char_to_escape, escape_with)
    return str_to_escape


def add_directory_to_bookmarks_dict(row):
    bookmarks[row[0]] = {"data": row, "child_directories": [], "child_items": []}


def add_directory_to_parent_child_directories(row):
    bookmarks[row[1]]["child_directories"].append(row[0])


# Iterate through every row of the result from the database
for row in data:
    row = list(row)  # convert row to list as it needs to be mutable
    row[3] = insert_display_names(row[3])
    if row[2] == 2 and row[1] > 0:
        add_directory_to_bookmarks_dict(row)
        add_directory_to_parent_child_directories(row)
    elif row[2] == 1:
        row[3] = escape_markdown(row[3])
        if "place:" not in row[4]:
            bookmarks[row[1]]["child_items"].append(row)


def recurse_child_directories(x, y):
    print_title(x, y)
    print_children(x)
    if len(bookmarks[x]["child_directories"]) > 0:
        for directory_index in bookmarks[x]["child_directories"]:
            recurse_child_directories(directory_index, y + 1)


def print_children(x):
    if len(bookmarks[x]["child_items"]) > 0:
        for item in bookmarks[x]["child_items"]:
            print("- [%s](%s)" % (item[3], item[4]))
        print()


def print_title(x, y):
    """ """
    if has_children(x):
        title_tag = "#" * y
        print("%s %s \n" % (title_tag, bookmarks[x]["data"][3]))


def has_children(x):
    result = False
    if (
        len(bookmarks[x]["child_items"]) > 0
        or len(bookmarks[x]["child_directories"]) > 0
    ):
        result = True
    return result


recurse_child_directories(1, 1)
