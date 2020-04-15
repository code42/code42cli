from code42cli import PRODUCT_NAME


def create_namespace(detection_list_type):
    return "{}.cmds.detectionlists.{}".format(PRODUCT_NAME, detection_list_type)


class DetectionListMockFactory(object):
    def __init__(self, mocker, detection_list_type):
        self.mocker = mocker
        self._type = detection_list_type
        self.namespace = create_namespace(detection_list_type)

    def create_bulk_template_generator(self):
        return self.mocker.patch("{}.generate_template".format(self.namespace))

    def create_bulk_processor(self):
        return self.mocker.patch("{}.run_bulk_process".format(self.namespace))
