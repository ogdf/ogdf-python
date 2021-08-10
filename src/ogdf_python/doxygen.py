import functools
import os
from collections import defaultdict


# doxygen XML parsing #################################################################################################


def parse_index_xml():
    root = etree.parse(os.path.join(DOXYGEN_XML_DIR, 'index.xml'))
    compounds = defaultdict(dict)
    for compound in root.iter('compound'):
        kind = compound.attrib['kind']
        name = compound.find('name').text.strip()
        if name in compounds[kind]:
            print("duplicate compound", kind, name)
            continue
        compound_data = compounds[kind][name] = {
            "kind": kind,
            "name": name,
            "refid": compound.attrib['refid'],
            "members": defaultdict(dict)
        }

        for member in compound.iter('member'):
            kind = member.attrib['kind']
            name = member.find('name').text.strip()
            refid = member.attrib['refid']
            if refid in compound_data["members"][name]:
                print("duplicate member", kind, name, refid)
                continue
            compound_data["members"][name][refid] = {
                "kind": kind,
                "name": name,
                "refid": refid
            }

    return compounds


def find_all_includes():
    for ctype in ("class", "struct", "namespace"):
        for compound in DOXYGEN_DATA[ctype].values():
            compound_xml = etree.parse(os.path.join(DOXYGEN_XML_DIR, compound["refid"] + '.xml'))
            for location in compound_xml.findall(".//*[@id]/location"):
                parent = location.getparent()
                if parent.get("id") == compound["refid"]:
                    member = compound
                else:
                    name = parent.find("name")
                    if name.text not in compound["members"]:
                        print("got location for unknown object", compound["refid"], parent.get("id"), name.text)
                        continue
                    else:
                        member = compound["members"][name.text][parent.get("id")]
                member["file"] = location.get("declfile", location.get("file"))


# doc strings / help messages##########################################################################################

def pythonize_docstrings(klass, name):
    data = DOXYGEN_DATA["class"][klass.__cpp_name__]  # TODO do the same for namespace members
    url = DOXYGEN_URL % (data["refid"], "")
    try:
        if klass.__doc__:
            klass.__doc__ = "%s\n%s" % (klass.__doc__, url)
        else:
            klass.__doc__ = url
    except AttributeError as e:
        print(klass.__cpp_name__, e)  # TODO remove once we can overwrite the __doc__ of CPPOverload etc.

    for mem, val in klass.__dict__.items():
        if mem not in data["members"]:
            print(klass.__cpp_name__, "has no member", mem)
            continue
        try:
            for override in data["members"][mem].values():
                val.__doc__ += "\n" + DOXYGEN_URL % (data["refid"], override["refid"][len(data["refid"]) + 2:])
        except AttributeError as e:
            print(klass.__cpp_name__, e)  # TODO remove once we can overwrite the __doc__ of CPPOverload etc.
            # import traceback
            # traceback.print_exc()
            # print(val.__doc__)
            pass


# helpful "attribute not found" errors ################################################################################

def find_include(*names):
    if len(names) == 1:
        if isinstance(names[0], str):
            names = names[0].split("::")
        else:
            names = names[0]

    name = names[-1]
    qualname = "::".join(names)
    parentname = "::".join(names[:-1])

    data = DOXYGEN_DATA["class"].get(qualname, None)
    filename = None
    if not data:
        data = DOXYGEN_DATA["struct"].get(qualname, None)
    if not data:
        namespace_data = DOXYGEN_DATA["namespace"].get(parentname, None)
        if namespace_data and name in namespace_data["members"]:
            data = next(iter(namespace_data["members"][name].values()))
            filename = namespace_data["refid"]
    if not data:
        return None

    if "file" in data:
        return data["file"]

    if not filename:
        filename = data["refid"]
    namespace_xml = etree.parse(os.path.join(DOXYGEN_XML_DIR, filename + '.xml'))
    location = namespace_xml.find(".//*[@id='%s']/location" % data["refid"])
    return location.get("declfile", location.get("file"))


def wrap_getattribute(ns):
    getattrib = type(ns).__getattribute__
    if hasattr(getattrib, "__wrapped__"): return

    @functools.wraps(getattrib)
    def helpful_getattribute(ns, name):
        try:
            val = getattrib(ns, name)
            if isinstance(type(val), type(type(ns))):
                wrap_getattribute(val)
            return val
        except AttributeError as e:
            if hasattr(e, "__helpful__"):
                raise e
            msg = e.args[0]
            file = find_include(*ns.__cpp_name__.split("::"), name)
            if file:
                prefix = "include/"
                msg += "\nDid you forget to include file %s? Try running\ncppinclude(\"%s\")" % \
                       (file, file[len(prefix):] if file.startswith(prefix) else file)
            else:
                msg += "\nThe name %s::%s couldn't be found in the docs." % (ns.__cpp_name__, name)
            e.args = (msg, *e.args[1:])
            e.__helpful__ = True
            raise e

    type(ns).__getattribute__ = helpful_getattribute


# __main__ and imported use ###########################################################################################

if "OGDF_DOC_DIR" in os.environ:
    from lxml import etree

    DOXYGEN_XML_DIR = os.path.join(os.environ["OGDF_DOC_DIR"], "xml")
    DOXYGEN_DATA = parse_index_xml()

    if __name__ == "__main__":
        import json, sys

        find_all_includes()
        with open("doxygen.json", "wt") as f:
            json.dump(DOXYGEN_DATA, f)
        sys.exit(0)

else:
    import json

    DOXYGEN_XML_DIR = None

    try:
        with open("doxygen.json", "rt") as f:
            DOXYGEN_DATA = json.load(f)
    except FileNotFoundError:
        import importlib_resources

        with importlib_resources.files("ogdf_python").joinpath("doxygen.json").open("rt") as f:
            DOXYGEN_DATA = json.load(f)

if "OGDF_DOC_URL" in os.environ:
    DOXYGEN_URL = os.environ["OGDF_DOC_URL"]
else:
    DOXYGEN_URL = "https://ogdf.github.io/doc/ogdf/%s.html#%s"

import cppyy

# cppyy.py.add_pythonization(pythonize_docstrings, "ogdf") # TODO needs to be added *before* any classes are loaded
wrap_getattribute(cppyy.gbl.ogdf)
