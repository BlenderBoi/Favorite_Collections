import bpy

def update_UI():
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()

def draw_subpanel(self, boolean, property, label, layout):

    if boolean:
        ICON = "TRIA_DOWN"
    else:
        ICON = "TRIA_RIGHT"

    row = layout.row(align=True)
    row.alignment = "LEFT"
    row.prop(self, property, text=label, emboss=False, icon=ICON)

    return boolean


class FC_UL_Favorite_Collection_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout = layout.row(align=True)

        layout.operator("favorite_collection.select_objects", text="", icon="OBJECT_DATAMODE").index = index

        layout.separator()

        if item.Collection:
            layout.prop(item.Collection, "hide_viewport", text="")
            layout.prop(item.Collection, "hide_render", text="")
            layout.prop(item.Collection, "hide_select", text="")

            layout.prop(item.Collection, "name", text="", emboss=False)
        else:
            layout.label(text="Pick a Collection", icon="ERROR")

        layout.prop(item, "Collection", text="", emboss=True)

        OPERATOR = layout.operator("favorite_collection.list_operator", icon="REMOVE", text="")
        OPERATOR.operation = "REMOVE"
        OPERATOR.index = index


class FC_OT_Select_Collection_Objects(bpy.types.Operator):
    """Select Collection Objects"""
    bl_idname = "favorite_collection.select_objects"
    bl_label = "Select Collection Objects"
    bl_options = {'REGISTER', 'UNDO'}

    index: bpy.props.IntProperty()

    def execute(self, context):

        scn = context.scene
        data = scn.Favorite_Collection_List[self.index]

        if data.Collection:

            check = any([object.select_get() for object in data.Collection.objects])

            for object in data.Collection.objects:

                object.select_set(not check)


        return {'FINISHED'}

class FC_OT_Collection_Select_Object(bpy.types.Operator):
    """Select Object (Shift Click to Add to Selection)"""
    bl_idname = "favorite_collection.select_this_object"
    bl_label = "Select This Object"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.StringProperty()
    object: bpy.props.StringProperty()

    def invoke(self, context, event):

        if self.operation == "SELECT":
            if event.shift:
                self.deselect = False
            else:
                self.deselect = True


        
        return self.execute(context)



    def execute(self, context):

        scn = context.scene

        object = scn.objects.get(self.object)
    
        if object:

            if self.operation == "SELECT":
                if self.deselect:
                    for obj in context.selected_objects:
                        obj.select_set(False)


                object.select_set(True)
                bpy.context.view_layer.objects.active = object



        return {'FINISHED'}







class FC_PT_Favorite_Collections(bpy.types.Panel):
    """Your Favorite Collection Panel"""
    bl_label = "Favorite Collection"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Favorite Collection"

    def draw(self, context):

        layout = self.layout

        scn = context.scene

        row = layout.row(align=True)
        row.template_list("FC_UL_Favorite_Collection_List", "", scn, "Favorite_Collection_List", scn, "Favorite_Collection_List_Index")

        index = scn.Favorite_Collection_List_Index

        col = row.column(align=True)

        col.operator("favorite_collection.list_operator", icon="ADD", text="").operation = "ADD"
        OPERATOR = col.operator("favorite_collection.list_operator", icon="REMOVE", text="")
        OPERATOR.operation = "REMOVE"
        OPERATOR.index = index
        col.separator()
        col.operator("favorite_collection.list_operator", icon="TRIA_UP", text="").operation = "UP"
        col.operator("favorite_collection.list_operator", icon="TRIA_DOWN", text="").operation = "DOWN"

        


        if len(scn.Favorite_Collection_List) > index:
            box = layout.box()
            row = box.row(align=True)
            if draw_subpanel(scn, scn.Favorite_Collection_Show_Objects, "Favorite_Collection_Show_Objects", "Show Objects", row):
                if scn.Favorite_Collection_Show_Objects:

                    item = scn.Favorite_Collection_List[index]
                    collection = item.Collection
                    if collection:

                        if len(collection.objects) > 0:
                            box.label(text="Filter")
                            col2 = box.column(align=True)
                            col2.prop(item, "Filter_name", text="")
                            col2.prop(item, "Filter_types", text="")
                            for object in collection.objects:

                                filter_item = True
                                filter_type = True


                                if item.Filter_name == "":
                                    filter_item = False
                                else:
                                    if item.Filter_name.lower() in object.name.lower():
                                        filter_item = False
                                    else:
                                        filter_item = True


                                if item.Filter_types == "ALL":
                                    filter_type= False

                                elif item.Filter_types == object.type:
                                    filter_type= False 

                                



                                if not filter_item and not filter_type:


                                    row2 = box.row(align=True)
                                    operation = row2.operator("favorite_collection.select_this_object",icon="OBJECT_DATA", text="")
                                    operation.object = object.name
                                    row2.separator()
                                    operation.operation = "SELECT"
                                    row2.prop(object, "hide_viewport", text="")
                                    row2.prop(object, "hide_render", text="")
                                    row2.prop(object, "hide_select", text="")

                                    row2.label(text=object.name, icon=object.type + "_DATA")


                        else:
                            box.label(text="No Object in Collection", icon="INFO")






ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"),("UP","Up","Up"),("DOWN","Down","Down")]

class FC_OT_List_Operator(bpy.types.Operator):
    """List Operator"""
    bl_idname = "favorite_collection.list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    index: bpy.props.IntProperty()
    Collection: bpy.props.StringProperty()

    def draw(self, context):

        layout = self.layout
        layout.prop_search(self, "Collection", bpy.data, "collections")


    def invoke(self, context, event):

        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):


        scn = context.scene

        item_list = scn.Favorite_Collection_List
        item_index = scn.Favorite_Collection_List_Index

        if len(item_list) > 0:

            if self.operation == "REMOVE":

                item_list.remove(self.index)

                if len(item_list) == scn.Favorite_Collection_List_Index:
                    scn.Favorite_Collection_List_Index = len(item_list) - 1

                update_UI()

                return {'FINISHED'}

            if self.operation == "UP":
                if item_index >= 1:
                    item_list.move(item_index, item_index-1)
                    scn.Favorite_Collection_List_Index -= 1
                    return {'FINISHED'}

            if self.operation == "DOWN":
                if len(item_list)-1 > item_index:
                    item_list.move(item_index, item_index+1)
                    scn.Favorite_Collection_List_Index += 1
                    return {'FINISHED'}

        if self.operation == "ADD":
            if self.Collection:
                if bpy.data.collections.get(self.Collection):
                    item = item_list.add()
                    item.Collection = bpy.data.collections.get(self.Collection)

                    scn.Favorite_Collection_List_Index = len(item_list) - 1
                    update_UI()

            return {'FINISHED'}

        update_UI()
        return {'FINISHED'}


def ENUM_filter_types(self, context):
    
    item_types = set()
    # items = [("ALL", "All", "All", 0, "RADIOBUT_ON"),]
    items = [("ALL", "All", "All", "RADIOBUT_ON", 0)]

    if self.Collection:
        for object in self.Collection.objects:
            item_types.add(object.type)

    for index, type in enumerate(item_types):
        # items.append([type, type.capitalize(), type, type + "_DATA", index+1])
        items.append((type, type.capitalize(), type, type + "_DATA", index+1))

    if len(items) > 0:
        pass
    else:
        items = [("None","None","None")]


    
    return items
                
                

class Favorite_Collections_Property(bpy.types.PropertyGroup):
    Collection : bpy.props.PointerProperty(type=bpy.types.Collection)
    Filter_types: bpy.props.EnumProperty(items=ENUM_filter_types)
    Filter_name: bpy.props.StringProperty(options={'TEXTEDIT_UPDATE'})





classes = [FC_OT_Collection_Select_Object, Favorite_Collections_Property, FC_OT_List_Operator, FC_UL_Favorite_Collection_List, FC_PT_Favorite_Collections, FC_OT_Select_Collection_Objects]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Favorite_Collection_List = bpy.props.CollectionProperty(type=Favorite_Collections_Property)
    bpy.types.Scene.Favorite_Collection_List_Index = bpy.props.IntProperty()
    bpy.types.Scene.Favorite_Collection_Show_Objects = bpy.props.BoolProperty()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.Favorite_Collection_List
    del bpy.types.Scene.Favorite_Collection_List_Index
    del bpy.types.Scene.Favorite_Collection_Show_Objects

if __name__ == "__main__":
    register()
