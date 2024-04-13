# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

from mixbox import entities, fields, idgen

import cybox
import cybox.utils
import cybox.bindings.cybox_core as core_binding
from cybox.common import MeasureSource, StructuredText
from cybox.common.location import Location, LocationFactory
from cybox.common.object_properties import ObjectPropertiesFactory, ObjectProperties
from cybox.common.vocabs import VocabField
from cybox.common.vocabs import ObjectRelationship as Relationship
from cybox.core.effect import DefinedEffectFactory

_EXTERNAL_CLASSES = {}  # Maps xsi:type values to binding


def add_external_class(klass, xsi_type):
    """Adds a class implementation to this binding's globals() dict.

    These classes can be used to implement Properties,
    Domain_Specific_Object_Properties, or Defined_Effect fields on an Object.

    Args:
        klass (class): Python class that implements the new type
        xsi_type (str): An xsi:type value corresponding to the `klass`.
    """
    _EXTERNAL_CLASSES[xsi_type] = klass


class ExternalTypeFactory(entities.EntityFactory):
    def entity_class(cls, key):
        return _EXTERNAL_CLASSES[key]


def _modify_properties_parent(instance, value=None):
    if isinstance(instance, RelatedObject) and not instance._inline:
        return
    if instance.properties:
        instance.properties.parent = instance


def _cache_object(instance, value=None):
    if instance.id_:
        cybox.utils.cache_put(instance)


class Object(entities.Entity):
    """
    The CybOX Object construct identifies and specifies the characteristics of
    a specific cyber-relevant object (e.g. a file, a registry key or a
    process).

    Currently only supports the following data members:
    - id
    - idref
    - has_changed
    - description
    - properties
    - related_objects
    - domain_specific_object_properties

    Notes:
        By default ``cybox.core.object.Object`` will cache objects when
        instantiated. If your are experiencing memory issues in your
        environment, we encourage the use of ``cybox.utils.caches.cache_clear()``
        in your script to prevent an Out of Memory error. Depending on your
        use case, it can be after serialization or if a certain threshold is
        met (e.g. %30 of memory consumed by cache mechanism).

    """
    _binding = core_binding
    _binding_class = _binding.ObjectType
    _namespace = 'http://cybox.mitre.org/cybox-2'

    id_ = fields.IdField("id", postset_hook=_cache_object)
    idref = fields.IdrefField("idref")
    has_changed = fields.TypedField("has_changed")
    state = VocabField("State")
    description = fields.TypedField("Description", StructuredText)
    properties = fields.TypedField("Properties", ObjectProperties, factory=ObjectPropertiesFactory, postset_hook=_modify_properties_parent)
    domain_specific_object_properties = fields.TypedField("Domain_Specific_Object_Properties", type_="cybox.core.object.DomainSpecificObjectProperties", factory=ExternalTypeFactory)
    location = fields.TypedField("Location", Location, factory=LocationFactory)
    related_objects = fields.TypedField("Related_Objects", type_="cybox.core.object.RelatedObjects")
    defined_effect = fields.TypedField("Defined_Effect", "cybox.core.effect.DefinedEffect", factory=DefinedEffectFactory)
    discovery_method = fields.TypedField("Discovery_Method", MeasureSource)

    def __init__(self, properties=None, id_=None, idref=None):
        super(Object, self).__init__()

        if properties:
            prefix = str(properties.__class__.__name__)
        else:
            prefix = "Object"

        self.id_ = id_ or idgen.create_id(prefix=prefix)
        self.idref = idref
        self.properties = properties
        self.related_objects = RelatedObjects()

    def __str__(self):
        if self.id_ is not None:
            return self.id_
        elif self.idref is not None:
            return self.idref
        else:
            return super(Object, self).__repr__()

    def add_related(self, related, relationship, inline=True):
        if not isinstance(related, ObjectProperties):
            raise ValueError("Must be a ObjectProperties")
        r = RelatedObject(related, relationship=relationship, inline=inline)
        self.related_objects.append(r)


class RelatedObject(Object):
    _binding = core_binding
    _binding_class = _binding.RelatedObjectType

    relationship = VocabField("Relationship", Relationship)

    def __init__(self, *args, **kwargs):
        relationship = kwargs.pop('relationship', None)
        self._inline = kwargs.pop('inline', True)

        super(RelatedObject, self).__init__(*args, **kwargs)
        self.relationship = relationship

        if not self._inline and self.properties:
            self.idref = self.properties.parent.id_
            self.properties = None

    def __str__(self):
        return "Related: " + super(RelatedObject, self).__str__()

    #TODO: make this a property somehow
    def get_properties(self):
        if self.properties:
            return self.properties
        elif self.idref:
            return cybox.utils.cache_get(self.idref).properties
        else:
            return None

    def to_obj(self, ns_info=None):
        relobj_obj = super(RelatedObject, self).to_obj(ns_info=ns_info)

        if not self._inline:
            relobj_obj.idref = self.idref

        if self.relationship:
            relobj_obj.Relationship = self.relationship.to_obj(ns_info=ns_info)

        return relobj_obj

    def to_dict(self):
        if self._inline:
            return super(RelatedObject, self).to_dict()

        relobj_dict = {'idref': self.idref}

        if self.relationship:
            relobj_dict['relationship'] = self.relationship.to_dict()

        return relobj_dict

    @classmethod
    def from_obj(cls, cls_obj):
        if not cls_obj:
            return None

        relobj = super(RelatedObject, cls).from_obj(cls_obj)

        if not relobj.idref and relobj.properties:
            relobj._inline = True

        return relobj

    @classmethod
    def from_dict(cls, cls_dict):
        if not cls_dict:
            return None

        relobj = super(RelatedObject, cls).from_dict(cls_dict)

        if not relobj.idref and relobj.properties:
            relobj._inline = True

        return relobj


class RelatedObjects(entities.EntityList):
    _namespace = "http://cybox.mitre.org/cybox-2"
    _binding = core_binding
    _binding_class = _binding.RelatedObjectsType

    related_object = fields.TypedField("Related_Object", RelatedObject, multiple=True)


class DomainSpecificObjectProperties(entities.Entity):
    """The Cybox DomainSpecificObjectProperties base class."""
    _binding = core_binding
    _binding_class = _binding.DomainSpecificObjectPropertiesType

    # Override in subclass
    _XSI_TYPE = None
    _XSI_NS = None

    def to_obj(self, ns_info=None):
        obj = super(DomainSpecificObjectProperties, self).to_obj(ns_info=ns_info)
        obj.xsi_type = "%s:%s" % (self._XSI_NS, self._XSI_TYPE)

    def to_dict(self):
        d = super(DomainSpecificObjectProperties, self).to_dict()

        if self._XSI_TYPE:
            d['xsi:type'] = self._XSI_TYPE

        return d
