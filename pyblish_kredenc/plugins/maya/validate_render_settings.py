import os

import pymel
import pyblish.api

from ft_studio import ft_maya, ft_pathUtils
reload(ft_maya)


class RepairRenderSettings(pyblish.api.Action):
    label = "Repair"
    on = "failed"
    icon = "wrench"

    def process(self, instance):

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        # repairing current render layer
        layer = pymel.core.PyNode('defaultRenderLayer')
        pymel.core.nodetypes.RenderLayer.setCurrent(layer)

        # repairing frame/animation ext
        render_globals.animation.set(1)
        render_globals.outFormatControl.set(0)
        render_globals.putFrameBeforeExt.set(1)
        render_globals.extensionPadding.set(4)
        render_globals.periodInExt.set(1)

        # repairing frame padding
        render_globals.extensionPadding.set(4)

        # repairing file name prefix
        expected_prefix = '<RenderLayer>/<Version>/<Scene>'
        render_globals.imageFilePrefix.set(expected_prefix)

        # repairing renderpass naming
        render_globals.multiCamNamingMode.set(1)
        render_globals.bufferName.set('<RenderPass>')

        # repairing workspace path
        path = os.path.dirname(pymel.core.system.sceneName())
        pymel.core.system.Workspace.open(path)

        # repairing default lighting
        render_globals.enableDefaultLight.set(False)

        version = instance.context.data['version']
        render_globals.renderVersion.set('v' + version)

        # repairing image path
        output = self.get_path(instance)
        pymel.core.system.Workspace.fileRules['images'] = output
        pymel.core.system.Workspace.save()




class ValidateRenderSettings(pyblish.api.Validator):
    """ Validates settings """

    families = ['deadline.render']
    optional = True
    label = 'Render Settings'

    actions = [RepairRenderSettings]

    def get_path(self, instance):

        ftrack_data = instance.context.data('ftrackData')
        taskid = instance.context.data('ftrackData')['Task']['id']

        if 'Asset_Build' not in ftrack_data.keys():
            templates = [
                'shot.task.output'
            ]
        else:
            templates = [
                'asset.task.output'
            ]

        root = instance.context.data('ftrackData')['Project']['root']
        renderFolder = ft_pathUtils.getPathsYaml(taskid,
                                                 templateList=templates,
                                                 root=root)
        renderFolder = renderFolder[0]

        return renderFolder.replace('\\', '/')

    def process(self, instance):

        if instance.context.has_data('renderOutputChecked'):
            return
        else:
            instance.context.set_data('renderOutputChecked', value=True)

        render_globals = pymel.core.PyNode('defaultRenderGlobals')

        fails = []

        # validate frame/animation ext
        msg = 'Frame/Animation ext is incorrect. Expected: "name.#.ext".'
        if (render_globals.animation.get() != 1 or
                render_globals.outFormatControl.get() != 0 or
                render_globals.putFrameBeforeExt.get() != 1 or
                render_globals.extensionPadding.get() != 4 or
                render_globals.periodInExt.get() != 1):
            fails.append(msg)

        # validate frame padding
        msg = 'Frame padding is incorrect. Expected: 4'
        if not render_globals.extensionPadding.get() == 4:
            fails.append(msg)

        # validate file name prefix
        msg = 'File name prefix is incorrect.'
        prefix = render_globals.imageFilePrefix.get()
        expected_prefix = '<RenderLayer>/<Version>/<Scene>'
        if not prefix == expected_prefix:
            fails.append(msg)

        # validate renderpass naming
        msg = 'Renderpass naming is incorrect:'
        msg += '\n\n"Frame Buffer Naming": "Custom"'
        msg += '\n\n"Custom Naming String": "<RenderPass>"'
        data = instance.data('data')
        if 'multiCamNamingMode' in data:
            if (int(data['multiCamNamingMode']) != 1 or
                    render_globals.bufferName.get() != '<RenderPass>'):
                fails.append(msg)

        # validate default lighting off
        msg = 'Default lighting is enabled.'
        if render_globals.enableDefaultLight.get():
            fails.append(msg)

        # ftrack dependent validation
        if not instance.context.has_data('ftrackData'):
            return

        # validate image path
        expected_output = self.get_path(instance)
        output = str(pymel.core.system.Workspace.fileRules['images'])
        msg = 'Project Images directory is incorrect.'
        msg += ' Expected: %s' % expected_output
        if not output == expected_output:
            fails.append(msg)

        version = instance.context.data['version']
        version_label = render_globals.renderVersion.get()
        msg = 'Version Label is incorrect.'
        msg += ' Expected: v{}'.format(version)
        if not version_label == ('v' + version):
            fails.append(msg)

        if len(fails) > 0:
            for fail in fails:
                self.log.error(fail)

        assert len(fails) == 0, 'Some things need to be fixed'
