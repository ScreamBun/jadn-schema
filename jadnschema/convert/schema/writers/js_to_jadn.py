import jadn
import json
from jadn.definitions import TypeName
from typing import Union
from ..enums import CommentLevels
from ..helpers import register_writer
from ....schema import Schema

DEBUG = False
D = [(f'${n}' if DEBUG else '') for n in range(10)]

jss: dict = {}
jssx: dict = {}

def typedefname(jsdef: str, type_from: str) -> str:
    """
    Infer type name from a JSON Schema definition
    """
    prefix = ''
    if type_from == '$Root':
        prefix = type_from
    else: prefix =('#/'+type_from+'/')
    assert isinstance(jsdef, str), f'Not a type definition name: {jsdef}'
    if jss[type_from].get(jsdef, ''):
        if d := jss[type_from].get(jsdef, ''):
            if ':' in jsdef:  # qualified definition name
                colon_separated_name = maketypename('', jsdef.split(':', maxsplit=1)[1], type_from) + D[1]
                return colon_separated_name
            if d.get('$ref', ''):  # reference name 
                ref = str(d.get('$ref', ''))
                ref_prefixed_name = ref.removeprefix(prefix) + D[2]  
                return ref_prefixed_name
        return jsdef
    else:
        exact_name = jsdef.removeprefix(prefix) + D[0]     # Exact type name or none
        return exact_name

def typerefname(jsref: dict, type_from: str ) -> str:
    """
    Infer a type name from a JSON Schema property reference
    """
    if type_from == '':
        return ''
    if (t := jsref.get('type', '')) in ('string', 'integer', 'number', 'boolean'):
        return t.capitalize() + D[4]    # Built-in type
    if ref := jsref.get('$ref', ''):
        td = str(jssx.get(ref, ref))
        prefix =('#/'+type_from+'/')
        if td.startswith(prefix):  # Exact type name
            return td.removeprefix(prefix) + D[5] # make sure the D value does not need to change based on the prefix passed
        if ':' in td:
            return maketypename('', td.split(':', maxsplit=1)[1], type_from) + D[6]  # Extract type name from $id
        if (type_from != '') & (type_from != '$Root'): 
            if td2 := jss[type_from].get(td, {}):
                return typerefname(td2, type_from) + D[7]      # make sure the D value does not need to change based on the prefix passed  
    return ''


def singular(name: str) -> str:  # examine for jadn2.0
    """
    Guess a singular type name for the anonymous items in a plural ArrayOf type
    """
    if name.endswith('ies'):
        return name[:-3] + 'y'
    elif name.endswith('es'):
        n = -2 if name[-4:-3] == 's' else -1
        return name[:n]
    elif name.endswith('s'):
        return name[:-1]
    return name + '-item'


def maketypename(tn: str, name: str, type_from: str) -> str:
    """
    Convert a type and property name to type name
    """
    tn = typedefname(tn, type_from)
    name = f'{tn}${name}' if tn else name.capitalize()
    return name + '1' if jadn.definitions.is_builtin(name) else name # team discussion leads towards this behavior being in error: check back after spec discussion


def scandef(tn: str, tv: dict, nt: list, type_from: str):
    """
    Process nested type definitions, add to list nt
    """

    if not (td := define_jadn_type(tn, tv, type_from)):
        return
    
    nt.append(td)
    if tv.get('type', '') == 'object':
        for k, v in tv.get('properties', {}).items():
            if v.get('$ref', '') or v.get('type', '') in ('string', 'number', 'integer', 'boolean'):     # Not nested
                pass
            elif v.get('type', '') == 'array':
                scandef(maketypename('', k, type_from), v, nt, type_from)
                scandef(singular(maketypename('', k, type_from)), v['items'], nt, type_from)  # TODO: primitive with options or none
            elif v.get('anyOf', '') or v.get('allOf', ''):
                scandef(maketypename(tn, k, type_from), v, nt, type_from)
            elif typerefname(v, type_from):
                print('  nested property type:', f'{td[TypeName]}${k}', v)

        if not tn:
            print(f'  nested type: "{tv.get("title", "")}"')
    elif (tc := tv.get('anyOf', '')) or (tc := tv.get('allOf', '')):
        for n, v in enumerate(tc, start=1):
            scandef(maketypename(tn, n, type_from), v, nt)
    pass


def define_jadn_type(tn: str, tv: dict, type_from: str) -> list:
    topts = []
    tdesc = tv.get('description', '')
    fields = []
    if (jstype := tv.get('type', '')) == 'object':
        coretype = 'Record'
        req = tv.get('required', [])
        for n, (k, v) in enumerate(tv.get('properties', {}).items(), start=1):
            fopts = ['[0'] if k not in req else []
            fdesc = v.get('description', '')

            if v.get('type', '') == 'array':
                if jss.get(type_from, ''):
                    ftype = maketypename('', k, type_from)
                    idesc = jss[type_from].get(jssx.get(v['items'].get('$ref', ''), ''), {}).get('description', '')
                    fdesc = fdesc if fdesc else v['items'].get('description', idesc)

            elif v.get('type', '') == 'object':
                ftype = tn

            elif t := jssx.get(v.get('$ref', ''), ''):
                if jss.get(type_from):
                    rt = jss[type_from][t].get('$ref', '')
                    ftype = typedefname((rt if rt else t), type_from)
                    ft = jss[type_from][t]
                    fdesc = ft.get('description', '')

            elif v.get('anyOf', '') or v.get('allOf', ''):
                ftype = maketypename(tn, k, type_from)

            else:
                ftype = typerefname(v, type_from)
            fdef = [n, k, ftype, fopts, fdesc]
            if not ftype:
                raise ValueError(f'  empty field type {tn}${k}')
            fields.append(fdef)
    elif (td := tv.get('anyOf', '')) or (td := tv.get('allOf', '')):
        coretype = 'Choice'
        # topts = ['<', '∪'] if 'allOf' in tv else ['<']    # TODO: update Choice in JADN library
        # topts = ['∪'] if 'allOf' in tv else []
        for n, v in enumerate(td, start=1):
            fd = typerefname(v, type_from)
            ftype = fd if fd else maketypename(tn, n, type_from)
            fdef = [n, f'c{n}', ftype, [], '']
            fields.append(fdef)
    elif td := tv.get('enum', ''):
        coretype = 'Enumerated'
        for n, v in enumerate(td, start=1):
            fields.append([n, v, ''])
    elif jstype == 'array':     # TODO: process individual items
        coretype = 'ArrayOf'
        topts = [f'{{{tv["minItems"]}'] if 'minItems' in tv else []
        topts.append(f'}}{tv["maxItems"]}') if 'maxItems' in tv else []
        ref = jss[type_from].get(jssx.get(tv['items'].get('$ref', ''), ''), {})
        tr = typerefname(ref, type_from)
        tr = tr if tr else typerefname(tv['items'], type_from)
        tr = tr if tr else singular(tn)
        topts.append(f'*{tr}')
    elif jstype in ('string', 'integer', 'number', 'boolean'):
        if p := tv.get('pattern', ''):
            topts.append(f'%{p}')
        coretype = jstype.capitalize()
    else:
        return []

    return [typedefname(tn, type_from), coretype, topts, tdesc, fields]


def json_to_jadn_dumps(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs) -> str:
    """
    Create a JADN type from each definition in a Metaschema-generated JSON Schema
    """
    
    global jss
    types_from = []
    if isinstance(schema, str):
        jss = json.loads(schema)
    else:
        jss = schema    
    
    # Only add sections that exist
    if jss.get('properties'): types_from.append('properties')
    if jss.get('definitions'): types_from.append('definitions')
    if jss.get('$defs'): types_from.append('$defs')
    
    global jssx
    types = {}

    for i in range(len(types_from)):
        # Index from $id to definition - broken down for easier debugging
        current_types_section = jss[types_from[i]]
        jssx = {}
        for k, v in current_types_section.items():
            id_key = v.get('$id', k) if isinstance(v, dict) else k
            jssx[id_key] = k
        
        # Index from type name to definition
        section_types = {typedefname(k, types_from[i]): v for k, v in jss[types_from[i]].items()}
        types.update(section_types)

    assert len(types) == len(set(types)), f'Type name collision'

    meta = {'package': jss['$id']}
    meta.update({'comment': jss['$comment']} if '$comment' in jss else {})
    meta.update({'roots': ['$Root']})
    meta.update({'config': {'$MaxString': 1000, '$FieldName': '^[$a-z][-_$A-Za-z0-9]{0,63}$'}})

    nt = []     # Walk nested type definition tree to build type list
    
    for i in range(len(types_from)):
        for tn, tv in jss[types_from[i]].items():
            scandef(tn, tv, nt, types_from[i])



    #scandef('$Root', jss, nt, '$Root')
    #for i in range(len(types_from)):
     #   for tn, tv in jss[types_from[i]].items():
      #      scandef(tn, tv, nt, types_from[i])

    ntypes = []     # Prune identical type definitions
    for t in nt:
        if t not in ntypes:     # O(n^2) runtime because type definitions aren't hashable
            ntypes.append(t)    # Convert to immutable types if it becomes an issue

    """
    # schema view for debug in terminal
    print("returning meta + types")
    print(meta)
    print('---- ----- ---- ---- ----- ---- --- ---- --- -')
    print(ntypes)
    """
    return {'meta': meta, 'types': ntypes}

    # print('\n'.join([f'{k:>15}: {v}' for k, v in jadn.analyze(jadn.check(schema)).items()]))


def json_to_jadn_dump(schema: Union[str, dict, Schema], comm: CommentLevels = CommentLevels.ALL, **kwargs) -> None:
    return None
    # with open(fname, 'w') as f:
    #     if source:
    #         f.write(f'\' Generated from {source}, {datetime.ctime(datetime.now())}"\n\n')
    #     f.write(json_to_jadn_dumps(schema, **kwargs) + '\n')