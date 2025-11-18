from __future__ import absolute_import
import uuid
import six
from ..errs import ValidationError


class UUID(object):
    """ wrapper of uuid.UUID
    """

    def __str__(self):
        return str(self.v)

    def to_json(self):
        return str(self.v)

    def apply_with(self, _, val, ctx):
        """ constructor

        :param val: things used to construct uuid
        :type val: uuid as byte, string, or uuid.UUID
        """
        if isinstance(val, uuid.UUID):
            # Accept uuid.UUID directly; store as-is
            self.v = val
        elif isinstance(val, six.string_types):
            # Enforce hyphenated RFC 4122 form to avoid accepting ambiguous/non-standard inputs
            s = val.strip()
            # quick shape check: 36 length with 4 hyphens at standard positions
            if len(s) != 36 or not (s[8] == s[13] == s[18] == s[23] == '-'):
                raise ValidationError('Invalid UUID string (expected hyphenated RFC 4122 form): {0}'.format(val))
            try:
                self.v = uuid.UUID(s)
            except (ValueError, AttributeError, TypeError):
                raise ValidationError('Invalid UUID string: {0}'.format(val))
        elif isinstance(val, six.binary_type):
            # TODO: how to support bytes_le?
            self.v = uuid.UUID(bytes=val)
        else:
            raise ValueError('Unrecognized type for UUID: ' + str(type(val)))
