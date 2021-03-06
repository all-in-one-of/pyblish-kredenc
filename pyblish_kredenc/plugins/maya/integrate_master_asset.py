import shutil
import os
import pyblish.api


@pyblish.api.log
class IntegrateMasterAsset(pyblish.api.InstancePlugin):
    """Copies asset to it's final location
    """

    order = pyblish.api.IntegratorOrder
    # order = pyblish.api.ValidatorOrder
    families = ['model', 'rig', 'cache', 'look', 'location', 'prop']
    label = 'Master Asset'
    optional = True

    def process(self, instance):

        extractedPaths = [v for k,v in instance.data.items() if k.startswith('outputPath')]
        self.log.debug(extractedPaths)
        for path in extractedPaths:

            sourcePath = path
            filename, ext = os.path.splitext(sourcePath)
            self.log.debug(sourcePath)

            master_file = instance.data['masterFile']

            master_file = os.path.splitext(master_file)[0] + ext
            self.log.debug(master_file)

            self.log.debug('master file: {}'.format(master_file))

            d = os.path.dirname(master_file)
            if not os.path.exists(d):
                os.makedirs(d)
            shutil.copy(sourcePath, master_file)
