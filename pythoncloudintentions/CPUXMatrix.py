import numpy as np

# Define Identifiers
intentions = ["i1", "i2", "i3", "i4", "i5", "i6", "i7", "i8", "i9"]
objects = ["o1", "o2", "o3"]
design_nodes = ["d1", "d2", "d3"]

num_intentions = len(intentions)
num_objects = len(objects)
num_design_nodes = len(design_nodes)

# Intention-Design Node-Intention Matrix (I_Dn_I) - Expanding to 9x9
I_Dn_I = np.zeros((num_intentions, num_intentions))
I_Dn_I[0, 2] = 1  # i1 → d1 → i3
I_Dn_I[1, 3] = 1  # i2 → d1 → i4
I_Dn_I[2, 5] = 1  # i3 → d2 → i6
I_Dn_I[3, 6] = 1  # i4 → d3 → i7
I_Dn_I[4, 7] = 1  # i5 → d2 → i8

# Intention-Object-Intention Matrix (I_O_I) - Expanding to 9x9
I_O_I = np.zeros((num_intentions, num_intentions))
I_O_I[0, 2] = 1  # i1 → o1 → i3
I_O_I[1, 3] = 1  # i2 → o2 → i4
I_O_I[2, 5] = 1  # i3 → o1 → i6
I_O_I[3, 6] = 1  # i4 → o2 → i7
I_O_I[4, 7] = 1  # i5 → o3 → i8

# Unified Transition Matrix (T_Unified) - Merging I_Dn_I and I_O_I (Ensuring 9x9)
T_Unified = I_Dn_I + I_O_I

# Design Node to Intention Matrix (D_I) - Mapping (3x9)
D_I = np.zeros((num_design_nodes, num_intentions))
D_I[0, 0] = 1  # d1 starts with i1
D_I[0, 1] = 1  # d1 starts with i2
D_I[1, 2] = 1  # d2 starts with i3
D_I[1, 4] = 1  # d2 starts with i5
D_I[2, 3] = 1  # d3 starts with i4

# Function to compute all valid I-O-I-[O/Dn] sequences starting from a Design Node (Dn)
def compute_sequences_from_dn(start_dn_index):
    # Step 1: Get initial set of Intentions from the Design Node
    I_valid = np.copy(D_I[start_dn_index, :].reshape(1, -1))  # Shape (1, num_intentions)

    # Step 2: Propagate through the transition matrix iteratively
    max_iterations = num_intentions  # Prevent infinite loops
    iteration = 0
    while iteration < max_iterations:
        new_I_valid = np.dot(I_valid, T_Unified)  # Apply transitions
        if np.array_equal(new_I_valid, I_valid):  # Stop if no further changes
            break
        I_valid += new_I_valid  # Accumulate valid transitions
        iteration += 1

    return I_valid

# Compute all sequences from each Design Node
all_sequences = {}
for dn_index in range(num_design_nodes):
    all_sequences[design_nodes[dn_index]] = compute_sequences_from_dn(dn_index)

# Convert to Readable Output
def print_cpux_sequences():
    for dn, seq_matrix in all_sequences.items():
        print(f"\nStarting from {dn}:")
        for i in range(num_intentions):
            for j in range(num_intentions):
                if seq_matrix[0, j] > 0:  # Valid transition exists
                    print(f"  {dn} → {intentions[i]} → {intentions[j]}")

print_cpux_sequences()
