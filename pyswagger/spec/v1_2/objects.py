from __future__ import absolute_import
from ..base import BaseObj, FieldMeta, Context
import copy


class BaseObj_v1_2(BaseObj):
    __swagger_version__ = '1.2'


class Items(BaseObj_v1_2, metaclass=FieldMeta):
    """ Items Object
    """
    __swagger_fields__ = {
        '$ref': None,
        'type': None,
        'format': None,
    }


class ItemsContext(Context):
    """ Context of Items Object
    """
    __swagger_ref_object__ = Items


class DataTypeObj(BaseObj_v1_2):
    """ Data Type Fields
    """
    __swagger_fields__ = {
        'type': None,
        '$ref': None,
        'format': None,
        'defaultValue': None,
        'enum': None,
        'items': None,
        'minimum': None,
        'maximum': None,
        'uniqueItems': None,
    }

    def __init__(self, ctx):
        # Items Object, too lazy to create a Context for DataTypeObj
        # to wrap this child.
        items_data = ctx._obj.get('items', None)
        if items_data:
            with ItemsContext(ctx._obj, 'items') as items_ctx:
                items_ctx.parse(items_data)
        else:
            setattr(self, self.get_private_name('items'), None)

        super(DataTypeObj, self).__init__(ctx)

class Scope(BaseObj_v1_2, metaclass=FieldMeta):
    """ Scope Object
    """

    __swagger_fields__ = {
        'scope': None,
        'description': None,
    }


class LoginEndpoint(BaseObj_v1_2, metaclass=FieldMeta):
    """ LoginEndpoint Object
    """

    __swagger_fields__ = {
        'url': None,
    }


class Implicit(BaseObj_v1_2, metaclass=FieldMeta):
    """ Implicit Object
    """

    __swagger_fields__ = {
        'loginEndpoint': None,
        'tokenName': None,
    }


class TokenRequestEndpoint(BaseObj_v1_2, metaclass=FieldMeta):
    """ TokenRequestEndpoint Object
    """

    __swagger_fields__ = {
        'url': None,
        'clientIdName': None,
        'clientSecretName': None,
    }


class TokenEndpoint(BaseObj_v1_2, metaclass=FieldMeta):
    """ TokenEndpoint Object
    """

    __swagger_fields__ = {
        'url': None,
        'tokenName': None,
    }


class AuthorizationCode(BaseObj_v1_2, metaclass=FieldMeta):
    """ AuthorizationCode Object
    """

    __swagger_fields__ = {
        'tokenRequestEndpoint': None,
        'tokenEndpoint': None,
    }


class GrantType(BaseObj_v1_2, metaclass=FieldMeta):
    """ GrantType Object
    """

    __swagger_fields__ = {
        'implicit': None,
        'authorization_code': None,
    }


class Authorizations(BaseObj_v1_2, metaclass=FieldMeta):
    """ Authorizations Object
    """

    __swagger_fields__ = {
        'scope': None,
        'description': None,
    }


class Authorization(BaseObj_v1_2, metaclass=FieldMeta):
    """ Authorization Object
    """

    __swagger_fields__ = {
        'type': None,
        'passAs': None,
        'keyname': None,
        'scopes': None,
        'grantTypes': None,
    }

    def get_name(self, path):
        return path.split('/', 3)[2]


class ResponseMessage(BaseObj_v1_2, metaclass=FieldMeta):
    """ ResponseMessage Object
    """

    __swagger_fields__ = {
        'code': None,
        'message': None,
        'responseModel': None,
    }


class Parameter(DataTypeObj, metaclass=FieldMeta):
    """ Parameter Object
    """

    __swagger_fields__ = {
        'paramType': None,
        'name': None,
        'required': None,
        'allowMultiple': None,
        'description': None,
    }


class Operation(DataTypeObj, metaclass=FieldMeta):
    """ Operation Object
    """

    __swagger_fields__ = {
        'method': None,
        'nickname': None,
        'authorizations': None,
        'parameters': None,
        'responseMessages': None,
        'produces': None,
        'consumes': None,
        'deprecated': None,
        'summary': None,
        'notes': None,
    }

    __internal_fields__ = {
        # path from Api object, concated with Resource object
        'path': None,
    }

    def get_name(self, path):
        return self.nickname


class Api(BaseObj_v1_2, metaclass=FieldMeta):
    """ Api Object
    """

    __swagger_fields__ = {
        'path': None,
        'operations': None,
        'description': None,
    }


class Property(DataTypeObj, metaclass=FieldMeta):
    """ Property Object
    """

    __swagger_fields__ = {
        'description': None,
    }     


class Model(BaseObj_v1_2, metaclass=FieldMeta):
    """ Model Object
    """

    __swagger_fields__ = {
        'id': None,
        'required': [],
        'properties': None,
        'subTypes': None,
        'discriminator': None,
        'description': None,
    }

    __internal_fields__ = {
        # for model inheritance
        '_extends_': None,
    }

    def get_name(self, path):
        return self.id


class Resource(BaseObj_v1_2, metaclass=FieldMeta):
    """ Resource Object
    """

    __swagger_fields__ = {
        'swaggerVersion': None,
        'apiVersion': None,
        'apis': None,
        'basePath': None,
        'resourcePath': None,
        'models': None,
        'produces': None,
        'consumes': None,
        'authorizations': None,
        'description': None,
    }

    def __init__(self, ctx):
        """ The original structure of API object is very bad
        for seeking nickname for operations. Since nickname is unique
        in one Resource, we can just make it flat.
        """
        super(Resource, self).__init__(ctx)

        new_api = {}
        for api in ctx._obj['apis']:
            for op in api.operations:
                name = op.nickname
                if name in new_api.keys():
                    raise ValueError('duplication operation found: ' + name)

                # Operation objects now have 'path' attribute.
                op.update_field('path', api.path)
                # Operation objects' parent is now Resource object(API Declaration).
                op._parent__ = self
                new_api[name] = op

        # replace Api with Operations
        self.update_field('apis', new_api)

    def get_name(self, path):
        return path.split('/', 3)[2]


class Info(BaseObj_v1_2, metaclass=FieldMeta):
    """ Info Object
    """

    __swagger_fields__ = {
        'title': None,
        'termsOfServiceUrl': None,
        'contact': None,
        'license': None,
        'licenseUrl': None,
        'description': None,
    }


class ResourceList(BaseObj_v1_2, metaclass=FieldMeta):
    """ Resource List Object
    """
    __swagger_fields__ = {
        'swaggerVersion': None,
        'apis': None,
        'apiVersion': None,
        'info': None,
        'authorizations': None,
    }

