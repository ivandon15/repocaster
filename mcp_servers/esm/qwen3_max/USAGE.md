# repo_source MCP Server User Guide

## 1. Introduction

This MCP server provides access to ESM-based protein modeling tools for structure prediction, sequence design, variant effect prediction, and representation extraction.

**Core capabilities:**
- Predict 3D protein structures from sequences (ESMFold)
- Design sequences for fixed backbones or generate de novo proteins
- Sample or score sequences compatible with a given structure (inverse folding)
- Predict functional effects of amino acid variants
- Extract ESM-2 embeddings from protein sequences

---

## 2. Tool Reference

### `esmfold_structure_prediction`
**Purpose:** Predicts 3D protein structure from amino acid sequence using ESMFold.  
**Input:**  
- `fasta` (string, required): Path to input FASTA file  
- `pdb` (string, required): Path to output PDB directory  
- `model-dir` (string, optional)  
- `num-recycles` (integer, optional)  
- `max-tokens-per-batch` (integer, optional)  
- `cpu-only` (string, optional)  
**Output:** PDB file(s) written to specified directory.

---

### `inverse_folding_sample_sequences`
**Purpose:** Samples sequences compatible with a given backbone using inverse folding (e.g., ESM-IF1).  
**Input:**  
- `chain` (string, optional)  
- `temperature` (number, optional)  
- `outpath` (string, optional)  
- `num-samples` (integer, optional)  
- `multichain-backbone` (string, optional)  
- `singlechain-backbone` (string, optional)  
**Output:** FASTA-formatted sampled sequences written to `outpath`.

---

### `inverse_folding_score_likelihoods`
**Purpose:** Computes per-residue log-likelihood scores for a sequence-structure pair.  
**Input:**  
- `outpath` (string, optional)  
- `chain` (string, optional)  
- `multichain-backbone` (string, optional)  
- `singlechain-backbone` (string, optional)  
**Output:** Per-residue log-likelihood scores saved to `outpath`.

---

### `variant_effect_prediction`
**Purpose:** Predicts functional effects of amino acid variants using ESM-1v or similar models.  
**Input:**  
- `model-location` (string, optional)  
- `sequence` (string, optional)  
- `dms-input` (string, optional)  
- `mutation-col` (string, optional)  
- `dms-output` (string, optional)  
- `offset-idx` (integer, optional)  
- `scoring-strategy` (string, optional)  
- `msa-path` (string, optional)  
**Output:** CSV file with variant predictions at `dms-output`.

---

### `representation_extraction`
**Purpose:** Extracts ESM-2 embeddings or representations from protein sequences.  
**Input:**  
- `include` (string, required): Specify which representations to return  
- `repr_layers` (integer, optional)  
- `toks_per_batch` (integer, optional)  
- `truncation_seq_length` (integer, optional)  
**Output:** Embeddings saved in specified format (e.g., HDF5 or NPZ).

---

## 3. Workflow Examples

### **Workflow 1: Predict structure → Score sequence compatibility**
**Problem:** Evaluate how well a natural sequence fits its predicted structure.  
**Steps:**  
1. **Predict structure**:  
   ```bash
   esmfold_structure_prediction --fasta input.fasta --pdb ./output/
   ```
   *Input:* `input.fasta`  
2. **Score likelihood**:  
   ```bash
   inverse_folding_score_likelihoods \
     --singlechain-backbone ./output/input.pdb \
     --sequence_path input.fasta \
     --outpath scores.json
   ```
   *Input:* Predicted PDB + original FASTA  

---

### **Workflow 2: Fixed-backbone design → Validate with inverse folding**
**Problem:** Redesign a protein sequence for a known structure and assess quality.  
**Steps:**  
1. **Run fixed-backbone design**:  
   ```bash
   fixed_backbone_design pdb_fn=target.pdb task=fixedbb seed=42
   ```
   *Input:* `target.pdb`  
2. **Sample alternative sequences**:  
   ```bash
   inverse_folding_sample_sequences \
     --singlechain-backbone target.pdb \
     --num-samples 10 \
     --outpath designs.fasta
   ```
   *Input:* Same `target.pdb`  
3. **(Optional) Score designed sequence**:  
   Use `inverse_folding_score_likelihoods` on the top-designed sequence.

---

### **Workflow 3: Extract embeddings → Predict variant effects**
**Problem:** Use ESM-2 representations to interpret variant impacts.  
**Steps:**  
1. **Extract embeddings**:  
   ```bash
   representation_extraction \
     --model_location esm2_t33_650M_UR50D \
     --fasta_file wt.fasta \
     --include mean \
     --repr_layers 33 \
     --out_repr_file embeddings.h5
   ```
   *Input:* `wt.fasta`  
2. **Predict variant effects**:  
   ```bash
   variant_effect_prediction \
     --fasta_file wt.fasta \
     --dms-input variants.csv \
     --dms-output predictions.csv \
     --model_location esm1v_t33_650M_UR90S_1
   ```
   *Input:* Wild-type FASTA + variant list (`variants.csv`)