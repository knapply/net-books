"""One module per animation scene. Each module defines BUILDERS = {id: builder}; discover() collects them all, so
adding a scene never touches a shared file. A builder returns (scene, still_svg) like the ones in tools/make_anim.py.
Scene modules import make_anim lazily, inside the builder, to reuse encode, filmstrip, load and the palette."""
import importlib
import pkgutil


def discover():
    out = {}
    for m in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        out.update(importlib.import_module(f"{__name__}.{m.name}").BUILDERS)
    return out
