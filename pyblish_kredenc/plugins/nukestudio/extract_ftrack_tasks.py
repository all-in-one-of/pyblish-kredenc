import pyblish.api
import ftrack


class BumpyboxHieroExtractFtrackTasks(pyblish.api.Extractor):
    """ Extract Ftrack tasks.

    Offset to get shot from "extract_ftrack_shot"
    """

    families = ["task"]
    label = "Ftrack Tasks"
    optional = True
    order = pyblish.api.ExtractorOrder + 0.1

    def getTaskTypeByName(self, name):
        for t in ftrack.getTaskTypes():
            if t.getName().lower() == name.lower():
                return t

        return None

    def process(self, instance):

        shot = instance.data["ftrackShot"]
        tasks = shot.getTasks()

        for tag in instance[0].tags():
            data = tag.metadata().dict()
            if "task" == data.get("tag.family", ""):
                task = None
                try:
                    task = shot.createTask(
                        tag.name().lower(),
                        taskType=self.getTaskTypeByName(tag.name())
                    )
                except:
                    msg = "Could not create task \"{0}\"".format(tag.name())
                    self.log.info(msg)
                    for t in tasks:
                        if t.getName().lower() == tag.name().lower():
                            task = t

                # Store task id on tag
                tag.metadata().setValue("tag.id", task.getId())
