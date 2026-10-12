"""Pinned physical identity probes and unchanged A011 model adapter injection."""
from ..contracts import AgentRequest,PhysicalIdentity,BrokerModelResponse,Usage
from ..control import RunControl
from ..budgets import IntegrityStop
from ..broker import identity_key
from ..profile import GENERATION_DIGEST,EMBEDDING_DIGEST
from .transport import DeadlineJsonTransport,TransportLog
from flywire_asca.model.ollama import OllamaModelAdapter
from flywire_asca.model.contracts import ModelRequest,ModelMessage,ModelRole

def probe_physical_identity(base_url,*,transport=None):
    if transport is None:
        control=RunControl.create(AgentRequest("Configured inference metadata inspection"))
        transport=DeadlineJsonTransport(base_url,control,TransportLog())
    version=transport.request_json("GET","/api/version",None,30)["version"]
    tags=transport.request_json("GET","/api/tags",None,30)["models"]
    by_name={}
    for tag in tags:
        if tag["name"] in by_name:raise ValueError("duplicate model tag")
        by_name[tag["name"]]=tag
    generation=transport.request_json("POST","/api/show",{"model":"qwen3.5:4b"},30)
    embedding=transport.request_json("POST","/api/show",{"model":"qwen3-embedding:0.6b"},30)
    info=embedding["model_info"]
    dim=info[info["general.architecture"]+".embedding_length"]
    g=generation["model_info"]
    renderer=None
    for line in generation.get("modelfile","").splitlines():
        if line.startswith("RENDERER "):renderer=line.split(" ",1)[1].strip()
    return PhysicalIdentity("qwen3.5:4b",by_name["qwen3.5:4b"]["digest"],
        "qwen3-embedding:0.6b",by_name["qwen3-embedding:0.6b"]["digest"],dim,version,
        {"template":generation.get("template"),"renderer":renderer,
         "tokenizer.ggml.model":g.get("tokenizer.ggml.model"),
         "tokenizer.ggml.pre":g.get("tokenizer.ggml.pre"),
         "architecture":g.get("general.architecture"),
         "generation_defaults":generation.get("parameters",""),
         "quantization":generation.get("details",{}).get("quantization_level")})

def _validate_identity(observed,expected):
    if (identity_key(observed)!=identity_key(expected)
        or observed.model_digest!=GENERATION_DIGEST
        or observed.embedding_digest!=EMBEDDING_DIGEST
        or observed.metadata!=expected.metadata):
        raise IntegrityStop(message="fresh physical identity or tokenizer/renderer mismatch")

class PinnedModelPort:
    def __init__(self,base_url,control,identity,*,transport=None):
        self.base_url=base_url;self.control=control;self.identity=identity
        self.log=TransportLog()
        self.transport=transport or DeadlineJsonTransport(base_url,control,self.log)
    def for_control(self,control):
        if isinstance(self.transport,DeadlineJsonTransport):
            transport=DeadlineJsonTransport(self.base_url,control,self.log,
                                           opener=self.transport.opener,gate=self.transport.gate)
        else:transport=self.transport
        bound=PinnedModelPort(self.base_url,control,self.identity,transport=transport)
        bound.log=self.log
        return bound
    def generate(self,request,*,deadline,cancellation):
        self.control.check_dispatch()
        self.transport.override_deadline=deadline
        self.transport.override_cancellation=cancellation
        _validate_identity(probe_physical_identity(self.base_url,transport=self.transport),self.identity)
        adapter=OllamaModelAdapter(self.identity.model_name,
            expected_digest=self.identity.model_digest,
            timeout_seconds=min(120,max(.001,deadline-self.control.clock.now())),
            transport=self.transport)
        legacy=ModelRequest(request.subrequest_id,
            tuple(ModelMessage(ModelRole(m.role),m.content) for m in request.prompt.messages),
            max_output_tokens=request.max_output_tokens,context_limit=request.context_limit,
            temperature=request.temperature,seed=request.seed,thinking=request.thinking)
        response=adapter.generate(legacy)
        self.control.check_dispatch()
        fresh=probe_physical_identity(self.base_url,transport=self.transport)
        _validate_identity(fresh,self.identity)
        if response.model_digest!=self.identity.model_digest:
            raise IntegrityStop(message="legacy response digest mismatch")
        return BrokerModelResponse(response.request_id,fresh,response.content,
            Usage(response.prompt_tokens,response.generated_tokens,
                  response.prompt_tokens is not None and response.generated_tokens is not None),
            {key:getattr(response,key) for key in
             ("total_duration_ns","load_duration_ns","prompt_eval_duration_ns","eval_duration_ns")},
            transport_dispatches=1)

from ..contracts import EmbeddingBatch
from .transport import BoundedWorkerGate
from flywire_asca.embedding.ollama import OllamaEmbeddingAdapter
from flywire_asca.embedding.contracts import EmbeddingRequest,EmbeddingInputKind
import uuid

class PinnedEmbeddingPort:
    def __init__(self,base_url,control,identity,*,transport=None,gate=None,log=None):
        self.base_url=base_url;self.control=control;self.identity=identity
        self.gate=gate or BoundedWorkerGate();self.log=log or TransportLog()
        self.transport=transport or DeadlineJsonTransport(base_url,control,self.log,gate=self.gate)
    def for_control(self,control):
        # Indexes are immutable and shared; each dispatch retains its owning
        # request's single ledger/deadline. The worker limit is shared as well.
        if isinstance(self.transport,DeadlineJsonTransport):
            transport=DeadlineJsonTransport(self.base_url,control,self.log,
                                            opener=self.transport.opener,gate=self.gate)
        else:transport=self.transport
        return PinnedEmbeddingPort(self.base_url,control,self.identity,
                                    transport=transport,gate=self.gate,log=self.log)
    def embed(self,texts,*,deadline,cancellation):
        self.control.check_dispatch()
        self.transport.override_deadline=deadline;self.transport.override_cancellation=cancellation
        _validate_identity(probe_physical_identity(self.base_url,transport=self.transport),self.identity)
        adapter=OllamaEmbeddingAdapter(self.identity.embedding_name,
            expected_digest=self.identity.embedding_digest,expected_dimension=1024,
            timeout_seconds=min(120,max(.001,deadline-self.control.clock.now())),transport=self.transport)
        response=adapter.embed(EmbeddingRequest(self.control.run_id+":"+str(uuid.uuid4()),
                                               EmbeddingInputKind.DOCUMENT,tuple(texts)))
        self.control.check_dispatch()
        _validate_identity(probe_physical_identity(self.base_url,transport=self.transport),self.identity)
        return EmbeddingBatch(response.model_name,response.model_digest,1024,
            tuple(v.values for v in response.vectors),response.prompt_tokens,
            {"total_duration_ns":response.total_duration_ns,"load_duration_ns":response.load_duration_ns})
