import maya
import pyblish.api


class ExtractSceneSave(pyblish.api.Extractor):
    """
    """
    hosts = ['maya']
    order = pyblish.api.Extractor.order - 0.45
    families = ['scene']
    label = 'Scene Save'

    def process(self, instance):

        self.log.info('saving scene')
        maya.cmds.file(s=True)
