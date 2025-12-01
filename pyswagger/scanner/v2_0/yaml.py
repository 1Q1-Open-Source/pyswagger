from __future__ import absolute_import
from ...scan import Dispatcher
from ...spec.v2_0.objects import (
    Operation
    )


class YamlFixer(object):
    """ fix objects loaded by pyaml """

    class Disp(Dispatcher): pass

    @Disp.register([Operation])
    def _op(self, _, obj, app):
        """ convert status code in Responses from int to string
        """
        if obj.responses == None: return 

        tmp = {}
        for k, v in obj.responses.items():
            if isinstance(k, int):
                tmp[str(k)] = v
            else:
                tmp[k] = v
        obj.update_field('responses', tmp)

