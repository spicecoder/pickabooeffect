import numpy as np
from typing import List, Set, Tuple, Dict, Optional

class CPUXGenerator:
    def __init__(self, intentions: List[str], objects: List[str], design_nodes: List[str]):
        self.intentions = intentions
        self.objects = objects
        self.design_nodes = design_nodes
        
        # Initialize basic adjacency matrices
        self.dn_i_matrix = np.zeros((len(design_nodes), len(intentions)))  # DN -> I emissions
        self.i_dn_matrix = np.zeros((len(intentions), len(design_nodes)))  # I -> DN absorptions
        self.i_o_matrix = np.zeros((len(intentions), len(objects)))       # I -> O received
        self.o_i_matrix = np.zeros((len(objects), len(intentions)))       # O -> I reflections
        
        # Store valid i-o-i trios and i-dn-i trios
        self.valid_ioi: Set[Tuple[int, int, int]] = set()
        self.valid_idni: Set[Tuple[int, int, int]] = set()
        
        # Initialize combined transition matrix
        self.n_dn = len(design_nodes)
        self.n_i = len(intentions)
        self.n_o = len(objects)
        self.n_total = self.n_dn + self.n_i + self.n_o
        self.transition_matrix = np.zeros((self.n_total, self.n_total))
        
    def add_ioi_trio(self, i1_idx: int, o_idx: int, i2_idx: int):
        """Add valid i-o-i trio"""
        self.valid_ioi.add((i1_idx, o_idx, i2_idx))
        self.i_o_matrix[i1_idx, o_idx] = 1
        self.o_i_matrix[o_idx, i2_idx] = 1
        self._update_transition_matrix()
        
    def add_idni_trio(self, i1_idx: int, dn_idx: int, i2_idx: int):
        """Add valid i-dn-i trio"""
        self.valid_idni.add((i1_idx, dn_idx, i2_idx))
        self.i_dn_matrix[i1_idx, dn_idx] = 1
        self.dn_i_matrix[dn_idx, i2_idx] = 1
        self._update_transition_matrix()
        
    def _update_transition_matrix(self):
        """Update the combined transition matrix"""
        self.transition_matrix.fill(0)
        
        # DN -> I transitions
        self.transition_matrix[0:self.n_dn, self.n_dn:self.n_dn+self.n_i] = self.dn_i_matrix
        
        # I -> DN transitions
        self.transition_matrix[self.n_dn:self.n_dn+self.n_i, 0:self.n_dn] = self.i_dn_matrix
        
        # I -> O transitions
        self.transition_matrix[self.n_dn:self.n_dn+self.n_i, self.n_dn+self.n_i:] = self.i_o_matrix
        
        # O -> I transitions
        self.transition_matrix[self.n_dn+self.n_i:, self.n_dn:self.n_dn+self.n_i] = self.o_i_matrix

    def _get_component_type(self, idx: int) -> str:
        """Get the type of component (DN, I, or O) for a given index"""
        if idx < self.n_dn:
            return "DN"
        elif idx < self.n_dn + self.n_i:
            return "I"
        else:
            return "O"
        
    def is_valid_sequence(self, path: List[int]) -> bool:
        """Check if sequence follows CPUX rules"""
        if len(path) < 3:
            return False
            
        # Check pattern rules
        for i in range(len(path) - 1):
            curr_type = self._get_component_type(path[i])
            next_type = self._get_component_type(path[i + 1])
            
            # Valid transitions: DN->I, I->DN or I->O, O->I
            if curr_type == "DN" and next_type != "I":
                return False
            elif curr_type == "I" and next_type not in ["DN", "O"]:
                return False
            elif curr_type == "O" and next_type != "I":
                return False
            
            if self.transition_matrix[path[i], path[i + 1]] == 0:
                return False
                
        return True
    
    def get_valid_paths(self, max_length: int = 10) -> List[List[str]]:
        """Generate valid CPUXs using matrix operations"""
        valid_paths = []
        
        # Start with both objects and intentions
        current_paths = []
        current_paths.extend([[i + self.n_dn] for i in range(self.n_i)])
        current_paths.extend([[i + self.n_dn + self.n_i] for i in range(self.n_o)])
        
        for _ in range(max_length - 1):
            new_paths = []
            for path in current_paths:
                last_idx = path[-1]
                for next_idx in range(self.n_total):
                    if self.transition_matrix[last_idx, next_idx] > 0:
                        new_path = path + [next_idx]
                        if self.is_valid_sequence(new_path):
                            if new_path not in valid_paths:
                                valid_paths.append(new_path)
                        new_paths.append(new_path)
            current_paths = new_paths
            if not current_paths:
                break
                
        return [self._convert_path_to_components(path) for path in valid_paths]
    
    def _convert_path_to_components(self, path: List[int]) -> List[str]:
        """Convert numeric path to component names"""
        result = []
        for idx in path:
            if idx < self.n_dn:
                result.append(self.design_nodes[idx])
            elif idx < self.n_dn + self.n_i:
                result.append(self.intentions[idx - self.n_dn])
            else:
                result.append(self.objects[idx - self.n_dn - self.n_i])
        return result

class PnRSet:
    def __init__(self, pnrs: Dict[str, Tuple[str, str]]):
        """
        Initialize PnR set where:
        pnrs = {
            "prompt": ("response", "trivalence")  # trivalence: "Y"/"N"/"U"
        }
        """
        self.pnrs = pnrs
    
    def synctest(self, other: 'PnRSet') -> bool:
        """Implementation of the synctest algorithm"""
        for prompt, (_, trivalence) in self.pnrs.items():
            if prompt in other.pnrs:
                other_trivalence = other.pnrs[prompt][1]
                if trivalence != other_trivalence:
                    return False
        return True

class Component:
    def __init__(self, name: str, gatekeeper: Optional[PnRSet] = None, 
                 flowin: Optional[PnRSet] = None, flowout: Optional[PnRSet] = None):
        self.name = name
        self.gatekeeper = gatekeeper or PnRSet({})
        self.flowin = flowin or PnRSet({})
        self.flowout = flowout or PnRSet({})

class CPUXGeneratorWithPnR(CPUXGenerator):
    def __init__(self, intentions: List[str], objects: List[str], design_nodes: List[str]):
        super().__init__(intentions, objects, design_nodes)
        self.components: Dict[str, Component] = {}
        
    def add_component_pnr(self, component_name: str, 
                         gatekeeper: Optional[Dict[str, Tuple[str, str]]] = None,
                         flowin: Optional[Dict[str, Tuple[str, str]]] = None,
                         flowout: Optional[Dict[str, Tuple[str, str]]] = None):
        """Add PnR sets for a component"""
        self.components[component_name] = Component(
            component_name,
            PnRSet(gatekeeper or {}),
            PnRSet(flowin or {}),
            PnRSet(flowout or {})
        )
        
    def is_feasible_path(self, path: List[str]) -> Tuple[bool, Optional[str]]:
        """Check if a path is feasible based on PnR constraints"""
        current_pnr = PnRSet({})
        
        for i in range(len(path)):
            component = self.components.get(path[i])
            if not component:
                continue
                
            # Check gatekeeper
            if not component.gatekeeper.synctest(current_pnr):
                return False, f"Gatekeeper check failed at {path[i]}"
                
            # Apply flowin
            if component.flowin.pnrs:
                for prompt, (response, trivalence) in component.flowin.pnrs.items():
                    if prompt in current_pnr.pnrs:
                        current_pnr.pnrs[prompt] = (response, trivalence)
                        
            # Apply flowout
            if component.flowout.pnrs:
                for prompt, (response, trivalence) in component.flowout.pnrs.items():
                    current_pnr.pnrs[prompt] = (response, trivalence)
                    
        return True, None
    
    def get_feasible_cpuxs(self, max_length: int = 10) -> List[Tuple[List[str], PnRSet]]:
        """Get all feasible CPUXs with their final PnR states"""
        valid_cpuxs = self.get_valid_paths(max_length)
        feasible_cpuxs = []
        
        for cpux in valid_cpuxs:
            feasible, reason = self.is_feasible_path(cpux)
            if feasible:
                final_pnr = self._calculate_final_pnr(cpux)
                feasible_cpuxs.append((cpux, final_pnr))
                
        return feasible_cpuxs
    
    def _calculate_final_pnr(self, path: List[str]) -> PnRSet:
        """Calculate the final PnR state for a path"""
        current_pnr = PnRSet({})
        
        for component_name in path:
            component = self.components.get(component_name)
            if component and component.flowout.pnrs:
                for prompt, (response, trivalence) in component.flowout.pnrs.items():
                    current_pnr.pnrs[prompt] = (response, trivalence)
                    
        return current_pnr
    def get_categorized_cpuxs(self, max_length: int = 10) -> Dict[str, List[Tuple[List[str], PnRSet]]]:
        """
        Get CPUXs categorized by design node presence
        Returns:
            Dictionary with two keys:
            - 'with_dn': CPUXs containing at least one design node
            - 'without_dn': CPUXs with no design nodes
        """
        valid_cpuxs = self.get_valid_paths(max_length)
        categorized_cpuxs = {
            'with_dn': [],
            'without_dn': []
        }
        
        for cpux in valid_cpuxs:
            feasible, reason = self.is_feasible_path(cpux)
            if not feasible:
                continue
                
            final_pnr = self._calculate_final_pnr(cpux)
            
            # Check if CPUX contains any design nodes
            has_dn = any(component in self.design_nodes for component in cpux)
            
            if has_dn:
                categorized_cpuxs['with_dn'].append((cpux, final_pnr))
            else:
                categorized_cpuxs['without_dn'].append((cpux, final_pnr))
                
        return categorized_cpuxs

#
# Example usage
if __name__ == "__main__":
    intentions = ["i1", "i2", "i3"]
    objects = ["o1", "o2", "o3"]
    design_nodes = ["dn1", "dn2"]
    
    generator = CPUXGeneratorWithPnR(intentions, objects, design_nodes)
    
    # Add valid trios
    generator.add_ioi_trio(0, 0, 1)  # i1-o1-i2
    generator.add_ioi_trio(1, 1, 2)  # i2-o2-i3
    generator.add_idni_trio(1, 0, 2)  # i2-dn1-i3
    
    # Add PnR configurations
    generator.add_component_pnr(
        "o1",
        gatekeeper={"ready": ("yes", "Y")},
        flowin={"status": ("pending", "Y")},
        flowout={"processed": ("true", "Y")}
    )
    
    generator.add_component_pnr(
        "dn1",
        gatekeeper={"processed": ("true", "Y")},
        flowin={"input": ("valid", "Y")},
        flowout={"output": ("processed", "Y")}
    )
    
    feasible_cpuxs = generator.get_feasible_cpuxs(max_length=6)
    print("\nFeasible CPUXs with their final PnR states:")
    print("------------------------------------------")
    for cpux, final_pnr in feasible_cpuxs:
        print(f"Path: {' -> '.join(cpux)}")
        print("Final PnR state:")
        for prompt, (response, trivalence) in final_pnr.pnrs.items():
            print(f"  {prompt}: {response} ({trivalence})")
        print()
# Example usage
if __name__ == "__main__":
    intentions = ["i1", "i2", "i3"]
    objects = ["o1", "o2", "o3"]
    design_nodes = ["dn1", "dn2"]
    
    generator = CPUXGeneratorWithPnR(intentions, objects, design_nodes)
    
    # Add valid trios
    generator.add_ioi_trio(0, 0, 1)  # i1-o1-i2
    generator.add_ioi_trio(1, 1, 2)  # i2-o2-i3
    generator.add_ioi_trio(2, 2, 1)  # i3-o3-i2
    generator.add_idni_trio(1, 0, 2)  # i2-dn1-i3
    
    # Add PnR configurations
    generator.add_component_pnr(
        "o1",
        gatekeeper={"ready": ("yes", "Y")},
        flowin={"status": ("pending", "Y")},
        flowout={"processed": ("true", "Y")}
    )
    
    generator.add_component_pnr(
        "dn1",
        gatekeeper={"processed": ("true", "Y")},
        flowin={"input": ("valid", "Y")},
        flowout={"output": ("processed", "Y")}
    )
    
    categorized_cpuxs = generator.get_categorized_cpuxs(max_length=6)
    
    print("\nCPUXs with Design Nodes:")
    print("------------------------")
    for cpux, final_pnr in categorized_cpuxs['with_dn']:
        print(f"Path: {' -> '.join(cpux)}")
        print("Final PnR state:")
        for prompt, (response, trivalence) in final_pnr.pnrs.items():
            print(f"  {prompt}: {response} ({trivalence})")
        print()
        
    print("\nCPUXs without Design Nodes (Pure Object Reflections):")
    print("---------------------------------------------------")
    for cpux, final_pnr in categorized_cpuxs['without_dn']:
        print(f"Path: {' -> '.join(cpux)}")
        print("Final PnR state:")
        for prompt, (response, trivalence) in final_pnr.pnrs.items():
            print(f"  {prompt}: {response} ({trivalence})")
        print()


