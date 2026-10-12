"""Metadata-backed conservative bound for the pinned Windows Ollama BPE path.

This is an upper bound, never reported usage. The byte alphabet and every
merge product are checked in the deployed GGUF, excluding unknown-piece fallback.
"""
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping
import hashlib
import struct
from ..values import FrozenRecord, fingerprint
from ..contracts import PromptBound, PhysicalIdentity
from ..profile import GENERATION_DIGEST, EMBEDDING_DIGEST

class UnsupportedTokenBound(ValueError):
    pass

SOURCE_PINS = {
    "ollama": "v0.32.15",
    "ollama_tree": "b7871fc0d1d82fe109536efa3e0e8e411c766c75",
    "qwen35_renderer": "7d8d9fbe9e6e2d96d23cde3ea21ffb858f817c21",
    "renderer_registry": "93d3b0eabfb965548e84eb537dccbd09885e1ce0",
    "llama_cpp": "b10488",
    "llama_vocab": "ff926ceecd177633834cca4fbd296eb013317ea1",
    "llama_unicode": "b02ecdc930facad5d93ee69bee20c6dce6f77444",
}

@dataclass(frozen=True, slots=True)
class TokenBoundCertificate(FrozenRecord):
    identity: PhysicalIdentity
    template: str
    tokenizer_metadata: Mapping
    bound_method: str
    proof_assumptions: tuple[str,...]
    source_pins: Mapping
    @property
    def fingerprint(self):
        return fingerprint(self)

def build_token_bound_certificate(identity, template, tokenizer_metadata):
    m=dict(tokenizer_metadata)
    if (identity.model_name!="qwen3.5:4b" or identity.model_digest!=GENERATION_DIGEST
        or identity.embedding_name!="qwen3-embedding:0.6b"
        or identity.embedding_digest!=EMBEDDING_DIGEST
        or identity.embedding_dimension!=1024 or identity.backend_version!="0.32.15"):
        raise UnsupportedTokenBound("unsupported physical identity")
    if template!="{{ .Prompt }}":
        raise UnsupportedTokenBound("unsupported template")
    required={"tokenizer.ggml.model":"gpt2","tokenizer.ggml.pre":"qwen35",
              "renderer":"qwen3.5","byte_alphabet_complete":True,
              "all_merge_products_in_vocab":True}
    if any(m.get(k)!=v for k,v in required.items()):
        raise UnsupportedTokenBound("unsupported tokenizer/renderer or failed vocabulary proof")
    if m.get("tokenizer.ggml.escape_whitespaces",False) is not False:
        raise UnsupportedTokenBound("whitespace expansion unsupported")
    for key in ("metadata_sha256","model_blob_sha256"):
        value=m.get(key)
        if not isinstance(value,str) or len(value)!=64 or any(c not in "0123456789abcdef" for c in value):
            raise UnsupportedTokenBound("missing metadata/blob identity")
    return TokenBoundCertificate(identity,template,m,"RENDERED_UTF8_BYTES_PLUS_TWO",
        ("Only one system then one user message; no images, tools or history",
         "Pinned native qwen3.5 renderer, thinking disabled; no leading BOS",
         "Qwen35 regex partitions original Unicode without expanding it",
         "GPT2 maps each original byte to one initial vocabulary symbol",
         "Every BPE merge product exists in vocabulary: fallback unreachable",
         "Special tokens consume at least one input byte; at most one BOS and EOS",
         "Bound is conservative and separate from backend-reported token usage"),
        SOURCE_PINS)

def render_pinned_messages(prompt):
    if tuple(m.role for m in prompt.messages)!=("system","user"):
        raise UnsupportedTokenBound("only frozen system/user framing is certified")
    # Go TrimSpace only removes edge bytes. Retaining Python-only differences
    # cannot increase the actual prompt beyond the untrimmed form.
    return "".join("<|im_start|>"+m.role+"\n"+m.content+"<|im_end|>\n"
                   for m in prompt.messages)+"<|im_start|>assistant\n<think>\n\n</think>\n\n"

class PinnedTokenBounds:
    def __init__(self,certificate):
        self.certificate=certificate
    @classmethod
    def from_certificate(cls,certificate):
        rebuilt=build_token_bound_certificate(certificate.identity,certificate.template,
                                              certificate.tokenizer_metadata)
        if rebuilt!=certificate:
            raise UnsupportedTokenBound("certificate contents changed")
        return cls(certificate)
    def bound(self,prompt):
        rendered=render_pinned_messages(prompt)
        return PromptBound(len(rendered.encode("utf-8"))+2,self.certificate.fingerprint)

class _MetadataReader:
    def __init__(self,stream):
        self.stream=stream;self.size=0;self.digest=hashlib.sha256()
    def read(self,n):
        if n<0 or self.size+n>32*1024*1024:
            raise UnsupportedTokenBound("GGUF metadata size limit")
        value=self.stream.read(n)
        if len(value)!=n:raise UnsupportedTokenBound("truncated GGUF metadata")
        self.size+=n;self.digest.update(value);return value
    def scalar(self,fmt):
        return struct.unpack("<"+fmt,self.read(struct.calcsize("<"+fmt)))[0]
    def string(self):
        n=self.scalar("Q")
        if n>8*1024*1024:raise UnsupportedTokenBound("GGUF string size limit")
        try:return self.read(n).decode("utf-8")
        except UnicodeError as exc:raise UnsupportedTokenBound("GGUF Unicode") from exc
    def value(self,kind,collect=True):
        formats={0:"B",1:"b",2:"H",3:"h",4:"I",5:"i",6:"f",7:"?",10:"Q",11:"q",12:"d"}
        if kind in formats:return self.scalar(formats[kind])
        if kind==8:return self.string()
        if kind==9:
            item_kind=self.scalar("I");count=self.scalar("Q")
            if count>1000000 or item_kind==9:raise UnsupportedTokenBound("GGUF array limit")
            if not collect and item_kind in formats:
                self.read(struct.calcsize("<"+formats[item_kind])*count);return None
            result=[] if collect else None
            for _ in range(count):
                value=self.value(item_kind,collect)
                if collect:result.append(value)
            return result
        raise UnsupportedTokenBound("unknown GGUF metadata kind")

def read_gguf_tokenizer_metadata(path):
    path=Path(path)
    with path.open("rb") as stream:
        r=_MetadataReader(stream)
        if r.read(4)!=b"GGUF" or r.scalar("I")!=3:
            raise UnsupportedTokenBound("requires GGUF version 3")
        tensors=r.scalar("Q");entries=r.scalar("Q")
        if entries>4096:raise UnsupportedTokenBound("GGUF entry limit")
        metadata={}
        for _ in range(entries):
            key=r.string();kind=r.scalar("I")
            if key in metadata:raise UnsupportedTokenBound("duplicate metadata key")
            collect=key.startswith("tokenizer.ggml.")
            value=r.value(kind,collect)
            if collect:metadata[key]=value
        raw_hash=r.digest.hexdigest();size=r.size
    tokens=metadata.pop("tokenizer.ggml.tokens",None)
    merges=metadata.pop("tokenizer.ggml.merges",None)
    if (not isinstance(tokens,list) or not isinstance(merges,list)
        or any(not isinstance(t,str) for t in tokens+merges)):
        raise UnsupportedTokenBound("missing BPE vocabulary/merges")
    vocab=set(tokens)
    byte_chars={chr(b) for b in list(range(33,127))+list(range(161,173))+list(range(174,256))}
    byte_chars.update(chr(256+n) for n in range(256-len(byte_chars)))
    bad_merges=0
    for merge in merges:
        parts=merge.split(" ")
        if len(parts)!=2 or not all(parts) or "".join(parts) not in vocab:bad_merges+=1
    # Token scores/types are irrelevant to count and too large for the certificate.
    metadata.pop("tokenizer.ggml.scores",None);metadata.pop("tokenizer.ggml.token_type",None)
    metadata.update(metadata_sha256=raw_hash,metadata_bytes=size,tensor_count=tensors,
                    token_count=len(tokens),merge_count=len(merges),
                    byte_alphabet_complete=byte_chars<=vocab,
                    all_merge_products_in_vocab=bad_merges==0,
                    missing_merge_products=bad_merges,
                    model_blob_sha256=path.name.removeprefix("sha256-"),
                    blob_identity_basis="Ollama content-addressed FROM reference; metadata independently hashed")
    return metadata
