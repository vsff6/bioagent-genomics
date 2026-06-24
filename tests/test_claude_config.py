"""
Tests that all required Claude Code agent and skill configuration files exist
and have valid frontmatter.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


REQUIRED_AGENTS = [
    "genomics-file-inspector.md",
    "scrna-qc-specialist.md",
    "single-cell-modeling-specialist.md",
    "atac-qc-specialist.md",
    "wgs-qc-variant-specialist.md",
    "nextflow-pipeline-specialist.md",
    "biology-interpretation-reviewer.md",
]

REQUIRED_SKILLS = [
    "inspect-genomics-files/SKILL.md",
    "scrna-qc-wrapper/SKILL.md",
    "single-cell-modeling-wrapper/SKILL.md",
    "atac-qc-wrapper/SKILL.md",
    "wgs-qc-wrapper/SKILL.md",
    "biological-interpretation-report/SKILL.md",
]


class TestAgentsExist:
    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_file_exists(self, agent_file):
        path = AGENTS_DIR / agent_file
        assert path.exists(), f"Missing agent file: {path}"

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_frontmatter(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---"), f"{agent_file} missing YAML frontmatter (---)"

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_name_field(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert "name:" in content, f"{agent_file} missing 'name:' field"

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_description(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert "description:" in content, f"{agent_file} missing 'description:' field"

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_tools(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert "tools:" in content, f"{agent_file} missing 'tools:' field"

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_role_section(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert "## Role" in content or "# Role" in content, (
            f"{agent_file} missing ## Role section"
        )

    @pytest.mark.parametrize("agent_file", REQUIRED_AGENTS)
    def test_agent_has_must_not_section(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8")
        assert "must not" in content.lower() or "never" in content.lower(), (
            f"{agent_file} missing safety constraints (must not / never)"
        )


class TestSkillsExist:
    @pytest.mark.parametrize("skill_path", REQUIRED_SKILLS)
    def test_skill_file_exists(self, skill_path):
        path = SKILLS_DIR / skill_path
        assert path.exists(), f"Missing skill file: {path}"

    @pytest.mark.parametrize("skill_path", REQUIRED_SKILLS)
    def test_skill_has_purpose(self, skill_path):
        path = SKILLS_DIR / skill_path
        content = path.read_text(encoding="utf-8")
        assert "## Purpose" in content or "# Skill:" in content, (
            f"{skill_path} missing ## Purpose section"
        )

    @pytest.mark.parametrize("skill_path", REQUIRED_SKILLS)
    def test_skill_has_workflow(self, skill_path):
        path = SKILLS_DIR / skill_path
        content = path.read_text(encoding="utf-8")
        assert "## Workflow" in content or "workflow" in content.lower(), (
            f"{skill_path} missing workflow section"
        )

    @pytest.mark.parametrize("skill_path", REQUIRED_SKILLS)
    def test_skill_has_outputs(self, skill_path):
        path = SKILLS_DIR / skill_path
        content = path.read_text(encoding="utf-8")
        assert "output" in content.lower(), (
            f"{skill_path} missing outputs section"
        )


class TestBiologicalEnforcement:
    """Verify biological reasoning is enforced in agent and skill files."""

    @pytest.mark.parametrize("agent_file", [
        "scrna-qc-specialist.md",
        "atac-qc-specialist.md",
        "wgs-qc-variant-specialist.md",
        "biology-interpretation-reviewer.md",
    ])
    def test_agent_mentions_biology(self, agent_file):
        path = AGENTS_DIR / agent_file
        content = path.read_text(encoding="utf-8").lower()
        bio_terms = ["biological", "artifact", "tissue", "cell type"]
        assert any(t in content for t in bio_terms), (
            f"{agent_file} should mention biological reasoning"
        )

    def test_biology_reviewer_has_artifact_table(self):
        path = AGENTS_DIR / "biology-interpretation-reviewer.md"
        content = path.read_text(encoding="utf-8")
        assert "Possible Technical Explanation" in content
        assert "Possible Biological Explanation" in content
        assert "Confidence" in content

    def test_wgs_agent_no_clinical_claims(self):
        path = AGENTS_DIR / "wgs-qc-variant-specialist.md"
        content = path.read_text(encoding="utf-8").lower()
        assert "clinical" in content  # Must address clinical topic
        assert "never" in content or "must not" in content  # Must forbid it

    def test_scrna_skill_has_official_tool_preference(self):
        path = SKILLS_DIR / "scrna-qc-wrapper/SKILL.md"
        content = path.read_text(encoding="utf-8")
        assert "single-cell-rna-qc@life-sciences" in content

    def test_atac_skill_has_official_tool_preference(self):

        path = SKILLS_DIR / "atac-qc-wrapper/SKILL.md"
        content = path.read_text(encoding="utf-8")
        assert "nextflow-development@life-sciences" in content

    def test_wgs_skill_has_official_tool_preference(self):
        path = SKILLS_DIR / "wgs-qc-wrapper/SKILL.md"
        content = path.read_text(encoding="utf-8")
        assert "nextflow-development@life-sciences" in content


class TestCLAUDEmd:
    def test_claude_md_exists(self):
        assert (REPO_ROOT / "CLAUDE.md").exists()

    def test_claude_md_has_guardrails(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        required = [
            "Never load large genomics files",
            "clinical",
            "biological reasoning",
            "Reproducibility",
        ]
        for phrase in required:
            assert phrase.lower() in content.lower(), f"CLAUDE.md missing: {phrase}"

    def test_claude_md_has_agent_delegation(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "genomics-file-inspector" in content
        assert "scrna-qc-specialist" in content
        assert "biology-interpretation-reviewer" in content


class TestScRNAPositioning:
    """
    Verify that the official single-cell-rna-qc@life-sciences skill is the documented
    primary scRNA QC path and that the local tool is clearly framed as fallback-only.
    """

    def test_scrna_agent_prefers_official_skill(self):
        """Agent must check official skill first and stop if available."""
        content = (AGENTS_DIR / "scrna-qc-specialist.md").read_text(encoding="utf-8")
        assert "single-cell-rna-qc@life-sciences" in content, (
            "scrna-qc-specialist.md must reference single-cell-rna-qc@life-sciences"
        )

    def test_scrna_agent_has_stop_at_official_skill(self):
        """Agent must explicitly stop and use official skill before running local tool."""
        content = (AGENTS_DIR / "scrna-qc-specialist.md").read_text(encoding="utf-8")
        # Must have a hard stop: use official when available, only fall back otherwise
        assert "fallback" in content.lower(), (
            "scrna-qc-specialist.md must label local tool as fallback"
        )
        assert "unavailable" in content.lower() or "not available" in content.lower(), (
            "scrna-qc-specialist.md must describe when fallback applies"
        )

    def test_scrna_agent_must_not_duplicate_official_skill(self):
        """Agent must say not to duplicate official QC."""
        content = (AGENTS_DIR / "scrna-qc-specialist.md").read_text(encoding="utf-8")
        lower = content.lower()
        assert "do not" in lower or "must not" in lower or "never" in lower, (
            "scrna-qc-specialist.md must contain prohibition language"
        )
        assert "duplicate" in lower or "not run" in lower or "do not run" in lower or "do not use" in lower, (
            "scrna-qc-specialist.md must prohibit duplicating official QC"
        )

    def test_scrna_skill_official_is_primary(self):
        """SKILL.md must unambiguously state official skill is primary."""
        content = (SKILLS_DIR / "scrna-qc-wrapper/SKILL.md").read_text(encoding="utf-8")
        assert "single-cell-rna-qc@life-sciences" in content
        lower = content.lower()
        assert "primary" in lower or "preferred" in lower or "default" in lower, (
            "scrna-qc-wrapper/SKILL.md must say official skill is primary/preferred/default"
        )

    def test_scrna_skill_labels_local_as_fallback(self):
        """SKILL.md must explicitly call local tool a fallback."""
        content = (SKILLS_DIR / "scrna-qc-wrapper/SKILL.md").read_text(encoding="utf-8")
        assert "fallback" in content.lower(), (
            "scrna-qc-wrapper/SKILL.md must label tools/scrna_qc_local.py as fallback"
        )

    def test_scrna_skill_says_do_not_duplicate(self):
        """SKILL.md must prohibit duplicating official QC."""
        content = (SKILLS_DIR / "scrna-qc-wrapper/SKILL.md").read_text(encoding="utf-8")
        assert "do not" in content.lower() or "do NOT" in content, (
            "scrna-qc-wrapper/SKILL.md must contain 'do not' prohibition"
        )
        assert "duplicate" in content.lower() or "unnecessarily" in content.lower(), (
            "scrna-qc-wrapper/SKILL.md must prohibit unnecessary duplication"
        )

    def test_scrna_skill_biological_interpretation_after_official(self):
        """SKILL.md must describe biological interpretation applied after official skill output."""
        content = (SKILLS_DIR / "scrna-qc-wrapper/SKILL.md").read_text(encoding="utf-8")
        assert "biological interpretation" in content.lower() or "artifact" in content.lower(), (
            "scrna-qc-wrapper/SKILL.md must describe biological interpretation step"
        )

    def test_readme_does_not_present_local_scrna_as_primary(self):
        """README must not present scrna_qc_local.py as the primary scRNA QC path."""
        content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        assert "single-cell-rna-qc@life-sciences" in content, (
            "README must reference single-cell-rna-qc@life-sciences as the primary path"
        )
        lower = content.lower()
        # Must say the official skill is preferred/primary
        assert "preferred" in lower or "primary" in lower or "default" in lower, (
            "README must say official skill is preferred/primary/default for scRNA QC"
        )
        # Must label local tool as fallback
        assert "fallback" in lower, (
            "README must label scrna_qc_local.py as fallback"
        )

    def test_readme_local_scrna_listed_as_fallback_not_primary(self):
        """README implementation status must not list local scRNA QC as fully implemented."""
        content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        # The phrase 'fallback-only' should appear in the local scRNA QC bullet
        assert "fallback-only" in content or "fallback only" in content.lower(), (
            "README must use 'fallback-only' or 'fallback only' for local scRNA QC"
        )

    def test_implementation_status_scrna_primary_is_official(self):
        """IMPLEMENTATION_STATUS.md must mark official skill as primary for scRNA QC."""
        content = (REPO_ROOT / "docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")
        assert "single-cell-rna-qc@life-sciences" in content
        lower = content.lower()
        assert "primary" in lower or "official-first" in lower, (
            "IMPLEMENTATION_STATUS.md must say official skill is primary for scRNA QC"
        )

    def test_implementation_status_local_scrna_is_fallback(self):
        """IMPLEMENTATION_STATUS.md must label local scRNA QC as fallback only."""
        content = (REPO_ROOT / "docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")
        assert "fallback" in content.lower(), (
            "IMPLEMENTATION_STATUS.md must label local scRNA QC as fallback"
        )

    def test_implementation_status_mentions_full_production_uses_official(self):
        """IMPLEMENTATION_STATUS.md must state production scRNA QC should use official skill."""
        content = (REPO_ROOT / "docs/IMPLEMENTATION_STATUS.md").read_text(encoding="utf-8")
        assert "production" in content.lower() or "full production" in content.lower(), (
            "IMPLEMENTATION_STATUS.md must mention that full/production scRNA QC uses official skill"
        )
