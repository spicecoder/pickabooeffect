import numpy as np
from typing import List, Set, Tuple

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
        
    def get_valid_paths(self, max_length: int = 10) -> List[List[str]]:
        """Generate valid CPUXs using matrix operations"""
        valid_paths = []
        
        # Start with both objects and intentions as valid starting points
        current_paths = []
        # Add paths starting with intentions
        current_paths.extend([[i + self.n_dn] for i in range(self.n_i)])
        # Add paths starting with objects
        current_paths.extend([[i + self.n_dn + self.n_i] for i in range(self.n_o)])
        
        for _ in range(max_length - 1):
            new_paths = []
            for path in current_paths:
                last_idx = path[-1]
                # Get possible next steps from transition matrix
                for next_idx in range(self.n_total):
                    if self.transition_matrix[last_idx, next_idx] > 0:
                        new_path = path + [next_idx]
                        if self.is_valid_sequence(new_path):
                            if new_path not in valid_paths:
                                valid_paths.append(new_path)
                        new_paths.append(new_path)
            current_paths = new_paths
            if not current_paths:  # No more paths to explore
                break
                
        return [self._convert_path_to_components(path) for path in valid_paths]
    
    def is_valid_sequence(self, path: List[int]) -> bool:
        """Check if sequence follows CPUX rules"""
        if len(path) < 3:  # Minimum path length
            return False
            
        # Check pattern validity
        for i in range(len(path) - 1):
            curr_type = self._get_component_type(path[i])
            next_type = self._get_component_type(path[i + 1])
            
            # Valid transitions:
            # DN -> I
            # I -> DN or I -> O
            # O -> I
            if curr_type == "DN" and next_type != "I":
                return False
            elif curr_type == "I" and next_type not in ["DN", "O"]:
                return False
            elif curr_type == "O" and next_type != "I":
                return False
            
            # Verify transition exists in matrix
            if self.transition_matrix[path[i], path[i + 1]] == 0:
                return False
                
        return True
    
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

# Example usage
if __name__ == "__main__":
    intentions = ["i1", "i2", "i3", "i4", "i5"]
    objects = ["o1", "o2", "o3"]
    design_nodes = ["dn1", "dn2", "dn3"]
    
    generator = CPUXGenerator(intentions, objects, design_nodes)
    
    # Add valid trios
    generator.add_ioi_trio(0, 0, 1)  # i1-o1-i2
    generator.add_ioi_trio(1, 1, 2)  # i2-o2-i3
    generator.add_ioi_trio(4, 2, 2)  # i5-o3-i3
    generator.add_ioi_trio(2, 2, 4)  # i3-o3-i5
    generator.add_idni_trio(1, 1, 2)  # i2-dn2-i3
    
    valid_cpuxs = generator.get_valid_paths(max_length=8)
    print("\nValid CPUXs including derived o-i-o patterns:")
    print("--------------------------------------------")
    for cpux in valid_cpuxs:
        print(" -> ".join(cpux))