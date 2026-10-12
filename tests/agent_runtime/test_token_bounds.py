import pytest
from .conftest import api

def identity():
    c=api("contracts");p=api("profile")
    return c.PhysicalIdentity("qwen3.5:4b",p.GENERATION_DIGEST,
        "qwen3-embedding:0.6b",p.EMBEDDING_DIGEST,1024,"0.32.15")

def metadata():
    return {"tokenizer.ggml.model":"gpt2","tokenizer.ggml.pre":"qwen35",
            "renderer":"qwen3.5","byte_alphabet_complete":True,
            "all_merge_products_in_vocab":True,"metadata_sha256":"a"*64,
            "model_blob_sha256":"81fb60c7daa80fc1123380b98970b320ae233409f0f71a72ed7b9b0d62f40490"}

def test_bound_is_conservative_rendered_bytes_not_reported_tokens():
    t=api("adapters.token_bounds");c=api("contracts")
    cert=t.build_token_bound_certificate(identity(),"{{ .Prompt }}",metadata())
    bounds=t.PinnedTokenBounds.from_certificate(cert)
    prompt=c.ModelPrompt((c.ModelMessage("system","schema"),c.ModelMessage("user","ไทย")),"x","y")
    rendered=t.render_pinned_messages(prompt)
    assert "<|im_start|>system" in rendered and "<think>\n\n</think>" in rendered
    assert bounds.bound(prompt).upper_tokens==len(rendered.encode("utf-8"))+2
    assert bounds.bound(prompt).certificate_hash==cert.fingerprint

@pytest.mark.parametrize("key,value",[
    ("tokenizer.ggml.model","spm"),("tokenizer.ggml.pre","unrecognized"),
    ("renderer","changed"),("byte_alphabet_complete",False),
    ("all_merge_products_in_vocab",False),
])
def test_uncertifiable_tokenizer_or_template_blocks_physical_gate(key,value):
    t=api("adapters.token_bounds");m=metadata();m[key]=value
    with pytest.raises(t.UnsupportedTokenBound):
        t.build_token_bound_certificate(identity(),"{{ .Prompt }}",m)

def test_template_change_and_assistant_history_are_not_silently_accepted():
    t=api("adapters.token_bounds");c=api("contracts")
    with pytest.raises(t.UnsupportedTokenBound):
        t.build_token_bound_certificate(identity(),"custom template",metadata())
    cert=t.build_token_bound_certificate(identity(),"{{ .Prompt }}",metadata())
    prompt=c.ModelPrompt((c.ModelMessage("assistant","earlier"),),"x","y")
    with pytest.raises(t.UnsupportedTokenBound):t.PinnedTokenBounds.from_certificate(cert).bound(prompt)

def synthetic_gguf(path, *, missing_byte=False, invalid_merge=False):
    import struct
    alphabet=[chr(b) for b in range(33,127)]+[chr(b) for b in range(161,173)]+[chr(b) for b in range(174,256)]
    alphabet += [chr(256+n) for n in range(256-len(alphabet))]
    if missing_byte:alphabet.pop()
    tokens=alphabet+["ab"]
    def string(s):
        b=s.encode("utf-8");return struct.pack("<Q",len(b))+b
    entries=[]
    for k,v in [("tokenizer.ggml.model","gpt2"),("tokenizer.ggml.pre","qwen35")]:
        entries.append(string(k)+struct.pack("<I",8)+string(v))
    for k,items in [("tokenizer.ggml.tokens",tokens),("tokenizer.ggml.merges",["a b" if not invalid_merge else "a z"])]:
        entries.append(string(k)+struct.pack("<IIQ",9,8,len(items))+b"".join(string(i) for i in items))
    data=b"GGUF"+struct.pack("<IQQ",3,0,len(entries))+b"".join(entries)
    path.write_bytes(data+b"UNREAD WEIGHTS")
    return len(data)

def test_gguf_reader_proves_alphabet_and_merges_without_reading_tensors(tmp_path):
    t=api("adapters.token_bounds");path=tmp_path/"sha256-model"
    size=synthetic_gguf(path)
    m=t.read_gguf_tokenizer_metadata(path)
    assert m["byte_alphabet_complete"] is True
    assert m["all_merge_products_in_vocab"] is True
    assert m["metadata_bytes"]==size and m["token_count"]==257

@pytest.mark.parametrize("mode",["missing_byte","invalid_merge"])
def test_gguf_reader_records_failed_proof(tmp_path,mode):
    t=api("adapters.token_bounds");path=tmp_path/"model"
    synthetic_gguf(path,**{mode:True})
    m=t.read_gguf_tokenizer_metadata(path)
    key="byte_alphabet_complete" if mode=="missing_byte" else "all_merge_products_in_vocab"
    assert m[key] is False

def test_truncated_gguf_is_not_a_certificate(tmp_path):
    t=api("adapters.token_bounds");path=tmp_path/"model";path.write_bytes(b"GGUF")
    with pytest.raises(t.UnsupportedTokenBound):t.read_gguf_tokenizer_metadata(path)
