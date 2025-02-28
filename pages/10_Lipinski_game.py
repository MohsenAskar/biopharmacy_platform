import streamlit as st
import pandas as pd
import rdkit
import py3Dmol
import time
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, AllChem

# -----------------------------
# Caching for Visualization
# -----------------------------
@st.cache_data(show_spinner=False)
def get_2d_image(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        return Draw.MolToImage(mol)
    return None

@st.cache_data(show_spinner=False)
def get_3d_molblock(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        mol_3d = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol_3d, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol_3d)
        return Chem.MolToMolBlock(mol_3d)
    return None

# -----------------------------
# Helper: Attach Functional Group
# -----------------------------
def attach_functional_group(mol, fg_smiles):
    """
    Attaches a functional group to the first available hydrogen on a heavy atom.
    The functional group is expected to have a dummy attachment point [*] (defined as [*:1] in SMILES).
    """
    # Convert the functional group (fg) molecule.
    fg = Chem.MolFromSmiles(fg_smiles)
    if fg is None:
        return None

    # Add explicit hydrogens to the main molecule.
    mol_h = Chem.AddHs(mol)
    
    # Find the first hydrogen atom attached to a heavy atom.
    heavy_idx = None
    hydrogen_idx = None
    for atom in mol_h.GetAtoms():
        if atom.GetAtomicNum() == 1:  # hydrogen
            neighbors = atom.GetNeighbors()
            if neighbors:
                heavy_atom = neighbors[0]
                heavy_idx = heavy_atom.GetIdx()
                hydrogen_idx = atom.GetIdx()
                break

    if hydrogen_idx is None or heavy_idx is None:
        return None

    # Remove the hydrogen atom.
    emol = Chem.EditableMol(mol_h)
    emol.RemoveAtom(hydrogen_idx)
    mol_no_H = emol.GetMol()
    # Adjust heavy atom index if needed (if hydrogen came before heavy atom)
    if hydrogen_idx < heavy_idx:
        heavy_idx = heavy_idx - 1

    # Combine the main molecule and the functional group.
    combo = Chem.CombineMols(mol_no_H, fg)
    emol_combo = Chem.EditableMol(combo)
    n_atoms_main = mol_no_H.GetNumAtoms()

    # Identify the dummy attachment point in the functional group.
    dummy_idx = None
    for atom in fg.GetAtoms():
        if atom.GetAtomicNum() == 0:  # dummy atom
            dummy_idx = atom.GetIdx()
            break
    if dummy_idx is None:
        dummy_idx = 0  # fallback if no dummy found

    new_dummy_idx = n_atoms_main + dummy_idx
    # Add a bond between the heavy atom (in main mol) and the dummy atom (in fg).
    emol_combo.AddBond(heavy_idx, new_dummy_idx, order=Chem.rdchem.BondType.SINGLE)
    new_mol = emol_combo.GetMol()

    # Remove the dummy atom from the combined molecule.
    rw_mol = Chem.RWMol(new_mol)
    try:
        rw_mol.BeginBatchEdit()
        rw_mol.RemoveAtom(new_dummy_idx)
        rw_mol.CommitBatchEdit()
    except Exception as e:
        st.error(f"Error removing dummy atom: {str(e)}")
    final_mol = rw_mol.GetMol()
    Chem.SanitizeMol(final_mol)
    return final_mol

# -----------------------------
# Main Game Class
# -----------------------------
class LipinskiGame:
    def __init__(self):
        self.setup_page()
        self.initialize_session_state()
        self.main_game_loop()
    
    def setup_page(self):
        st.set_page_config(page_title="Drug Designer Challenge", layout="wide")
        st.title("💊 Drug Designer Challenge")
        st.markdown("Learn Lipinski's Rule of 5 by designing drug-like molecules!")
    
    def initialize_session_state(self):
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'current_molecule' not in st.session_state:
            st.session_state.current_molecule = "CC"  # Start with ethane
        if 'game_mode' not in st.session_state:
            st.session_state.game_mode = "tutorial"
        if 'message' not in st.session_state:
            st.session_state.message = ""
        if 'view_3d' not in st.session_state:
            st.session_state.view_3d = False
        # For Time Trial mode: set a start time (in seconds)
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None
            
    def calculate_lipinski_parameters(self, mol):
        if mol is None:
            return None
        
        mw = Descriptors.ExactMolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        
        return {
            "Molecular Weight": mw,
            "LogP": logp,
            "H-Bond Donors": hbd,
            "H-Bond Acceptors": hba
        }
    
    def check_lipinski_compliance(self, params):
        if params is None:
            return False
        
        # Each parameter comes with an explanation (for educational value).
        rules = {
            "Molecular Weight": params["Molecular Weight"] <= 500,
            "LogP": params["LogP"] <= 5,
            "H-Bond Donors": params["H-Bond Donors"] <= 5,
            "H-Bond Acceptors": params["H-Bond Acceptors"] <= 10
        }
        compliance = sum(rules.values()) >= 3  # Allow one violation
        return rules, compliance
    
    def display_molecule(self, smiles):
        # Toggle for 2D/3D view
        st.session_state.view_3d = st.toggle('Switch to 3D View', st.session_state.view_3d)
        
        if st.session_state.view_3d:
            # 3D View using cached molblock
            molblock = get_3d_molblock(smiles)
            if molblock:
                viewer_html = f"""
                <div style="height: 400px; width: 400px;">
                    <script src="https://3dmol.org/build/3Dmol-min.js"></script>
                    <script>
                        let element = document.currentScript.parentElement;
                        let viewer = $3Dmol.createViewer(element, {{backgroundColor: "white"}});
                        let mol = `{molblock}`;
                        viewer.addModel(mol, "mol");
                        viewer.setStyle({{}}, {{stick: {{}}}});
                        viewer.zoomTo();
                        viewer.render();
                    </script>
                </div>
                """
                st.components.v1.html(viewer_html, height=400)
            else:
                st.error("3D visualization failed.")
        else:
            # 2D View using cached image generation
            img = get_2d_image(smiles)
            if img:
                st.image(img)
            else:
                st.error("2D visualization failed.")
    
    def display_parameters(self, params, rules):
        if params is None:
            return
            
        # Detailed explanations for educational purposes.
        explanations = {
            "Molecular Weight": "A measure of mass; lower values (<500 Da) often improve absorption.",
            "LogP": "Indicates lipophilicity; values below 5 favor balanced solubility and permeability.",
            "H-Bond Donors": "Fewer donors (≤5) help avoid excessive water interactions.",
            "H-Bond Acceptors": "A limit of ≤10 promotes optimal drug–target binding."
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Molecular Parameters")
            for param, value in params.items():
                status = "✅" if rules[0][param] else "❌"
                st.write(f"{param}: {value:.2f} {status}")
                st.caption(explanations.get(param, ""))
                
        with col2:
            st.subheader("Lipinski Compliance")
            if rules[1]:
                st.success("Molecule is drug-like! 🎉")
                # Only increment score on submission (not on every refresh) and outside tutorial mode.
                if st.session_state.game_mode != "tutorial" and not st.session_state.get("submitted", False):
                    st.session_state.score += 1
                    st.session_state.submitted = True  # Flag to prevent re-scoring until molecule change.
            else:
                st.warning("Molecule needs optimization 🔧")
    
    def functional_group_editor(self):
        st.subheader("Modify Your Molecule")
        
        # Define functional groups with dummy attachment points for reaction-based attachment.
        functional_groups = {
            "Methyl (-CH3)": "[*:1]C",
            "Hydroxyl (-OH)": "[*:1]O",
            "Amine (-NH2)": "[*:1]N",
            "Carboxyl (-COOH)": "[*:1]C(=O)O",
            "Benzene Ring": "[*:1]c1ccccc1"
        }
        
        st.text(f"Current SMILES: {st.session_state.current_molecule}")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_group = st.selectbox(
                "Select functional group to add:",
                list(functional_groups.keys())
            )
            
            if st.button("Add Group"):
                try:
                    mol = Chem.MolFromSmiles(st.session_state.current_molecule)
                    if mol is None:
                        st.session_state.message = "Current molecule is invalid!"
                    else:
                        new_mol = attach_functional_group(mol, functional_groups[selected_group])
                        if new_mol is not None:
                            st.session_state.current_molecule = Chem.MolToSmiles(new_mol)
                            st.session_state.message = "Group added successfully!"
                            st.session_state.submitted = False  # Reset submission flag for scoring
                        else:
                            st.session_state.message = "Invalid modification!"
                except Exception as e:
                    st.session_state.message = f"Error: {str(e)}"
                    
        with col2:
            smiles_input = st.text_input(
                "Or enter SMILES directly:",
                st.session_state.current_molecule
            )
            if smiles_input != st.session_state.current_molecule:
                mol = Chem.MolFromSmiles(smiles_input)
                if mol is not None:
                    st.session_state.current_molecule = smiles_input
                    st.session_state.message = "SMILES updated successfully!"
                    st.session_state.submitted = False
                else:
                    st.session_state.message = "Invalid SMILES!"
        
        if st.session_state.message:
            st.info(st.session_state.message)
            st.session_state.message = ""
    
    def game_modes(self):
        st.sidebar.title("Game Modes")
        new_mode = st.sidebar.radio(
            "Select Mode:",
            ["Tutorial", "Design Challenge", "Fix-It Mode", "Time Trial"]
        ).lower()
        
        if new_mode != st.session_state.game_mode:
            st.session_state.game_mode = new_mode
            st.session_state.current_molecule = "CC"  # Reset molecule
            st.session_state.score = 0  # Reset score
            st.session_state.submitted = False
            # Reset timer if switching to time trial
            if new_mode == "time trial":
                st.session_state.start_time = time.time()
            else:
                st.session_state.start_time = None
    
    def show_instructions(self):
        with st.sidebar.expander("📖 How to Play", expanded=True):
            st.markdown("""
            ### 🎮 Game Controls
            1. **Add Functional Groups**: Select a group and click 'Add Group' (functional groups attach via reaction-based chemistry).
            2. **Direct SMILES**: Enter SMILES notation directly.
            3. **Monitor Parameters**: Watch the molecular parameters and their explanations update in real-time.
            4. **Check Compliance**: Green checkmarks (✅) indicate parameters within Lipinski's limits.
            
            ### 🎯 Game Modes
            - **Tutorial**: Learn the basics with guided examples.
            - **Design Challenge**: Build drug-like molecules from scratch.
            - **Fix-It Mode**: Optimize non-compliant molecules.
            - **Time Trial**: Race against the clock (60 seconds) to design a compliant molecule.
            
            ### 💡 Tips
            - Start small and build up your molecule.
            - Notice how each functional group affects properties.
            - One rule violation is allowed!
            """)
    
    def tutorial_mode(self):
        st.markdown("""
        ## 📚 Tutorial Mode
        
        ### Lipinski's Rule of 5:
        1. **Molecular Weight** < 500 daltons  
           *Helps with absorption through cell membranes.*
        
        2. **LogP** < 5  
           *Balances water solubility and membrane penetration.*
        
        3. **H-Bond Donors** ≤ 5  
           *Affects interaction with water molecules.*
        
        4. **H-Bond Acceptors** ≤ 10  
           *Influences drug–target binding strength.*
        
        ### 🎯 Your Mission:
        Start with ethane (CC) and modify it to create a drug-like molecule:
        - Add functional groups one at a time.
        - Watch how each addition affects the properties.
        - Aim to meet the criteria (one rule violation is allowed).
        
        ### 💡 Educational Insights:
        - Each parameter has an impact on drug absorption and efficacy.
        - Read the inline explanations to understand why each threshold matters.
        """)
    
    def design_challenge_mode(self):
        st.markdown("""
        ## 🔬 Design Challenge Mode
        
        ### 🎯 Objective:
        Design drug-like molecules that follow Lipinski's Rule of 5.
        
        ### 📋 Challenge Rules:
        - Build up from a simple starting molecule.
        - Create a molecule with:
          - Molecular Weight < 500 daltons
          - LogP < 5
          - H-Bond Donors ≤ 5
          - H-Bond Acceptors ≤ 10
        
        ### 💯 Scoring:
        - +1 point for each compliant molecule.
        - See the detailed score breakdown in the parameters panel.
        """)
    
    def time_trial_mode(self):
        st.markdown("""
        ## ⏱️ Time Trial Mode
        
        ### 🎯 Objective:
        Create as many compliant molecules as possible within 60 seconds.
        
        ### ⏳ How It Works:
        - A countdown timer is shown on the sidebar.
        - Each valid submission increases your score.
        - Try to optimize quickly without sacrificing compliance!
        """)
    
    def main_game_loop(self):
        self.game_modes()
        
        # Display mode-specific instructions
        if st.session_state.game_mode == "tutorial":
            self.tutorial_mode()
        elif st.session_state.game_mode == "design challenge":
            self.design_challenge_mode()
        elif st.session_state.game_mode == "time trial":
            self.time_trial_mode()
        
        # In Time Trial, show timer and check for time expiry.
        if st.session_state.game_mode == "time trial":
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()
            elapsed = time.time() - st.session_state.start_time
            remaining = 60 - elapsed
            st.sidebar.markdown(f"## Time Remaining: {int(remaining)} seconds")
            if remaining <= 0:
                st.sidebar.error("Time's up!")
                st.stop()  # Stop further processing when time expires
        
        # Display current molecule and visualization.
        self.display_molecule(st.session_state.current_molecule)
        
        # Calculate and display parameters.
        mol = Chem.MolFromSmiles(st.session_state.current_molecule)
        params = self.calculate_lipinski_parameters(mol)
        rules = self.check_lipinski_compliance(params)
        self.display_parameters(params, rules)
        
        # Molecule editor.
        self.functional_group_editor()
        
        # Score display.
        st.sidebar.markdown(f"## Score: {st.session_state.score}")

if __name__ == "__main__":
    game = LipinskiGame()
