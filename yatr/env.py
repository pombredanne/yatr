from jinja2 import Template

from syn.base import Base, Attr, init_hook
from syn.type import Dict
from syn.five import STR

from .context import Context, BUILTIN_CONTEXTS
from .task import Task

#-------------------------------------------------------------------------------

INITIAL_MACROS = {}

#-------------------------------------------------------------------------------
# Env


class Env(Base):
    _attrs = dict(macros = Attr(Dict(STR), init=lambda self: dict()),
                  contexts = Attr(Dict(Context), init=lambda self: dict()),
                  tasks = Attr(Dict(Task), init=lambda self: dict()),
                  secret_values = Attr(Dict(STR), init=lambda self: dict()),
    
                  default_context = Attr(Context))
    _opts = dict(init_validate = True)

    @init_hook
    def _init_populate(self):
        if isinstance(self.macros, list):
            self.update_macros(self.macros)
        self.macros.update(INITIAL_MACROS)
        self.contexts.update(BUILTIN_CONTEXTS)

        if not hasattr(self, 'default_context'):
            self.default_context = self.contexts['null']

    def macro_env(self, **kwargs):
        if isinstance(self.macros, list):
            dct = {} # should only be here on object initialization
        else:
            dct = dict(self.macros)
        dct.update(self.secret_values)
        return dct

    def update_macros(self, macros, **kwargs):
        if isinstance(macros, dict):
            macros = [macros]

        out = {}
        env = self.macro_env(**kwargs)
        for dct in macros:
            for name, template in dct.items():
                value = Template(template).render(env)
                out[name] = value
                env[name] = value
        
        if isinstance(self.macros, list):
            self.macros = dict(env)
        else:
            self.macros.update(out)

    def update_contexts(self, contexts, **kwargs):
        for name, ctx in contexts.items():
            self.contexts[name] = ctx

    def update_tasks(self, tasks, **kwargs):
        for name, task in tasks.items():
            self.tasks[name] = task

    def update(self, env, **kwargs):
        self.secret_values.update(env.secret_values)
        self.update_macros(env.macros, **kwargs)
        self.update_contexts(env.contexts, **kwargs)
        self.update_tasks(env.tasks, **kwargs)

        self.default_context = env.default_context

    def validate(self):
        super(Env, self).validate()
        
        for name, ctx in self.contexts.items():
            ctx.validate()

        for name, task in self.tasks.items():
            task.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Env',)

#-------------------------------------------------------------------------------
