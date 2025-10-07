# encoding:utf-8
# @file CubeEncrypt.py
# @brief Enhanced Cube encryption and decryption tool with full cryptographic randomness
# @author Dc-3387
# @date 2024-06-20
# @version 4.0
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

import copy
import argparse
import json
import os
import hashlib
import secrets
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

# Global variables for cube order and move dictionary
moveDict = {}

def initialize_move_dict(cube_order):
    """Initialize move dictionary based on cube order"""
    global moveDict
    moveDict = {
        "L1": (0, 1), "L1'": (0, -1), "R1": (1, 1), "R1'": (1, -1),
        "U1": (2, 1), "U1'": (2, -1), "D1": (3, 1), "D1'": (3, -1),
    }
    
    # Add more moves based on cube order
    for i in range(1, cube_order):
        moveDict[f"L{i+1}"] = (i*2, 1)
        moveDict[f"L{i+1}'"] = (i*2, -1)
        moveDict[f"R{i+1}"] = (i*2 + 1, 1)
        moveDict[f"R{i+1}'"] = (i*2 + 1, -1)
        moveDict[f"U{i+1}"] = (i*2 + 2, 1)
        moveDict[f"U{i+1}'"] = (i*2 + 2, -1)
        moveDict[f"D{i+1}"] = (i*2 + 3, 1)
        moveDict[f"D{i+1}'"] = (i*2 + 3, -1)

def generate_cryptographic_cube_order():
    """Generate cryptographically secure random cube order between 8 and 100"""
    return secrets.randbelow(93) + 8  # 8 to 100 inclusive

def generate_cryptographic_num_moves():
    """Generate cryptographically secure random number of moves between 256 and 65536"""
    return secrets.randbelow(65281) + 256  # 256 to 65536 inclusive

def generate_cryptographic_padding_chars():
    """Generate cryptographically secure random padding characters"""
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?~"
    return ''.join(secrets.choice(charset) for _ in range(secrets.randbelow(100) + 50))

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


def initCube(cubeString, order):
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
                # Use cryptographic randomness for padding
                charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?~"
                ch = secrets.choice(charset)
            cube_data.append(ch)
        cubes.append(Cube(order, cube_data))
    return cubes


def cubeToString(cube):
    return ''.join(cube.cube)


def generateCryptographicMoves(numMoves, cube_order):
    """Generate cryptographically secure random moves"""
    moves = list(moveDict.keys())
    cryptographic_moves = []
    
    for _ in range(numMoves):
        # Use secrets module for cryptographic randomness
        move = secrets.choice(moves)
        cryptographic_moves.append(move)
    
    return cryptographic_moves


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


def encrypt_with_full_cryptographic_randomness(cubes):
    """
    Encrypt each cube with full cryptographic randomness
    
    Args:
        cubes: List of cubes to encrypt
    
    Returns:
        Tuple of (encrypted_cubes, encryption_parameters)
    """
    encrypted_cubes = []
    all_encryption_params = []
    
    for i, cube in enumerate(cubes):
        # Generate unique cryptographic random parameters for each cube
        cube_order = generate_cryptographic_cube_order()
        num_moves = generate_cryptographic_num_moves()
        
        # Reinitialize move dictionary for this cube's order
        initialize_move_dict(cube_order)
        
        # Generate cryptographic random moves
        moves = generateCryptographicMoves(num_moves, cube_order)
        
        # Encrypt the cube
        encrypted_cube = encryptCube(cube, moves)
        encrypted_cubes.append(encrypted_cube)
        
        # Store encryption parameters
        encryption_params = {
            'cube_order': cube_order,
            'num_moves': num_moves,
            'moves': moves,
            'original_cube_size': len(cube.cube)
        }
        all_encryption_params.append(encryption_params)
        
        print(f"Cube {i} encrypted with order {cube_order}, {num_moves} cryptographically random moves")
    
    return encrypted_cubes, all_encryption_params


def main():
    parser = argparse.ArgumentParser(description="Fully Cryptographically Random Cube Encryption and Decryption Tool")
    parser.add_argument("-mode", choices=["encrypt", "decrypt"], required=True, 
                       help="Operation mode: encrypt or decrypt")
    parser.add_argument("-s", "--string", type=str, help="String to encrypt/decrypt")
    parser.add_argument("-f", "--file", type=str, help="File to read input string from")
    parser.add_argument("-k", "--key", type=str, required=True, help="Key file to save/load encryption keys")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file to save the result")
    
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

    if args.mode == "encrypt":
        print("Generating cryptographically secure random parameters...")
        
        # For encryption, we'll use a base order to initialize the first cube
        # Each cube will have its own random order during actual encryption
        base_order = generate_cryptographic_cube_order()
        initialize_move_dict(base_order)
        
        # Initialize cubes with base order (will be changed per cube during encryption)
        cubes = initCube(inputString, base_order)
        
        # Encrypt cubes with full cryptographic randomness
        encrypted_cubes, encryption_params = encrypt_with_full_cryptographic_randomness(cubes)
        
        # Add some random padding to increase security
        padding = generate_cryptographic_padding_chars()
        print(f"Added {len(padding)} cryptographically random padding characters")
        
        # Save keys and encrypted data
        key_data = {
            'encryption_parameters': encryption_params,
            'padding': padding,
            'num_cubes': len(cubes),
            'metadata': {
                'encryption_date': str(os.path.getctime(__file__)),
                'full_cryptographic_randomness': True,
                'version': '4.0'
            }
        }
        
        with open(args.key, 'w') as kf:
            json.dump(key_data, kf, indent=2)

        with open(args.output, 'w') as of:
            for cube in encrypted_cubes:
                of.write(cubeToString(cube))
            # Add padding to the end
            of.write(padding)

        print(f"\nEncryption complete!")
        print(f"Encrypted {len(cubes)} cubes with fully random parameters:")
        for i, params in enumerate(encryption_params):
            print(f"  Cube {i}: order={params['cube_order']}, moves={params['num_moves']}")
        print(f"Output: {args.output}")
        print(f"Keys: {args.key}")

    elif args.mode == "decrypt":
        try:
            with open(args.key, 'r') as kf:
                key_data = json.load(kf)
            
            encryption_params = key_data['encryption_parameters']
            padding = key_data.get('padding', '')
            
        except Exception as e:
            print(f"Error reading key file: {e}")
            exit(1)

        # Read encrypted data (remove padding)
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
        else:
            encrypted_data = args.string
            
        # Remove padding if present
        if padding and encrypted_data.endswith(padding):
            encrypted_data = encrypted_data[:-len(padding)]

        print(f"Decrypting {len(encryption_params)} cubes...")
        
        decrypted_cubes = []
        total_chars_processed = 0
        
        for i, params in enumerate(encryption_params):
            cube_order = params['cube_order']
            moves = params['moves']
            original_size = params['original_cube_size']
            
            # Initialize move dictionary for this cube's order
            initialize_move_dict(cube_order)
            
            # Extract the portion of encrypted data for this cube
            cube_data = encrypted_data[total_chars_processed:total_chars_processed + original_size]
            total_chars_processed += original_size
            
            if len(cube_data) < original_size:
                print(f"Warning: Not enough data for cube {i}, expected {original_size}, got {len(cube_data)}")
                break
                
            # Create and decrypt cube
            cube = Cube(cube_order, cube_data)
            decrypted_cube = decryptCube(cube, moves)
            decrypted_cubes.append(decrypted_cube)
            
            print(f"Cube {i} decrypted with order {cube_order}, {len(moves)} moves")

        with open(args.output, 'w') as of:
            for cube in decrypted_cubes:
                of.write(cubeToString(cube))

        print(f"Decryption complete! Output: {args.output}")


if __name__ == "__main__":
    main()
