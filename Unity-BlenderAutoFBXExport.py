import bpy
import bmesh
#blender249 = True
#blender280 = (2,80,0) <= bpy.app.version
from bpy.app.handlers import persistent

bl_info = {
    "name": "Blender Auto FBX Export to Unity",
    "author": "Arch",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "File > Save",
    "description": ("Auto export to FBX along the blend file"),
    "warning": "",  # used for warning icon and text in addons panel
    "category": "System"}


# FUNCTION TO APPLY ALL SHARED MODIFIERS
#
@persistent
def ApplySharedModifiers():
    
    #start by OBJECT mode 
    bpy.ops.object.mode_set(mode='OBJECT')

    collections = bpy.data.collections
    cLen = len(collections)    
    objs = bpy.data.objects
    #objs = bpy.data.collections[0].all_objects
    oLen = len(objs)
    print("Will look for shared modifiers in "+str(objs)+" objects and "+str(cLen)+" collections")
    #1. Group by shared mesh data
    meshDataList = {}
    for obj in objs:

        if obj.data is None:
            print("No mesh data for "+obj.name)
            continue       

        meshDataName = obj.data.name

        if not meshDataList.get(meshDataName):
            meshDataList[meshDataName] = [] 
            print("Shared Mesh "+meshDataName)
            
        meshDataList[meshDataName].append(obj)
        print("\tAdd object"+obj.name)
        
    #2. Keep meshDataList with shared only data and modifiers.
    for meshDataName in meshDataList:
        # check same modifiers
        meshDataRef = meshDataList[meshDataName]
        meshData = meshDataRef[0]
        modifiers = meshData.modifiers
        
        #meshDataName are kept in blend files even if no object are referencing them. Check that before trying to select them.
        isInView = False
        for view in bpy.context.view_layer.objects:
            isInView |= view.name == meshData.name

        if not isInView:
            print("Ignore Mesh Data as not attached to any object in view : "+meshData.name)
            continue        
        
        print("Checking mesh data "+meshDataName)
                
        groupValid = ''
        for modifier in modifiers:
            print("\tChecking modifier "+modifier.name)
            for obj in meshDataRef[1:]:
              if obj.modifiers.find(modifier.name) == -1:
                  groupValid = obj.name+"."+modifier.name
                  break
        
        if not groupValid == '': 
            print("\tNot Shared "+groupValid)
            continue       

        #If there is no shared modifiers on same named mesh we should return to avoid blender import issues.     
        if len(modifiers) == 0:
            print("\tNo modifier on "+meshData.name)
            continue   

    

        #3. Apply to geometry modifiers on first meshData data    
        bpy.context.view_layer.objects.active = meshData
        meshData.select_set(state=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        #low level convert
        depGraph = bpy.context.evaluated_depsgraph_get()        
        bm = bmesh.new()
        bm.from_object(meshData, depGraph)
        bm.to_mesh(meshData.data)
        
        meshData.select_set(state=False)
        
        #4. clean modifiers for other
        for obj in meshDataRef:
            #print("\tobj.modifiers.clear()")
            obj.modifiers.clear()

@persistent
def ExportUnityFbx(dummy):
#    try:
#        import Blender
#    except:
#        blender249 = False

#    if not blender280:
#        if blender249:
#            try:
#                import export_fbx
#            except:
#                print('error: export_fbx not found.')
#                Blender.Quit()
#        else :
#            try:
#                import io_scene_fbx.export_fbx
#            except:
#                print('error: io_scene_fbx.export_fbx not found.')
#                # This might need to be bpy.Quit()
#                raise

    # Find the Blender output file
#    import os
#    outfile = os.getenv("UNITY_BLENDER_EXPORTER_OUTPUT_FILE")
#    if not outfile:
#        outfile = "./DebugLocal.fbx"
    import bpy.path
    import os

    try:
        path = bpy.data.filepath
        path.index(".uniblend")
    except ValueError:
        print("only export blend files with .uniblend extension")
        return
    
    print(".uniblend ext detectect file will be exported for unity")
    dirpath =  os.path.dirname(bpy.data.filepath)
    outname = bpy.path.display_name_from_filepath(bpy.data.filepath)
#    outname = outname.replace(".","") #replace the unity hiding prefix    
#    outname = outname.replace("_blend","") #replace the unity blend suffix    
    outname =  outname+".fbx"
    outfile = os.path.join(dirpath, outname)

    # Do the conversion
    print("Starting blender to FBX conversion " + outfile)

    #TRY APPLY ALL SHARED MODIFIERS
    try:
        ApplySharedModifiers()
    except Exception as e:
        print("Couldn't apply modifiers, see exception below. Will continue with default behaviour") 
        print(e) 

#    if blender280:
    import bpy.ops
    bpy.ops.export_scene.fbx(filepath=outfile,
        check_existing=False,
        use_selection=False,
        use_active_collection=False,
        object_types= {'ARMATURE','CAMERA','LIGHT','MESH','OTHER','EMPTY'},
        use_mesh_modifiers=True,
        mesh_smooth_type='OFF',
        use_custom_props=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=True,
        apply_scale_options='FBX_SCALE_ALL')
#    elif blender249:
#        mtx4_x90n = Blender.Mathutils.RotationMatrix(-90, 4, 'x')
#        export_fbx.write(outfile,
#            EXP_OBS_SELECTED=False,
#            EXP_MESH=True,
#            EXP_MESH_APPLY_MOD=True,
#            EXP_MESH_HQ_NORMALS=True,
#            EXP_ARMATURE=True,
#            EXP_LAMP=True,
#            EXP_CAMERA=True,
#            EXP_EMPTY=True,
#            EXP_IMAGE_COPY=False,
#            ANIM_ENABLE=True,
#            ANIM_OPTIMIZE=False,
#            ANIM_ACTION_ALL=True,
#            GLOBAL_MATRIX=mtx4_x90n)
#    else:
#        # blender 2.58 or newer
#        import math
#        from mathutils import Matrix
#        # -90 degrees
#        mtx4_x90n = Matrix.Rotation(-math.pi / 2.0, 4, 'X')

#        class FakeOp:
#            def report(self, tp, msg):
#                print("%s: %s" % (tp, msg))

#        exportObjects = ['ARMATURE', 'EMPTY', 'MESH']

#        minorVersion = bpy.app.version[1];
#        if minorVersion <= 58:
#            # 2.58
#            io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile,
#                global_matrix=mtx4_x90n,
#                use_selection=False,
#                object_types=exportObjects,
#                mesh_apply_modifiers=True,
#                ANIM_ENABLE=True,
#                ANIM_OPTIMIZE=False,
#                ANIM_OPTIMIZE_PRECISSION=6,
#                ANIM_ACTION_ALL=True,
#                batch_mode='OFF',
#                BATCH_OWN_DIR=False)
#        else:
#            # 2.59 and later
#            kwargs = io_scene_fbx.export_fbx.defaults_unity3d()
#            io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile, **kwargs)
#        # HQ normals are not supported in the current exporter

    print("Finished blender to FBX conversion " + outfile)
    
def register():
    if not ExportUnityFbx in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(ExportUnityFbx)

def unregister():
    if ExportUnityFbx in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(ExportUnityFbx)
        
if __name__ == "__main__":
    register()
