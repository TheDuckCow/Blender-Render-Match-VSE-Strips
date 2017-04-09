bl_info = {
    "name": "Render Match VSE Strips",
    "description": "Operator that sets render resolution and start/end frame to match selected VSE strips",
    "author": "Patrick W. Crawford",
    "version": (1, 1),
    "blender": (2, 7, 7),
    "location": "VSE strip editor > Properties > Edit Strip (Panel): Match Strips",
    "wiki_url": "",
    "tracker_url":"",
    "category": "Sequencer"}

import bpy

class SEQUENCE_OT_match_sequence_resolution(bpy.types.Operator):
	"""Change the render settings and scene length to match selected strips"""
	bl_label = "Match Strip"
	bl_idname = "sequencer.match_sequence_resolution"
	bl_options = {'REGISTER', 'UNDO'}


	def execute(self, context):

		selection = [seq for seq in context.scene.sequence_editor.sequences if seq.select]
		seq_active = context.scene.sequence_editor.active_strip
		if seq_active.type == None or seq_active.type in ['SOUND','TRANSFORM']:
			self.report({'ERROR'}, "Active strip must be an image or video with inherent resolution")
			return {'CANCELLED'}
		
		# include active as well
		if seq_active not in selection:
			selection.append(seq_active)
		
		# base settings on the active strip
		context.scene.render.resolution_x = seq_active.elements[0].orig_width
		context.scene.render.resolution_y = seq_active.elements[0].orig_height

		# initialize to smallest frame
		endframe = 0

		# initialize to a frame that definitely is after start
		startframe = seq_active.frame_final_end

		# base frame start/end  on all of selected strips
		for seq in selection:
			if endframe < seq.frame_final_end:
				endframe = seq.frame_final_end
			if startframe > seq.frame_final_start:
				startframe = seq.frame_final_start

		context.scene.frame_end = endframe-1
		context.scene.frame_start = startframe

		return {'FINISHED'}


class SEQUENCE_OT_show_hide_strip_modifiers(bpy.types.Operator):
	"""Show, hide, or toggle visibility on all selected strip modifiers"""
	bl_label = "Match Strip"
	bl_idname = "sequencer.show_hide_strip_modifiers"
	bl_description = "Show, hide, or toggle visibility on all selected strip modifiers"
	bl_options = {'REGISTER', 'UNDO'}

	selection_only = bpy.props.BoolProperty(
		name="Only Selected",
		default=True,
		description="Only apply to selected strips")

	showhide = bpy.props.EnumProperty(
		items = [('show', 'Show', 'Make modifiers visible'),
				('hide', 'Hide', 'Make modifiers not visible'),
				('toggle', 'Toggle', 'Toggle modifier visilibity per modifier')],
		name = "show/hide",
		description = "Show, hide, or toggle all strip modifier")


	def execute(self, context):

		stps = []
		if self.selection_only==True:
			stps = [seq for seq in context.scene.sequence_editor.sequences if seq.select]
		else:
			stps = context.scene.sequence_editor.sequences

		for stp in stps:
			for mod in stp.modifiers:
				print(stp, mod)
				if self.showhide=="show":
					mod.mute=False
				elif self.showhide=="hide":
					mod.mute=True
				else:
					mod.mute = not mod.mute

			# add arbitrary property to each modifier (or to each stip)
			# on what the INITIAL state was??

		return {'FINISHED'}


def panel_append(self, context):
	self.layout.operator(SEQUENCE_OT_match_sequence_resolution.bl_idname)

def header_append(self, context):
	row = self.layout.row(align=True)
	row.operator(SEQUENCE_OT_show_hide_strip_modifiers.bl_idname,
		icon="RESTRICT_VIEW_OFF",text="").showhide = "show"
	row.operator(SEQUENCE_OT_show_hide_strip_modifiers.bl_idname,
		icon="ARROW_LEFTRIGHT",text="").showhide = "toggle"
	row.operator(SEQUENCE_OT_show_hide_strip_modifiers.bl_idname,
		icon="RESTRICT_VIEW_ON",text="").showhide = "hide"
	


def register():
	bpy.utils.register_class(SEQUENCE_OT_match_sequence_resolution)
	bpy.utils.register_class(SEQUENCE_OT_show_hide_strip_modifiers)
	bpy.types.SEQUENCER_PT_edit.append(panel_append)
	bpy.types.SEQUENCER_HT_header.append(header_append)

def unregister():
	bpy.utils.unregister_class(SEQUENCE_OT_match_sequence_resolution)
	bpy.utils.unregister_class(SEQUENCE_OT_show_hide_strip_modifiers)
	bpy.types.SEQUENCER_PT_edit.remove(panel_append)
	bpy.types.SEQUENCER_HT_header.append(header_append)


if __name__ == "__main__":
    register()
