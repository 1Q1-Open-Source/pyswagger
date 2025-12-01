from __future__ import absolute_import
import base64


class Byte(object):
    """ for string type, byte format
    """

    def apply_with(self, _, v, ctx):
        """ constructor

        :param str v: accept str or bytes
        """
        if isinstance(v, (bytes, bytearray)):
            self.v = v
        elif isinstance(v, str):
            self.v = v.encode('utf-8')
        else:
            raise ValueError('Unsupported type for Byte: ' + str(type(v)))

    def __str__(self):
        return self.v.decode('utf-8')

    def to_json(self):
        """ according to https://github.com/wordnik/swagger-spec/issues/50,
        we should exchange 'byte' type via base64 encoding.
        """
        return base64.urlsafe_b64encode(self.v).decode('utf-8')


