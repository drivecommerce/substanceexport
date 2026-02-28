# pylint: disable=import-error, missing-module-docstring, missing-class-docstring, missing-function-docstring, line-too-long
from PySide6 import QtWidgets, QtCore, QtGui

import substance_painter as sp

import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import substance_painter.layerstack
import substance_painter.js
import substance_painter.ui

class ExportVariationsPlugin:
    def __init__(self):
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setWindowTitle("Export Variations")
        self.log.append("Waiting...")

        substance_painter.ui.add_dock_widget(self.log)

        self.export_action = QtGui.QAction("Export Variations...")

        self.export_action.triggered.connect(self.export_variations)
        substance_painter.ui.add_action(
            substance_painter.ui.ApplicationMenu.File,
            self.export_action
        )

    def __del__(self):
        substance_painter.ui.delete_ui_element(self.log)
        substance_painter.ui.delete_ui_element(self.export_action)

    def check_set(self, name):
        for s in range(1, 4):
            for v in range(1, 4):
                prefix = f'S{s}V{v}('
                if prefix in name:
                    return {
                        'prefix': prefix,
                        'set': f'set{s}',
                        'type': f'var{v}',
                    }
        return None

    def find_named_layers(self, layer, stack, layers):
        if hasattr(layer, 'get_name'):
            name = layer.get_name()

            check = self.check_set(name)

            self.log.append(f"{name} -> {check}")

            if 'FMT(' in name:
                layers.append({
                    'type': 'format',
                    'layer': layer
                })
            else:
                if check is not None:
                    layers.append({
                        'type': check['type'],
                        'set': check['set'],
                        'prefix': check['prefix'],
                        'layer': layer,
                        'stack': stack
                    })

        if type(layer) is sp.layerstack.GroupLayerNode:
            for child in layer.sub_layers():
                self.find_named_layers(child, stack, layers)

    def find_layers(self):
        texture_sets = sp.textureset.all_texture_sets()

        # Iterate over all texture sets
        for texture_set in texture_sets:
            layers = []

            for stack in texture_set.all_stacks():
                stack_root_nodes = sp.layerstack.get_root_layer_nodes(stack)
                for layer in stack_root_nodes:
                    self.find_named_layers(layer, stack.name(), layers)

            has_active_format = False

            for layer in layers:
                if layer['type'] == 'format' and layer['layer'].is_visible():
                    has_active_format = True

            if has_active_format:
                return texture_set, layers

        return None, None

    def add_layer(self, variations, index, variable, prefix, layer, stack):
        if index not in variations:
            variations[index] = {
                'index': 0,
                'variable': variable,
                'prefix': prefix,
                'layers': [],
                'stack': stack
            }

        variations[index]['layers'].append(layer)

    def extract_value(self, name, prefix):
        starts = name.find(prefix)
        ends = name.find(')', starts)
        return name[starts + len(prefix): ends]

    def replace_all(self, value, from_str, to_str):
        while True:
            result = value.replace(from_str, to_str)
            if result == value:
                return result
            value = result

    def export_set(self, layers, set_name, set_index, texture_set):
        variations = {}

        format_value = None

        for layer in layers:
            if layer['type'] == 'format':
                format_value = self.extract_value(layer['layer'].get_name(), 'FMT(')
                continue

            if layer['set'] != set_name:
                continue

            if layer['type'] == 'var1':
                self.log.append(f"Append 1 {layer['layer'].get_name()}")
                self.add_layer(variations, 0, 'VAR1', f'S{set_index}V1(', layer['layer'], layer['stack'])

            if layer['type'] == 'var2':
                self.log.append(f"Append 2 {layer['layer'].get_name()}")
                self.add_layer(variations, 1, 'VAR2', f'S{set_index}V2(', layer['layer'], layer['stack'])

            if layer['type'] == 'var3':
                self.log.append(f"Append 3 {layer['layer'].get_name()}")
                self.add_layer(variations, 2, 'VAR3', f'S{set_index}V3(', layer['layer'], layer['stack'])

        if not variations:
            return None

        if 1 in variations and 0 not in variations:
            self.log.append('Not all variation variables are defined')
            return None

        if 2 in variations and 1 not in variations:
            self.log.append('Not all variation variables are defined')
            return None

        self.log.append('Looping through variations...')

        for guard in range(10000):
            name = format_value

            # Hide all layers
            for layer in layers:
                if layer['type'] != 'format' and layer['set'] == set_name:
                    layer['layer'].set_visible(False)

            for variation in variations.values():
                layer = variation['layers'][variation['index']]

                # Enable only selected layers
                layer.set_visible(True)

                id_value = self.extract_value(layer.get_name(), variation['prefix'])

                name = self.replace_all(name, variation['variable'], id_value)

            self.log.append(f'... Variation {name}')

            self.log.append('Exporting...');

            script = '''
                function exportTextures() {
                    var log = [];

                    log.push('... Variation ' + name);

                    var channels = alg.mapexport.channelIdentifiers([]);
                    log.push('... has channels ' + channels);

                    var computed = alg.mapexport.convertedMapIdentifiers();
                    log.push('... has computed ' + computed);

                    var mesh = alg.mapexport.meshMapIdentifiers([textureSetName]);
                    log.push('... mesh maps ' + mesh);

                    var exportTo = alg.mapexport.exportPath();

                    exportTo = exportTo + '/' + name + '/' + textureSetName;

                    log.push('... ... export to ', exportTo);

                    alg.mapexport.save(
                        [
                            textureSetName,
                            'basecolor'
                        ],
                        exportTo + '_baseColor.png', {});

                    alg.mapexport.save(
                        [
                            textureSetName,
                            'normal'
                        ],
                        exportTo + '_normal.png', {});

                    alg.mapexport.saveConvertedMap(
                        [
                            textureSetName,
                            stackName,
                        ],
                        'ao_mixed',
                        exportTo + '_ambientOcclusion.png', {});

                    alg.mapexport.save(
                        [
                            textureSetName,
                            'roughness'
                        ],
                        exportTo + '_roughness.png', {});

                    alg.mapexport.save(
                        [
                            textureSetName,
                            'metallic'
                        ],
                        exportTo + '_metallic.png', {});

                    log.push('... ... saved.');

                    return log
                }

                exportTextures();
            '''

            script = f"var name = '{name}';\n" + \
                f"var textureSetName = '{texture_set.name()}';\n" + \
                f"var stackName = '{variations[0]['stack']}';\n" + \
                script

            result = substance_painter.js.evaluate(script)

            self.log.append(str(result))

            # Hide all layers
            for layer in layers:
                if layer['type'] != 'format' and layer['set'] == set_name:
                    layer['layer'].set_visible(False)

            next_increment = 0

            if 1 in variations:
                next_increment = 1

            if 2 in variations:
                next_increment = 2

            if 3 in variations:
                next_increment = 3

            while True:
                variations[next_increment]['index'] += 1
                if variations[next_increment]['index'] >= len(variations[next_increment]['layers']):
                    variations[next_increment]['index'] = 0
                    next_increment -= 1
                    if next_increment < 0:
                        self.log.append('Done making variations')
                        return True
                else:
                    break

    @QtCore.Slot()
    def export_variations(self):
        # Do the export.
        self.log.append("Export textures.")

        try:
            texture_set, layers = self.find_layers()

            if texture_set is not None:
                self.log.append(f'Exporting {texture_set.name()}')

                for set_index in range(1, 5):
                    self.log.append(f'Trying set {set_index}')

                    self.export_set(layers, f'set{set_index}', set_index, texture_set)

            self.log.append("Done.")
        except ValueError as err:
            self.log.append("Export failed.")
            self.log.append(repr(err))

EXPORT_PLUGIN = None

def start_plugin():
    global EXPORT_PLUGIN
    EXPORT_PLUGIN = ExportVariationsPlugin()

def close_plugin():
    global EXPORT_PLUGIN
    del EXPORT_PLUGIN

if __name__ == "__main__":
    start_plugin()
