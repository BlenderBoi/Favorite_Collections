bl_info = {
    "name": "Favorite Collection",
    "author": "BlenderBoi",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "description": "",
    "wiki_url": "",
    "category": "Collection",
}

import bpy
from . import Favorite_Collection

modules = [
    Favorite_Collection,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
