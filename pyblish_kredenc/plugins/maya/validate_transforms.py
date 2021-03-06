import math

import pymel
import pyblish.api


@pyblish.api.log
class ValidateTransforms(pyblish.api.Validator):
    """"""

    families = ['model']
    optional = True
    label = 'Model - Transforms'

    def process(self, instance):

        check = True
        for node in instance:
            # skipping references

            node = pymel.core.PyNode(node)

            if node.isReferenced():
                return

            transform = node.root()
            v = sum(transform.getRotatePivot(space='world'))
            if (math.ceil(v*100.0)/100.0) > 0.01:
                msg = '"%s" pivot is not at world zero.' % transform.name()
                self.log.error(msg)
                check = False

            v = sum(transform.getRotation(space='world'))
            if (math.ceil(v*100.0)/100.0) > 0.01:
                msg = '"%s" pivot axis is not aligned to world.' % transform.name()
                self.log.error(msg)
                check = False

            if sum(transform.scale.get()) != 3:
                msg = '"%s" scale is not neutral.' % transform.name()
                self.log.error(msg)
                check = False

        msg = "Transforms in the scene aren't reset."
        msg += ' Please reset by moving the pivot to world zero,'
        msg += ' and freeze the transform.'
        assert check, msg
