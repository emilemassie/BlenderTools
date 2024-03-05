import bpy

class SetupCompositorForNuke():
    def __init__(self):
        self.settings  = {
            "output_path": "/tmp",
            "format": "OPEN_EXR_MULTILAYER",
            "color_depth": "16",
            "compression": 18,
            "render_passes" : ['Image','Alpha','Noisy Image','Depth'],
            "utl_passes" : ['Position','Normal','Vector','UV','Shadow','AO','CryptoObject00','CryptoObject01','CryptoObject02','CryptoMaterial00','CryptoMaterial01','CryptoMaterial02','CryptoAsset00','CryptoAsset01','CryptoAsset02'],
            "env_passes" : ['Mist']
        }
    def execute(self):

        # Access the current scene
        scene = bpy.context.scene
        # Enable the compositor
        scene.use_nodes = True
        links = scene.node_tree.links

        # Set the layer views
        view_layer = scene.view_layers['ViewLayer']
        view_layer.use_pass_combined = True
        view_layer.use_pass_z = True
        view_layer.use_pass_mist = True
        view_layer.use_pass_position = True
        view_layer.use_pass_normal = True
        view_layer.use_pass_vector = True
        view_layer.use_pass_uv = True

        view_layer.use_pass_environment = True
        view_layer.use_pass_shadow = True
        view_layer.use_pass_ambient_occlusion = True
        view_layer.cycles.use_pass_shadow_catcher = True

        view_layer.use_pass_cryptomatte_object = True
        view_layer.use_pass_cryptomatte_material = True
        view_layer.use_pass_cryptomatte_asset = True

        # Access the compositor nodes
        nodes = scene.node_tree.nodes

        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)

        # Add a Composite node
        composite_node = nodes.new(type='CompositorNodeComposite')
        composite_node.location = 1000, 500

        # Add a Render Layers node
        render_layers_node = nodes.new(type='CompositorNodeRLayers')
        # Position the node in the compositor editor
        render_layers_node.location = 0, 0
        render_layers_node.select = False

        # Add a File Output nodes
        self.file_nodes = {}
        self.settings['output_path'] = scene.render.filepath
        for output in ['beauty','utilities','environement']:
            file_output_node = nodes.new(type='CompositorNodeOutputFile')
            # Set ouput path
            file_output_node.base_path = self.settings.get('output_path')+ "_"+output
            # Set the output format to OpenEXR
            file_output_node.format.file_format = self.settings.get('format')
            # Set the output color depth to 16-bit float
            file_output_node.format.color_depth = self.settings.get('color_depth')
            # Set the output compression to Zip16
            file_output_node.format.compression = self.settings.get('compression')
            #file_output_node.inputs.remove(file_output_node.inputs.get('Image'))
            file_output_node.select = False
            self.file_nodes[output] = file_output_node

        self.file_nodes['beauty'].inputs.remove(self.file_nodes['beauty'].inputs.get('Image'))

        # Position the node in the compositor editor
        self.file_nodes['beauty'].location = 500, -500
        self.file_nodes['utilities'].location = 1000, -500
        self.file_nodes['environement'].location = 1500, -500

        # Add a viewer
        viewer_node = nodes.new(type='CompositorNodeViewer')
        viewer_node.location = 1000, 250

        
        # Connect and build all inputs with proper naming
        for layer in self.settings.get('render_passes'):
            layer_name = layer
            match layer_name:
                case "Image":
                    layer_name = "rgba"
                case "Alpha":
                    layer_name = "alpha"
            try:          
                self.file_nodes["beauty"].file_slots.new(layer_name)
                links.new(render_layers_node.outputs[layer], self.file_nodes["beauty"].inputs[layer_name])
            except:
                pass    

        for layer in self.settings.get('utl_passes'):
            layer_name = layer
            match layer_name:
                case "Vector":
                    layer_name = "motion"
                case "Position":
                    layer_name = "position"
            try:          
                self.file_nodes["utilities"].file_slots.new(layer_name)
                links.new(render_layers_node.outputs[layer], self.file_nodes["utilities"].inputs[layer_name])
            except:
                pass
        # Connect viewer and compositor
        links.new(render_layers_node.outputs[0], composite_node.inputs[0])
        links.new(render_layers_node.outputs[0], viewer_node.inputs[0])