from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT/".github/workflows/ci.yml"

def test_ci_retains_every_existing_standalone_gate():
    text = CI.read_text(encoding="utf-8")
    commands = (
        "python -m pytest -q",
        "python scripts/audit_architecture_contract.py",
        "python scripts/qualify_repository.py",
        "python scripts/run_familiarity_benchmark_a003.py --qualify",
        "python scripts/qualify_procedural_memory_a008.py",
        "python scripts/qualify_integrated_loop_a009.py",
        "python scripts/qualify_baseline_comparison_a010.py",
        "git diff --check HEAD^ HEAD",
    )
    assert all([line.strip() for line in text.splitlines()].count("run: "+c) == 1 for c in commands)
    assert "fetch-depth: 2" in text and 'python-version: "3.11"' in text

def test_ci_adds_nonfinal_a011_and_uploads_even_on_failure():
    text = CI.read_text(encoding="utf-8")
    name = "Qualify A011 portable system"
    assert text.count("name: "+name) == 1
    assert 'python scripts/qualify_asca_v0x_a011.py --expected-source-sha "$(git rev-parse HEAD)"' in text
    assert '--output-dir "$RUNNER_TEMP/a011-portable-${{ github.run_id }}-${{ github.run_attempt }}"' in text
    assert text.index("Qualify A010") < text.index(name) < text.index("Check whitespace")
    upload = text[text.index("- name: Upload A011 portable qualification pack"):text.index("- name: Check whitespace")]
    assert "if: always()" in upload and "uses: actions/upload-artifact@v4" in upload
    assert "if-no-files-found: error" in upload
    assert "path: ${{ runner.temp }}/a011-portable-${{ github.run_id }}-${{ github.run_attempt }}/" in upload

def test_ci_has_no_physical_model_or_calibration_command():
    text = CI.read_text(encoding="utf-8")
    runs = [line.split("run:",1)[1].strip() for line in text.splitlines() if "run:" in line]
    forbidden = ("_physical.py","qualify_qwen_a004","qualify_vector_memory_a005",
        "qualify_selective_activation_a006","qualify_uncertainty_expansion_a007",
        "ollama","--calibrate","--threshold","--model","--accept-current")
    assert not any(word in command for command in runs for word in forbidden)
