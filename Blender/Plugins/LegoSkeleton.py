bl_info = {
    "name": "Lego skeleton manager",
    "category": "Object",
}

import bpy

origin= (0,0,0)
amtName = "Armature"

class Utils(bpy.types.Operator):
    """Utils3000"""
    bl_idname = "object.utils3000"
    bl_label = "Util3000"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        obj = context.selected_objects[0]
        objData = obj.data
        for vert in objData.vertices:
            inf = []
            for influence in objData.getVertexInfluences(vert.index):
                inf.append(influence)
                print(vert.index,':',influence)
        

class LegoSkeletonCreator(bpy.types.Operator):
    """Lego Skeleton Creator"""
    bl_idname = "object.lego_skeleton_creator"
    bl_label = "Lego Skeleton Creator"
    bl_options =  {'REGISTER','UNDO'}
    
    def handle_torso(self, amt):
        bone = amt.edit_bones.new('Torso')

        bone.head = origin
        bone.tail = (0,0,1.2)

        self.handle_head(amt,bone)
        self.handle_shoulder(amt,bone,True)
        self.handle_shoulder(amt,bone,False)
        self.handle_leg(amt,bone,True)
        self.handle_leg(amt,bone,False)
    
    def handle_head(self, amt, torso):
        bone = amt.edit_bones.new('Head')
        bone.use_connect = True
        bone.parent = torso
        bone.head = torso.tail
        bone.tail = (0,0,2.2)
    
    def handle_shoulder(self, amt, torso, isLeft):
        bone = amt.edit_bones.new('Shoulder' + ((isLeft and 'L') or 'R'))
        bone.use_connect = True
        bone.parent = torso
        
        bone.head = torso.tail
        x=0.443
        z=1.122
        bone.tail = ((isLeft and x) or -x,0,z)
        
        self.handle_arm(amt,bone,isLeft)
    
    def handle_arm(self, amt, shoulder, isLeft):
        bone = amt.edit_bones.new('Arm' + ((isLeft and 'L') or 'R'))
        bone.use_connect = True
        bone.parent = shoulder
        
        bone.head = shoulder.tail
        x = 0.771
        z = 1.179
        bone.tail = ((isLeft and x) or -x,0,z)
        self.handle_hand(amt,bone,isLeft)
        
    def handle_hand(self, amt, arm, isLeft):
        bone = amt.edit_bones.new('Hand' + ((isLeft and 'L') or 'R'))
        bone.parent = arm
        
        hx = 0.882
        hy = -0.014
        hz = 0.82
        bone.head = ((isLeft and hx) or -hx,hy,hz)
        
        tx = 0.956
        ty = -0.414
        tz = 0.42
        bone.tail = ((isLeft and tx) or -tx,ty,tz)
        
    def handle_leg(self, amt, torso, isLeft):
        bone = amt.edit_bones.new('Leg' + ((isLeft and 'L') or 'R'))
        bone.parent = torso
        
        hx = 0.4
        hz = -0.2
        bone.head = ((isLeft and hx) or -hx,0,hz)
        
        tx = 0.4
        tz=-1.3
        bone.tail = ((isLeft and tx) or -tx,0,tz)

    def handle_constraints(self, bone):
        locConst = bone.constraints.new('LIMIT_LOCATION')
        rotConst = bone.constraints.new('LIMIT_ROTATION')
        locConst.owner_space = 'LOCAL'
        rotConst.owner_space = 'LOCAL'
        
        s = bone.name
                
        #locConst.min_x = locConst.min_y = locConst.min_z = 0
        #locConst.max_x = locConst.max_y = locConst.max_z = 0
        locConst.use_min_x = locConst.use_min_y = locConst.use_min_z = True
        locConst.use_max_x = locConst.use_max_y = locConst.use_max_z = True
        
        #rotConst.min_x = rotConst.min_y = rotConst.min_z = 0
        #rotConst.max_x = rotConst.max_y = rotConst.max_z = 0
        rotConst.use_limit_x = rotConst.use_limit_y = rotConst.use_limit_z = True
        
        
        if s == "Torso":
            locConst.use_min_x = locConst.use_min_y = locConst.use_min_z = False
            locConst.use_max_x = locConst.use_max_y = locConst.use_max_z = False
            rotConst.use_limit_x = rotConst.use_limit_y = rotConst.use_limit_z = False
        elif s == "Head":
            rotConst.use_limit_y = False
        elif s == "ShoulderL" or s == "ShoulderR":
            pass
        elif s == "ArmL" or s == "ArmR":
            rotConst.use_limit_y = False
        elif s == "HandL" or s == "HandR":
            rotConst.use_limit_y = False
        elif s == "LegL" or s == "LegR":
            rotConst.use_limit_x = False
        else:
            print('Error, bone name "'+ s +'" not recognized')
        

    def rig(self, pieces, amt):
        bpy.ops.object.mode_set(mode='EDIT')
        amtObject = bpy.data.objects[amtName]
        amtLocation = amtObject.location
        for o in pieces:
        
            minDist = 1000
            nearest_bone = None
            #bpy.ops.mesh.primitive_uv_sphere_add(location=bone.center + amtLocation)
            #bpy.context.object.scale = (0.1,0.1,0.1)
            #bpy.context.object.name = "sphere" + bone.name
            for bone in amt.edit_bones:
                for pos in [bone.tail,bone.center,bone.head]:
                    l = (o.location - (pos + amtLocation)).length
                    #print(o.name,": (",o.location,'-',bone.center,') =>',len)
                    if l < minDist:
                        minDist = l
                        nearest_bone = bone
            #print(o.name,'is near',nearest_bone.name)
            bpy.ops.object.parent_set(type='ARMATURE_NAME')
            
            existingMod = None
            if o.modifiers:
                for mod in o.modifiers:
                    if mod.name == "SkeletonLego":
                        existingMod = mod
            
            mod = existingMod or o.modifiers.new(name='SkeletonLego',type='ARMATURE')
            mod.object = amtObject

            name = nearest_bone.name
            
            #putting full weight for each object
            #print(o.vertex_groups)
            if not name in o.vertex_groups:
                group = o.vertex_groups.new(name)
            else:
                group = o.vertex_groups[name]
            
            vertCount = len(o.data.vertices)
            allVertices = range(vertCount)
            group.add(allVertices,1,"ADD")
            
        #adding bone constraints
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        amtObject.select = True
        bpy.context.scene.objects.active = amtObject
        bpy.ops.object.mode_set(mode='POSE')
        
        for bone in amtObject.pose.bones:
            bone.bone.select = True
            amt.bones.active = bone.bone
            self.handle_constraints(bone)            
        
        bpy.ops.object.mode_set(mode='EDIT')
        

    def execute(self, context):
        print('#################### Début Programme #####################')
        
        oldAmt = bpy.data.objects.get(amtName)
        if oldAmt:
            oldAmt.select = False
        
        pieces = context.selected_objects
        for p in pieces:
            p.select = False
        
        bpy.ops.object.delete()

        bpy.ops.object.add(
            type='ARMATURE',
            enter_editmode=False,
            location=(0,0,1.41082))
        
        bpy.ops.object.mode_set(mode='EDIT')
        ob = bpy.context.object
        amt = ob.data
        self.handle_torso(amt)
        self.rig(pieces,amt)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class LegoSkeletonSpectator(bpy.types.Operator):
    """Lego Skeleton Spectator"""
    bl_idname = "object.lego_skeleton_spectator"
    bl_label = "Lego Skeleton Analyser"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        ob = bpy.context.object
        amt = ob.data
        for bone in amt.bones:
            print(bone.name,":",bone.tail)
        return {'FINISHED'}
        

def register():
    bpy.utils.register_class(LegoSkeletonCreator)
    bpy.utils.register_class(LegoSkeletonSpectator)
    bpy.utils.register_class(Utils)


def unregister():
    bpy.utils.unregister_class(LegoSkeletonCreator)
    bpy.utils.unregister_class(LegoSkeletonSpectator)
    bpy.utils.register_class(Utils)


if __name__ == "__main__":
    register()