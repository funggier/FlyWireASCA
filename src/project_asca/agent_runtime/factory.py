"""Composition root: concrete legacy/infrastructure adapters appear only here."""
from .ports import RuntimePorts
from .broker import ModelBroker
from .goals import GoalCompiler,TaskSchemaRegistry
from .interpretation import Interpreter
from .context import ContextAcquirer
from .strategy import StrategyResolver
from .recovery import RecoveryEngine
from .controller import AgentRuntime,RunComponents
from .capabilities import CapabilityRegistry,StageAAuthorization
from .adapters.knowledge import KnowledgeAdapter
from .adapters.routing import RoutingAdapter
from .adapters.selection import SelectionAdapter
from .adapters.procedures import ProcedureExecutionAdapter

def build_stage_a_runtime(configuration,ports:RuntimePorts):
    knowledge=KnowledgeAdapter(configuration,ports.embedding)
    setup=knowledge.setup();identity=ports.identity.inspect()
    schemas=TaskSchemaRegistry.from_public(configuration)
    registry=CapabilityRegistry.from_public(configuration)
    def components(control):
        model=ports.model.for_control(control) if hasattr(ports.model,"for_control") else ports.model
        broker=ModelBroker(model,ports.token_bounds,identity)
        routing=RoutingAdapter(broker)
        acquirer=ContextAcquirer(knowledge,knowledge,routing,SelectionAdapter(),broker,snapshot=configuration.knowledge)
        return RunComponents(Interpreter(schemas,broker),GoalCompiler(),schemas,acquirer,
              StrategyResolver(configuration.catalog,registry,broker),RecoveryEngine(),
              ProcedureExecutionAdapter(),registry,StageAAuthorization(),broker)
    return AgentRuntime(configuration,ports,components,setup_metrics=setup,knowledge=knowledge)
