# encoding:utf-8
# @file CubeEncrypt.py
# @brief Enhanced Cube encryption and decryption tool with multi-key support
# @author Dc-3387
# @date 2024-06-20
# @version 2.0
# @license AGPL-3.0
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import random
import copy
import argparse
import json
import os
import hashlib
from typing import List, Tuple, Dict, Any

# The face Dict
FaceDict = {
    "F": 0, # Front
    "T": 1, # Top
    "B": 2, # Back
    "D": 3, # Down
    "L": 4, # Left
    "R": 5  # Right
}

# Dict to list all possible moves(max: move for Cubes of order 7)
# Dict to list all possible moves(max: move for Cubes of order 7)
moveDict = {
    "L1": (0, 1), "L1'": (0, -1), "R1": (1, 1), "R1'": (1, -1),
    "U1": (2, 1), "U1'": (2, -1), "D1": (3, 1), "D1'": (3, -1),
}

order = 25  # Default cube order

# function to use loop to add more moves to the moveDict
def generate_moves(order):
    for i in range(order):
        layer = i * 2
        moveDict[f"L{i+1}"] = (layer, 1)
        moveDict[f"L{i+1}'"] = (layer, -1)
        moveDict[f"R{i+1}"] = (layer + 1, 1)
        moveDict[f"R{i+1}'"] = (layer + 1, -1)
        moveDict[f"U{i+1}"] = (layer + 2, 1)
        moveDict[f"U{i+1}'"] = (layer + 2, -1)
        moveDict[f"D{i+1}"] = (layer + 3, 1)
        moveDict[f"D{i+1}'"] = (layer + 3, -1)


class Cube:
    def __init__(self, order, cube_data=None):
        self.order = order
        # Face Sequence: Front, Top, Back, Down, Left, Right
        self.face_names = ["F", "T", "B", "D", "L", "R"]
        if cube_data:
            self.faces = self._linear_to_faces(cube_data)
        else:
            self.faces = [[['' for _ in range(order)] for _ in range(order)] for _ in range(6)]
    
    def _linear_to_faces(self, linear_data):
        n = self.order
        faces = [[['' for _ in range(n)] for _ in range(n)] for _ in range(6)]
        
        for idx, char in enumerate(linear_data):
            if idx >= len(linear_data):
                break
            face_idx = idx // (n * n)
            if face_idx >= 6:
                break
            pos_in_face = idx % (n * n)
            row = pos_in_face // n
            col = pos_in_face % n
            if row < n and col < n:
                faces[face_idx][row][col] = char
        
        return faces
    
    def _faces_to_linear(self):
        n = self.order
        linear_data = []
        for face_idx in range(6):
            for row in range(n):
                for col in range(n):
                    linear_data.append(self.faces[face_idx][row][col])
        return linear_data
    
    def rotate_LR(self, which, direction):
        n = self.order
        if which < 0 or which >= n:
            return
            
        if direction == 1:  # Clockwise
            temp = [self.faces[0][r][which] for r in range(n)]
            
            for r in range(n):
                self.faces[0][r][which] = self.faces[3][n-1-r][n-1-which]
            for r in range(n):
                self.faces[3][n-1-r][n-1-which] = self.faces[2][r][n-1-which]
            for r in range(n):
                self.faces[2][r][n-1-which] = self.faces[1][n-1-r][which]
            for r in range(n):
                self.faces[1][r][which] = temp[r]
            
            if which == 0:
                self._rotate_face(4, 1)
            elif which == n-1:
                self._rotate_face(5, 1)
                
        else:  # Counter-clockwise
            temp = [self.faces[0][r][which] for r in range(n)]
            
            for r in range(n):
                self.faces[0][r][which] = self.faces[1][r][which]
            for r in range(n):
                self.faces[1][r][which] = self.faces[2][n-1-r][n-1-which]
            for r in range(n):
                self.faces[2][n-1-r][n-1-which] = self.faces[3][r][n-1-which]
            for r in range(n):
                self.faces[3][r][n-1-which] = temp[n-1-r]
            
            if which == 0:
                self._rotate_face(4, -1)
            elif which == n-1:
                self._rotate_face(5, -1)
    
    def rotate_UD(self, which, direction):
        n = self.order
        if which < 0 or which >= n:
            return
            
        if direction == 1:  # Clockwise
            temp = self.faces[0][which][:]
            
            for c in range(n):
                self.faces[0][which][c] = self.faces[5][which][c]
            for c in range(n):
                self.faces[5][which][c] = self.faces[2][which][c]
            for c in range(n):
                self.faces[2][which][c] = self.faces[4][which][c]
            for c in range(n):
                self.faces[4][which][c] = temp[c]
            
            if which == 0:
                self._rotate_face(1, 1)
            elif which == n-1:
                self._rotate_face(3, 1)
                
        else:  # Counter-clockwise
            temp = self.faces[0][which][:]
            
            for c in range(n):
                self.faces[0][which][c] = self.faces[4][which][c]
            for c in range(n):
                self.faces[4][which][c] = self.faces[2][which][c]
            for c in range(n):
                self.faces[2][which][c] = self.faces[5][which][c]
            for c in range(n):
                self.faces[5][which][c] = temp[c]
            
            if which == 0:
                self._rotate_face(1, -1)
            elif which == n-1:
                self._rotate_face(3, -1)
    
    def _rotate_face(self, face_idx, direction):
        n = self.order
        if face_idx < 0 or face_idx >= 6:
            return
            
        face = [row[:] for row in self.faces[face_idx]]
        new_face = [['' for _ in range(n)] for _ in range(n)]
        
        if direction == 1:
            for r in range(n):
                for c in range(n):
                    new_face[c][n-1-r] = face[r][c]
        else:
            for r in range(n):
                for c in range(n):
                    new_face[n-1-c][r] = face[r][c]
        
        self.faces[face_idx] = new_face
    
    def get_state_hash(self):
        """Get a hash of current cube state for verification"""
        state_string = ''.join(self.cube)
        return hashlib.md5(state_string.encode()).hexdigest()[:8]
    
    @property
    def cube(self):
        return self._faces_to_linear()
    
    @cube.setter
    def cube(self, value):
        self.faces = self._linear_to_faces(value)


def initCube(cubeString, order=7):
    cubeString = cubeString.replace(" ", "").replace("\n", "")
    totalChars = len(cubeString)
    charsPerCube = order * order * 6
    numCubes = (totalChars + charsPerCube - 1) // charsPerCube

    cubes = []
    for i in range(numCubes):
        cube_data = []
        for j in range(charsPerCube):
            charIndex = i * charsPerCube + j
            if charIndex < totalChars:
                ch = cubeString[charIndex]
            else:
                ch = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
            cube_data.append(ch)
        cubes.append(Cube(order, cube_data))
    return cubes


def cubeToString(cube):
    return ''.join(cube.cube)


def generateRandomMoves(numMoves):
    moves = list(moveDict.keys())
    randomMoves = random.choices(moves, k=numMoves)
    return randomMoves


def applyMoves(cube, moves):
    for move in moves:
        if move in moveDict:
            layer, direction = moveDict[move]
            if layer % 2 == 0:
                which = layer // 2
                cube.rotate_LR(which, direction)
            else:
                which = layer // 2
                cube.rotate_UD(which, direction)
    return cube


def decryptCube(cube, moves):
    reverseMoves = []
    for move in reversed(moves):
        if move.endswith("'"):
            reverseMove = move[:-1]
        else:
            reverseMove = move + "'"
        reverseMoves.append(reverseMove)
    
    decryptedCube = applyMoves(copy.deepcopy(cube), reverseMoves)
    return decryptedCube


def encryptCube(cube, moves):
    encryptedCube = applyMoves(copy.deepcopy(cube), moves)
    return encryptedCube


def generate_key_pool(num_cubes, moves_per_key=20, pool_multiplier=6):
    """
    Generate a pool of random keys for encryption
    
    Args:
        num_cubes: Number of cubes to encrypt
        moves_per_key: Number of moves per key
        pool_multiplier: Size of key pool (num_cubes * pool_multiplier)
    
    Returns:
        List of random move sequences
    """
    pool_size = num_cubes * pool_multiplier
    key_pool = []
    
    print(f"Generating key pool with {pool_size} keys...")
    for i in range(pool_size):
        moves = generateRandomMoves(moves_per_key)
        key_pool.append(moves)
    
    return key_pool


def selective_encrypt(cubes, key_pool, selection_method="random"):
    """
    Encrypt cubes using selective keys from the pool
    
    Args:
        cubes: List of cubes to encrypt
        key_pool: Pool of available keys
        selection_method: How to select keys ('random', 'sequential', 'hash_based')
    
    Returns:
        Tuple of (encrypted_cubes, used_key_indices)
    """
    encrypted_cubes = []
    used_key_indices = []
    
    for i, cube in enumerate(cubes):
        if selection_method == "random":
            key_index = random.randint(0, len(key_pool) - 1)
        elif selection_method == "sequential":
            key_index = i % len(key_pool)
        elif selection_method == "hash_based":
            cube_hash = cube.get_state_hash()
            key_index = int(cube_hash, 16) % len(key_pool)
        else:
            key_index = i % len(key_pool)
        
        selected_moves = key_pool[key_index]
        encrypted_cube = encryptCube(cube, selected_moves)
        encrypted_cubes.append(encrypted_cube)
        used_key_indices.append(key_index)
        
        print(f"Cube {i} encrypted with key {key_index} ({len(selected_moves)} moves)")
    
    return encrypted_cubes, used_key_indices


def brute_force_decrypt(encrypted_cubes, key_pool, max_attempts_per_cube=10):
    """
    Attempt to decrypt cubes using multiple keys from the pool
    
    Args:
        encrypted_cubes: List of encrypted cubes
        key_pool: Pool of possible keys
        max_attempts_per_cube: Maximum number of keys to try per cube
    
    Returns:
        List of decryption results with probabilities
    """
    results = []
    
    for i, encrypted_cube in enumerate(encrypted_cubes):
        cube_results = []
        attempts = min(max_attempts_per_cube, len(key_pool))
        
        # Try multiple random keys
        tested_indices = set()
        for attempt in range(attempts):
            # Ensure we don't test the same key twice
            available_indices = [idx for idx in range(len(key_pool)) if idx not in tested_indices]
            if not available_indices:
                break
                
            key_index = random.choice(available_indices)
            tested_indices.add(key_index)
            
            test_moves = key_pool[key_index]
            decrypted_cube = decryptCube(encrypted_cube, test_moves)
            decrypted_string = cubeToString(decrypted_cube)
            
            # Calculate readability score (simple heuristic)
            readable_chars = sum(1 for c in decrypted_string if c.isalnum() or c in ' .,!?;:\'"-')
            readability_score = readable_chars / len(decrypted_string)
            
            cube_results.append({
                'key_index': key_index,
                'decrypted_text': decrypted_string,
                'readability_score': readability_score,
                'key_moves': test_moves
            })
        
        # Sort by readability score
        cube_results.sort(key=lambda x: x['readability_score'], reverse=True)
        results.append({
            'cube_index': i,
            'attempts': len(cube_results),
            'best_result': cube_results[0] if cube_results else None,
            'all_results': cube_results
        })
    
    return results


def save_decryption_results(results, output_dir):
    """Save brute force decryption results to files"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    summary = []
    for result in results:
        cube_index = result['cube_index']
        best_result = result['best_result']
        
        if best_result:
            # Save best result
            best_file = os.path.join(output_dir, f"cube_{cube_index}_best.txt")
            with open(best_file, 'w') as f:
                f.write(best_result['decrypted_text'])
            
            # Save all attempts
            all_file = os.path.join(output_dir, f"cube_{cube_index}_all_attempts.json")
            with open(all_file, 'w') as f:
                json.dump(result['all_results'], f, indent=2, ensure_ascii=False)
            
            summary.append({
                'cube_index': cube_index,
                'best_score': best_result['readability_score'],
                'best_key': best_result['key_index'],
                'best_file': best_file
            })
    
    # Save summary
    summary_file = os.path.join(output_dir, "decryption_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="Enhanced Cube Encryption and Decryption Tool")
    parser.add_argument("-mode", choices=["encrypt", "decrypt", "bruteforce"], required=True, 
                       help="Operation mode: encrypt, decrypt, or bruteforce")
    parser.add_argument("-s", "--string", type=str, help="String to encrypt/decrypt")
    parser.add_argument("-f", "--file", type=str, help="File to read input string from")
    parser.add_argument("-k", "--key", type=str, required=True, help="Key file to save/load encryption keys")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file to save the result")
    parser.add_argument("-n", "--num_moves", type=int, default=20, help="Number of moves per key (default: 20)")
    parser.add_argument("--key_pool_size", type=int, default=6, help="Key pool multiplier (default: 6)")
    parser.add_argument("--selection", choices=["random", "sequential", "hash_based"], default="random",
                       help="Key selection method for encryption")
    parser.add_argument("--max_attempts", type=int, default=10, help="Max attempts per cube for bruteforce")
    parser.add_argument("--results_dir", type=str, default="decryption_results", 
                       help="Directory for bruteforce results")
    
    args = parser.parse_args()

    if not args.string and not args.file:
        print("Error: Either -s (string) or -f (file) must be provided.")
        exit(1)

    if args.string and args.file:
        print("Error: Only one of -s (string) or -f (file) should be provided.")
        exit(1)

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            inputString = ''.join(line.strip() for line in lines)
    else:
        inputString = args.string

    global order
    generate_moves(order)  # Generate moves for the specified order
    cubes = initCube(inputString, order)

    if args.mode == "encrypt":
        # Generate key pool
        key_pool = generate_key_pool(len(cubes), args.num_moves, args.key_pool_size)
        
        # Encrypt cubes using selective keys
        encrypted_cubes, used_key_indices = selective_encrypt(cubes, key_pool, args.selection)
        
        # Save keys and encrypted data
        key_data = {
            'key_pool': key_pool,
            'used_key_indices': used_key_indices,
            'selection_method': args.selection,
            'metadata': {
                'num_cubes': len(cubes),
                'key_pool_size': len(key_pool),
                'moves_per_key': args.num_moves,
                'encryption_date': str(os.path.getctime(__file__))
            }
        }
        
        with open(args.key, 'w') as kf:
            json.dump(key_data, kf, indent=2)

        with open(args.output, 'w') as of:
            for cube in encrypted_cubes:
                of.write(cubeToString(cube) + "\n")

        print(f"Encryption complete. Encrypted {len(cubes)} cubes using {len(key_pool)} key pool.")
        print(f"Output: {args.output}, Keys: {args.key}")

    elif args.mode == "decrypt":
        try:
            with open(args.key, 'r') as kf:
                key_data = json.load(kf)
            
            key_pool = key_data['key_pool']
            used_key_indices = key_data['used_key_indices']
            
        except Exception as e:
            print(f"Error reading key file: {e}")
            exit(1)

        print(f"Decrypting {len(cubes)} cubes with {len(key_pool)} key pool...")
        
        for i, cube in enumerate(cubes):
            if i < len(used_key_indices):
                key_index = used_key_indices[i]
                moves = key_pool[key_index]
                decrypted_cube = decryptCube(cube, moves)
                cube.cube = decrypted_cube.cube
                print(f"Cube {i} decrypted with key {key_index}")
            else:
                print(f"Warning: No key available for cube {i}")

        with open(args.output, 'w') as of:
            for cube in cubes:
                of.write(cubeToString(cube) + "\n")

        print(f"Decryption complete. Output: {args.output}")

    elif args.mode == "bruteforce":
        try:
            with open(args.key, 'r') as kf:
                key_data = json.load(kf)
            key_pool = key_data['key_pool']
        except Exception as e:
            print(f"Error reading key file: {e}")
            exit(1)

        print(f"Brute force decrypting {len(cubes)} cubes with {len(key_pool)} key pool...")
        print(f"Max attempts per cube: {args.max_attempts}")
        
        results = brute_force_decrypt(cubes, key_pool, args.max_attempts)
        summary = save_decryption_results(results, args.results_dir)
        
        print(f"\nBrute force decryption complete!")
        print(f"Results saved to: {args.results_dir}")
        print(f"\nSummary:")
        for item in summary:
            print(f"  Cube {item['cube_index']}: score={item['best_score']:.3f}, key={item['best_key']}")


if __name__ == "__main__":
    main()
