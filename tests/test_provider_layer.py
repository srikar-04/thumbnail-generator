"""Ticket 10 — the provider layer at the CLI-over-disk seam.

Cost ledger, retry/backoff, binding-as-configuration, key hygiene. The test
suite stays on fake providers: real Gemini is exercised only by the operator's
manual milestone-exit run, never here. All assertions are on disk artifacts
(ledger, journal, candidates) or CLI output.
"""

import json
from collections import Counter
from pathlib import Path

from test_order_run import start_order

# the model-call methods `order run` makes (onboarding's analyze_photo calls
# land in an earlier command and a different ledger)
ORDER_RUN_METHODS = {"propose_wordings", "propose_concepts", "generate_background"}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_order_run_writes_a_raw_cost_ledger_with_one_entry_per_model_call(thumb, make_photo):
    order_dir = start_order(thumb, make_photo)

    thumb("order", "run", "srikar", "001")

    entries = read_jsonl(order_dir / "ledger.jsonl")

    # ground truth of what calls were made: the fakes' journal
    journal = read_jsonl(thumb.root / ".thumb" / "provider-calls.jsonl")
    calls_made = Counter(j["method"] for j in journal if j["method"] in ORDER_RUN_METHODS)
    calls_billed = Counter(e["method"] for e in entries)
    assert calls_billed == calls_made, "ledger must have exactly one entry per model call"
    assert calls_billed["generate_background"] == 20  # images dominate the bill

    for entry in entries:
        assert entry["role"] in {"wording", "background", "critique"}
        assert entry["model"]
        assert entry["units"], f"entry {entry} must say what was consumed"
        assert isinstance(entry["cost_usd"], (int, float))

    # raw writes only (no reporting layer) — but the entries must sum
    assert sum(e["cost_usd"] for e in entries) == 0.0  # fakes are free


def test_transient_503s_are_retried_and_the_order_still_completes(thumb, make_photo):
    # The prototype hit frequent 503s on flash-lite; a half-finished Order must
    # never die to one. Script the fake to fail twice, then succeed.
    order_dir = start_order(thumb, make_photo)

    thumb(
        "order", "run", "srikar", "001",
        env={"THUMB_FAKE_503S": "2", "THUMB_RETRY_BASE_SECONDS": "0"},
    )

    assert len(list((order_dir / "candidates").glob("*.png"))) == 20

    # the journal proves the scripted failures really happened and were absorbed
    journal = read_jsonl(thumb.root / ".thumb" / "provider-calls.jsonl")
    transient = [j for j in journal if j["method"] == "transient-503"]
    assert len(transient) == 2, "the two scripted 503s must have been hit (and retried)"


def test_real_binding_is_selected_by_configuration_not_a_code_change(thumb, make_photo):
    # ADR-0002: fake -> real is THUMB_PROVIDERS, never a pipeline edit. With no
    # key available, the gemini binding must be recognized and fail fast at key
    # loading — before any candidate is generated or any network is touched.
    order_dir = start_order(thumb, make_photo)

    result = thumb(
        "order", "run", "srikar", "001", check=False, env={"THUMB_PROVIDERS": "gemini"}
    )

    assert result.returncode != 0
    assert "unknown provider binding" not in result.stderr, (
        "gemini must be a real binding, selectable by configuration"
    )
    assert "GEMINI_API_KEY" in result.stderr, (
        "the operator must be told how to supply the key (env or .env)"
    )
    assert not list((order_dir / "candidates").glob("*.png")), (
        "must fail fast at key loading, before generating anything"
    )


def test_gemini_binding_survives_fence_wrapped_vlm_json(thumb, make_photo):
    # Regression (2026-07-12): the real VLM wrapped its JSON in markdown code
    # fences with trailing prose (despite JSON mode), and `onboard` died with
    # JSONDecodeError. Drive the REAL gemini binding with the SDK shadowed by
    # tests/stubs (PYTHONPATH wins over site-packages) — no network, no key,
    # no credits — replaying that exact response shape.
    stubs = str(Path(__file__).parent / "stubs")
    env = {
        "THUMB_PROVIDERS": "gemini",
        "GEMINI_API_KEY": "stub-key-never-real",
        "PYTHONPATH": stubs,
    }

    shoot = thumb.root / "shoot"
    make_photo(shoot / "portrait.png")
    result = thumb(
        "onboard", "srikar",
        "--niche", "tech-explainer",
        "--face", "on",
        "--brand-color", "#D82C2C",
        "--photos", str(shoot),
        env=env,
    )

    assert "accepted 1" in result.stdout
    pack = thumb.root / "creators" / "srikar" / "asset-pack"
    metadata = json.loads((pack / "photos" / "portrait.json").read_text(encoding="utf-8"))
    assert metadata["lighting"] == "directional", (
        "the fenced payload must be parsed into clean cached metadata"
    )
    assert (pack / "cutouts" / "portrait.png").exists()

    # the real binding billed the call at real prices (not the fake's zeros)
    entries = read_jsonl(thumb.root / ".thumb" / "ledger.jsonl")
    analyze = [e for e in entries if e["method"] == "analyze_photo"]
    assert analyze and analyze[0]["model"] == "gemini-2.5-flash-lite"
    assert analyze[0]["cost_usd"] > 0


def test_the_api_key_never_appears_in_output_or_on_disk(thumb, make_photo):
    # Key hygiene: with the key present in the environment for every command,
    # the whole flow must leave it in no CLI output and no file — metadata,
    # ledger, journal, Contact Sheet, anything.
    sentinel = "hygiene-sentinel-key-8891x"
    env = {"GEMINI_API_KEY": sentinel}

    photos = thumb.root / "shoot"
    make_photo(photos / "face01.png")
    outputs = [
        thumb(
            "onboard", "srikar",
            "--niche", "tech-explainer",
            "--face", "on",
            "--brand-color", "#D82C2C",
            "--photos", str(photos),
            env=env,
        ),
        thumb(
            "order", "new", "srikar",
            "--title", "Loop Engineering",
            "--hook", "Why your loops fail and how to see it coming",
            env=env,
        ),
        thumb("order", "run", "srikar", "001", env=env),
        thumb("order", "sheet", "srikar", "001", env=env),
    ]

    for result in outputs:
        assert sentinel not in result.stdout + result.stderr

    leaks = [
        path
        for path in thumb.root.rglob("*")
        if path.is_file() and sentinel.encode() in path.read_bytes()
    ]
    assert not leaks, f"API key leaked to disk: {leaks}"
