"""A005 search and A013 target-free expansion, with one enclosing run ledger."""
from contextvars import ContextVar
from dataclasses import replace
import time
import uuid
from ..contracts import AgentRequest,SetupMetrics
from ..control import RunControl
from ..values import EvidenceKind,canonical_bytes,fingerprint
from ..semantics import EvidenceRecord,RetrievalHit,RetrievalBatch,RelationBatch,Deficit
from ..budgets import Resource,IntegrityStop
from ..profile import EMBEDDING_DIGEST
from flywire_asca.contracts.memory import MemoryRecord,AssociationEdge
from flywire_asca.contracts.enums import MemoryKind,RelationType
from flywire_asca.embedding.contracts import (EmbeddingDescriptor,EmbeddingResponse,normalize_embedding_values,EmbeddingInputKind)
from flywire_asca.embedding.ollama import QUERY_INSTRUCTION
from flywire_asca.vector_memory.models import VectorMemoryDocument,VectorMemoryQuery
from flywire_asca.vector_memory.index import ExactVectorMemoryIndex
from flywire_asca.relational_activation.index import TargetFreeRelationIndex
from flywire_asca.relational_activation.models import ExpansionRequest

class _EmbeddingBridge:
    def __init__(self,port):
        self.port=port;self.control=ContextVar("a015_embedding_owner",default=None)
        self.calls=[];self.setup_control=RunControl.create(AgentRequest("Configured index setup"))
    def inspect(self):
        return EmbeddingDescriptor("configured","pinned","qwen3-embedding:0.6b",EMBEDDING_DIGEST,
                                   "qwen3",None,"0.6B",None,32768,1024,("embedding",))
    def embed(self,request):
        control=self.control.get() or self.setup_control
        control.check_dispatch()
        texts=request.texts
        if request.input_kind is EmbeddingInputKind.QUERY:texts=tuple(QUERY_INSTRUCTION+t for t in texts)
        port=self.port.for_control(control) if hasattr(self.port,"for_control") else self.port
        if request.input_kind is EmbeddingInputKind.QUERY:
            control.ledger.record("query_embedding_calls")
            control.ledger.record("query_embedding_inputs",len(texts))
        result=port.embed(texts,deadline=min(control.ledger.deadline,control.clock.now()+120),
                         cancellation=control.cancellation)
        if result.model_name!="qwen3-embedding:0.6b" or result.model_digest!=EMBEDDING_DIGEST or result.dimension!=1024:
            raise IntegrityStop(message="embedding identity mismatch")
        if len(result.vectors)!=len(texts):raise IntegrityStop(message="embedding count mismatch")
        vectors=tuple(normalize_embedding_values(v,expected_dimension=1024) for v in result.vectors)
        self.calls.append({"run_id":control.run_id,"request_id":request.request_id,"kind":request.input_kind.value,
                           "inputs":len(texts),"prompt_tokens":result.prompt_tokens,"timings":dict(result.timings),
                           "model_name":result.model_name,"model_digest":result.model_digest,"dimension":result.dimension})
        if request.input_kind is EmbeddingInputKind.QUERY and result.prompt_tokens is not None:
            control.ledger.record("embedding_prompt_tokens",result.prompt_tokens)
        return EmbeddingResponse(request.request_id,result.model_name,result.model_digest,vectors,len(texts),
                                 result.prompt_tokens,result.timings.get("total_duration_ns"),result.timings.get("load_duration_ns"))

class KnowledgeAdapter:
    def __init__(self,configuration,embedding_port):
        self.configuration=configuration;self.snapshot=configuration.knowledge
        self.bridge=_EmbeddingBridge(embedding_port);self.cache={};self._ready=False
        self.evidence={};self.documents={};self.relation_records={}
    def setup(self):
        if self._ready:return self.setup_metrics
        started=time.monotonic();cfg=self.configuration;sid=self.snapshot.snapshot_id
        memory_docs=[];catalog_docs=[]
        def add(identifier,kind,payload,entity_ids,text,index):
            memory=MemoryRecord(identifier,MemoryKind.PROCEDURAL if kind is EvidenceKind.CATALOG_ENTRY else MemoryKind.SEMANTIC,
                                identifier,.9,(identifier,))
            self.evidence[identifier]=EvidenceRecord(identifier,kind,identifier,sid,payload)
            entity_kinds={e["id"]:e["kind"] for e in self.snapshot.entities}
            tags=(payload["task"],) if kind is EvidenceKind.CATALOG_ENTRY else tuple(
                sorted({"kind:"+entity_kinds[e] for e in entity_ids}))
            doc=VectorMemoryDocument(memory,text,tuple(entity_ids),tags,())
            self.documents[identifier]=doc;index.append(doc)
        for entity in self.snapshot.entities:
            identifier="entity:"+entity["id"]
            payload={"record_kind":"entity_metadata",**dict(entity)}
            add(identifier,EvidenceKind.STORED_FACT,payload,(entity["id"],),
                entity["name"]+" "+entity["kind"]+" "+entity["id"],memory_docs)
            self.relation_records[entity["id"]]=MemoryRecord(entity["id"],MemoryKind.SEMANTIC,
                                                           identifier,.9,(identifier,))
        for fact in self.snapshot.facts:
            add(fact["id"],EvidenceKind.STORED_FACT,fact,(fact["subject"],),
                canonical_bytes(fact).decode("utf-8"),memory_docs)
        for procedure in cfg.catalog.procedures:
            identifier="catalog:"+procedure["id"]
            add(identifier,EvidenceKind.CATALOG_ENTRY,procedure,(),canonical_bytes(procedure).decode("utf-8"),catalog_docs)
        total=len(memory_docs)+len(catalog_docs)
        if total>cfg.profile.indexed_records:raise ValueError("searchable record limit")
        self.memory_index=ExactVectorMemoryIndex(memory_docs,self.bridge,embedding_profile="a015-qwen-embedding-v1")
        self.catalog_index=ExactVectorMemoryIndex(catalog_docs,self.bridge,embedding_profile="a015-qwen-embedding-v1")
        edges=tuple(AssociationEdge(e["id"],e["source"],e["target"],RelationType(e["relation"].lower()),
                                    e["activation_weight"],e["confidence"],("evidence:"+e["id"],))
                    for e in self.snapshot.edges)
        self.relation_quality={}
        for edge in self.snapshot.edges:
            key=(edge["source"],edge["relation"])
            self.relation_quality[key]=max(self.relation_quality.get(key,0),edge["confidence"])
        self.relation_index=TargetFreeRelationIndex(tuple(self.relation_records.values()),edges)
        self.setup_metrics=SetupMetrics(len(self.bridge.calls),total,time.monotonic()-started,
                                       {"embedding_calls":tuple(self.bridge.calls)})
        self._ready=True;return self.setup_metrics
    def search(self,query,*,control):
        if not self._ready:raise ValueError("knowledge setup required")
        control.check_dispatch()
        key=(control.run_id,self.snapshot.snapshot_id,fingerprint(query))
        if key in self.cache:
            control.ledger.record("retrieval_cache_hits")
            return replace(self.cache[key],actual_queries=0,cache_hits=1,vectors_scored=0)
        if set(query.filters)-{"entity_ids","task","entity_kind"}:raise ValueError("query metadata filters")
        index=self.memory_index if query.index_kind=="memory" else self.catalog_index
        wanted=tuple(query.filters.get("entity_ids",()))
        task=query.filters.get("task");kind=query.filters.get("entity_kind")
        tags=((task,) if task else ())+(("kind:"+kind,) if kind else ())
        local=VectorMemoryQuery(control.run_id+":"+str(uuid.uuid4()),query.text,query.top_k,-1,
                                required_entity_ids=wanted,required_context_tags=tags)
        docs=[d for d in self.documents.values() if (d.memory.memory_id.startswith("catalog:"))==(query.index_kind=="catalog")]
        eligible=sum(index._eligible(d,local) for d in docs)
        trace=control.trace.reserve(2048)
        reservations=control.ledger.reserve_bundle({Resource.RETRIEVAL_QUERIES:1,Resource.VECTORS_SCORED:eligible},
                                    attempt_id=getattr(control,"query_round_id",None))
        token=self.bridge.control.set(control);invoked=False
        try:
            control.check_dispatch();invoked=True
            control.ledger.record("actual_retrieval_queries")
            control.ledger.reconcile(reservations[0],1)
            result=index.search(local)
            control.check_dispatch()
            control.ledger.reconcile(reservations[1],result.scored_vector_count)
            control.ledger.record("vectors_scored",result.scored_vector_count)
            hits=[]
            for hit in result.hits:
                evidence=self.evidence[hit.memory_id]
                if evidence.kind is EvidenceKind.STORED_FACT and evidence.payload.get("record_kind")!="entity_metadata":
                    evidence=replace(evidence,kind=EvidenceKind.VECTOR_HIT)
                hits.append(RetrievalHit(evidence,hit.similarity,result.query_id,hit.entity_ids,
                                         result.embedding_model_name,result.embedding_model_digest,result.embedding_profile))
            batch=RetrievalBatch(tuple(hits),1,0,result.scored_vector_count)
            self.cache[key]=batch;return batch
        finally:
            self.bridge.control.reset(token)
            for r in reservations:
                if r.reservation_id in control.ledger._open:control.ledger.reconcile(r,None if invoked else 0)
            from ..trace import TraceEvent
            control.trace.append(trace,TraceEvent(len(control.trace.freeze()),"retrieval",control.run_id,
                {"query_id":local.query_id,"query_hash":fingerprint(query),"index":query.index_kind,"invoked":invoked}))
    def expand(self,seed_ids,route,*,control):
        if not self._ready:raise ValueError("knowledge setup required")
        if not 1<=len(set(seed_ids))<=2 or len(set(seed_ids))!=len(seed_ids):raise ValueError("one/two unique legitimate seeds")
        if any(seed not in self.relation_records for seed in seed_ids):raise ValueError("unknown relation seed")
        if not route.relational:raise ValueError("positive structural route required")
        control.check_dispatch()
        p=control.profile
        local=ExpansionRequest(tuple(seed_ids),tuple(RelationType(r.lower()) for r in route.relation_types),
                               p.relation_hops,p.relation_visits_per_call,p.relation_edges_per_call,.5)
        reservations=control.ledger.reserve_bundle({Resource.RELATION_INVOCATIONS:1,
                                    Resource.RELATION_VISITS:p.relation_visits_per_call,
                                    Resource.RELATION_EDGES:p.relation_edges_per_call})
        invoked=False
        try:
            control.check_dispatch();invoked=True;control.ledger.record("relation_invocations")
            result=self.relation_index.expand(local)
            control.check_dispatch()
            counts=(1,len(result.visited_memory_ids),result.scanned_edge_count)
            for r,n in zip(reservations,counts):control.ledger.reconcile(r,n)
            control.ledger.record("relation_visit_events",counts[1]);control.ledger.record("relation_scanned_edges",counts[2])
            entity_by_id={e["id"]:e for e in self.snapshot.entities}
            edge_by_id={e["id"]:e for e in self.snapshot.edges}
            paths=[]
            for path in result.paths:
                records=[]
                for node in path.memory_ids:
                    records.append(EvidenceRecord("node:"+node,EvidenceKind.RELATION_PATH,node,self.snapshot.snapshot_id,
                                                  {"record_kind":"node",**dict(entity_by_id[node])}))
                for edge_id in path.edge_ids:
                    edge=edge_by_id[edge_id]
                    records.append(EvidenceRecord("edge:"+edge_id,EvidenceKind.RELATION_PATH,edge_id,self.snapshot.snapshot_id,
                                                  {"record_kind":"edge",**dict(edge)}))
                    records.append(EvidenceRecord("evidence:"+edge_id,EvidenceKind.RELATION_PATH,edge_id,self.snapshot.snapshot_id,
                                                  {"record_kind":"edge_evidence","id":"evidence:"+edge_id,"edge_id":edge_id,
                                                   "confidence":edge["confidence"],"version":edge["version"]}))
                identifier="path:"+fingerprint({"nodes":path.memory_ids,"edges":path.edge_ids,"snapshot":self.snapshot.snapshot_id})
                paths.append(EvidenceRecord(identifier,EvidenceKind.RELATION_PATH,identifier,self.snapshot.snapshot_id,
                    {"record_kind":"path","node_ids":path.memory_ids,"edge_ids":path.edge_ids,
                     "evidence_ids":path.evidence_ids,"records":tuple(records)},tuple(r.evidence_id for r in records)))
            deficits=()
            quality=tuple(self.relation_quality.get((seed,relation)) for seed in seed_ids for relation in route.relation_types)
            if not paths and any(q is not None for q in quality) and all(q is None or q<.5 for q in quality):
                deficits=(Deficit("INSUFFICIENT_CONFIDENCE",explanation="public source relation confidence below declared minimum"),)
            return RelationBatch(tuple(paths),result.visited_memory_ids,result.scanned_edge_count,deficits)
        finally:
            for r in reservations:
                if r.reservation_id in control.ledger._open:control.ledger.reconcile(r,None if invoked else 0)
