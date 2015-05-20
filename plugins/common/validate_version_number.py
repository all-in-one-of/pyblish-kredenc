import pyblish.api
import re
import sys
import pprint

@pyblish.api.log
class ValidateVersionNumber(pyblish.api.Validator):
    """Validates whether version number of output matches version of the
    work file
    """

    families = ['writeNode', 'prerenders', 'mantra']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    host = sys.executable.lower()

    def process_instance(self, instance):
        current_file = instance.context.data('current_file')
        current_v = int(self.version_get(current_file, 'v')[1])
        output_path = instance.data('output_path')

        try:
            output_v = int(self.version_get(output_path, 'v')[1])
        except:
            output_v = current_v

        if current_v != output_v:
            msg = 'Version number %s is not the same as ' % output_v
            msg += 'file version number %s' % current_v
            raise Exception(msg)


    def repair_instance(self, instance):
        """Sets the version number of the output to the same as the file name
        """
        current_file = instance.context.data('currentFile')
        output_path = instance.data('output_path')
        version_number = int(self.version_get(current_file, 'v')[1])
        v = int(self.version_get(output_path, 'v')[1])
        new_path = self.version_set(output_path, 'v', v, version_number)

        if "nuke" in self.host:
            self.set_output_nuke(instance, new_path)
        elif "maya" in self.host:
            pass
            # self.set_output_maya(instance, new_path)
        elif "houdini" in self.host:
            self.set_output_houdini(instance, new_path)
        else:
            output_path = None
            self.log.warning('version validation in current host is not supported yet!')

        instance[0]['file'].setValue(new_path)


    def version_get(self, string, prefix, suffix = None):
        """Extract version information from filenames.  Code from Foundry's nukescripts.version_get()"""

        if string is None:
           raise ValueError, "Empty version string - no match"

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            msg = "No \"_"+prefix+"#\" found in \""+string+"\""
            raise ValueError, msg
        return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())


    def version_set(self, string, prefix, oldintval, newintval):
        """Changes version information from filenames. Code from Foundry's nukescripts.version_set()"""

        regex = "[/_.]"+prefix+"\d+"
        matches = re.findall(regex, string, re.IGNORECASE)
        if not len(matches):
            return ""

        # Filter to retain only version strings with matching numbers
        matches = filter(lambda s: int(s[2:]) == oldintval, matches)

        # Replace all version strings with matching numbers
        for match in matches:
            # use expression instead of expr so 0 prefix does not make octal
            fmt = "%%(#)0%dd" % (len(match) - 2)
            newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
            string = re.sub(match, newfullvalue, string)
        return string


    def version_up(self, string):

        try:
            (prefix, v) = self.version_get(string, 'v')
            v = int(v)
            file = self.version_set(string, prefix, v, v+1)
        except:
            raise ValueError, 'Unable to version up File'

        return file


    # NUKE
    def set_output_nuke(self, instance, new_path):
        import nuke
        instance[0]['file'].setValue(new_path)

    # HOUDINI
    def set_output_houdini(self, instance, new_path):
        import hou
        instance[0].parm('vm_picture').set(new_path)