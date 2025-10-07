# encoding:utf-8
# @file CubeEncrypt.py
# @brief Cube encryption and decryption tool
# @author Dc-3387
# @date 2024-06-20
# @version 1.0
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

# ------------------------------------
# Modify #1 at 2024-06-20 21:50:00 CST
# Original framework: Dc-3387
# Core rotation logic debugging & redesign: DeepSeek V3 AI Assistant
# ------------------------------------

import random
import copy
import argparse
import json

# Face mapping dictionary
FaceDict = {
    "F": 0,  # Front
    "T": 1,  # Top
    "B": 2,  # Back
    "D": 3,  # Down
    "L": 4,  # Left
    "R": 5   # Right
}

# Dictionary mapping move notations to (layer, direction) tuples
# Supports up to 7x7 cube (order 7)
moveDict = {
    "L1": (0, 1), "L1'": (0, -1), "R1": (1, 1), "R1'": (1, -1),
    "U1": (2, 1), "U1'": (2, -1), "D1": (3, 1), "D1'": (3, -1),
    "L2": (4, 1), "L2'": (4, -1), "R2": (5, 1), "R2'": (5, -1),
    "U2": (6, 1), "U2'": (6, -1), "D2": (7, 1), "D2'": (7, -1),
    "L3": (8, 1), "L3'": (8, -1), "R3": (9, 1), "R3'": (9, -1),
    "U3": (10, 1), "U3'": (10, -1), "D3": (11, 1), "D3'": (11, -1),
    "L4": (12, 1), "L4'": (12, -1), "R4": (13, 1), "R4'": (13, -1),
    "U4": (14, 1), "U4'": (14, -1), "D4": (15, 1), "D4'": (15, -1),
    "L5": (16, 1), "L5'": (16, -1), "R5": (17, 1), "R5'": (17, -1),
    "U5": (18, 1), "U5'": (18, -1), "D5": (19, 1), "D5'": (19, -1),
    "L6": (20, 1), "L6'": (20, -1), "R6": (21, 1), "R6'": (21, -1),
    "U6": (22, 1), "U6'": (22, -1), "D6": (23, 1), "D6'": (23, -1),
    "L7": (24, 1), "L7'": (24, -1), "R7": (25, 1), "R7'": (25, -1),
    "U7": (26, 1), "U7'": (26, -1), "D7": (27, 1), "D7'": (27, -1)
}

class Cube:
    """
    Represents a virtual Rubik's cube for encryption/decryption operations.
    Each face is a 2D grid of characters that can be rotated.
    """
    
    def __init__(self, order, cube_data=None):
        """
        Initialize cube with specified order.
        
        Args:
            order (int): Size of the cube (order x order x order)
            cube_data (list): Optional linear list of characters to initialize cube
        """
        self.order = order
        # Face sequence: Front, Top, Back, Down, Left, Right
        self.face_names = ["F", "T", "B", "D", "L", "R"]
        if cube_data:
            self.faces = self._linear_to_faces(cube_data)
        else:
            # Initialize empty faces
            self.faces = [[['' for _ in range(order)] for _ in range(order)] for _ in range(6)]
    
    def _linear_to_faces(self, linear_data):
        """
        Convert linear character list to 6-face 3D structure.
        
        Args:
            linear_data (list): Flat list of characters
            
        Returns:
            list: 3D list representing 6 faces of the cube
        """
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
        """
        Convert 6-face 3D structure back to linear character list.
        
        Returns:
            list: Flat list of characters in face order
        """
        n = self.order
        linear_data = []
        for face_idx in range(6):
            for row in range(n):
                for col in range(n):
                    linear_data.append(self.faces[face_idx][row][col])
        return linear_data
    
    def rotate_LR(self, which, direction):
        """
        Rotate left or right layers of the cube.
        
        Args:
            which (int): Layer index (0 = leftmost, order-1 = rightmost)
            direction (int): 1 for clockwise, -1 for counter-clockwise
        """
        n = self.order
        if which < 0 or which >= n:
            return
            
        # Face indices: 0=F, 1=T, 2=B, 3=D, 4=L, 5=R
        if direction == 1:  # Clockwise rotation
            # Save Front column
            temp = [self.faces[0][r][which] for r in range(n)]
            
            # Front <- Down (reversed)
            for r in range(n):
                self.faces[0][r][which] = self.faces[3][n-1-r][n-1-which]
            
            # Down <- Back
            for r in range(n):
                self.faces[3][n-1-r][n-1-which] = self.faces[2][r][n-1-which]
            
            # Back <- Top (reversed)
            for r in range(n):
                self.faces[2][r][n-1-which] = self.faces[1][n-1-r][which]
            
            # Top <- Front (from temp)
            for r in range(n):
                self.faces[1][r][which] = temp[r]
            
            # Rotate side face if applicable
            if which == 0:  # Left face (index 4)
                self._rotate_face(4, 1)
            elif which == n-1:  # Right face (index 5)
                self._rotate_face(5, 1)
                
        else:  # Counter-clockwise rotation
            # Save Front column
            temp = [self.faces[0][r][which] for r in range(n)]
            
            # Front <- Top
            for r in range(n):
                self.faces[0][r][which] = self.faces[1][r][which]
            
            # Top <- Back (reversed)
            for r in range(n):
                self.faces[1][r][which] = self.faces[2][n-1-r][n-1-which]
            
            # Back <- Down
            for r in range(n):
                self.faces[2][n-1-r][n-1-which] = self.faces[3][r][n-1-which]
            
            # Down <- Front (from temp, reversed)
            for r in range(n):
                self.faces[3][r][n-1-which] = temp[n-1-r]
            
            # Rotate side face if applicable
            if which == 0:  # Left face
                self._rotate_face(4, -1)
            elif which == n-1:  # Right face
                self._rotate_face(5, -1)
    
    def rotate_UD(self, which, direction):
        """
        Rotate up or down layers of the cube.
        
        Args:
            which (int): Layer index (0 = top, order-1 = bottom)
            direction (int): 1 for clockwise, -1 for counter-clockwise
        """
        n = self.order
        if which < 0 or which >= n:
            return
            
        # Face indices: 0=F, 1=T, 2=B, 3=D, 4=L, 5=R
        if direction == 1:  # Clockwise rotation
            # Save Front row
            temp = self.faces[0][which][:]
            
            # Front <- Right
            for c in range(n):
                self.faces[0][which][c] = self.faces[5][which][c]
            
            # Right <- Back
            for c in range(n):
                self.faces[5][which][c] = self.faces[2][which][c]
            
            # Back <- Left
            for c in range(n):
                self.faces[2][which][c] = self.faces[4][which][c]
            
            # Left <- Front (from temp)
            for c in range(n):
                self.faces[4][which][c] = temp[c]
            
            # Rotate top or bottom face if applicable
            if which == 0:  # Top face (index 1)
                self._rotate_face(1, 1)
            elif which == n-1:  # Down face (index 3)
                self._rotate_face(3, 1)
                
        else:  # Counter-clockwise rotation
            # Save Front row
            temp = self.faces[0][which][:]
            
            # Front <- Left
            for c in range(n):
                self.faces[0][which][c] = self.faces[4][which][c]
            
            # Left <- Back
            for c in range(n):
                self.faces[4][which][c] = self.faces[2][which][c]
            
            # Back <- Right
            for c in range(n):
                self.faces[2][which][c] = self.faces[5][which][c]
            
            # Right <- Front (from temp)
            for c in range(n):
                self.faces[5][which][c] = temp[c]
            
            # Rotate top or bottom face if applicable
            if which == 0:  # Top face
                self._rotate_face(1, -1)
            elif which == n-1:  # Down face
                self._rotate_face(3, -1)
    
    def _rotate_face(self, face_idx, direction):
        """
        Rotate a single face 90 degrees.
        
        Args:
            face_idx (int): Index of face to rotate (0-5)
            direction (int): 1 for clockwise, -1 for counter-clockwise
        """
        n = self.order
        if face_idx < 0 or face_idx >= 6:
            return
            
        face = [row[:] for row in self.faces[face_idx]]  # Copy current face
        new_face = [['' for _ in range(n)] for _ in range(n)]
        
        if direction == 1:  # Clockwise rotation
            for r in range(n):
                for c in range(n):
                    new_face[c][n-1-r] = face[r][c]
        else:  # Counter-clockwise rotation
            for r in range(n):
                for c in range(n):
                    new_face[n-1-c][r] = face[r][c]
        
        self.faces[face_idx] = new_face
    
    @property
    def cube(self):
        """Property accessor for linear cube data."""
        return self._faces_to_linear()
    
    @cube.setter
    def cube(self, value):
        """Property setter for linear cube data."""
        self.faces = self._linear_to_faces(value)


def initCube(cubeString, order=7):
    """
    Initialize cube models from input string.
    
    Args:
        cubeString (str): Input text to encrypt/decrypt
        order (int): Size of each cube
        
    Returns:
        list: List of Cube objects containing the data
    """
    cubeString = cubeString.replace(" ", "").replace("\n", "")
    totalChars = len(cubeString)
    charsPerCube = order * order * 6
    numCubes = (totalChars + charsPerCube - 1) // charsPerCube  # Ceiling division

    cubes = []
    for i in range(numCubes):
        cube_data = []
        for j in range(charsPerCube):
            charIndex = i * charsPerCube + j
            if charIndex < totalChars:
                ch = cubeString[charIndex]
            else:
                # Fill remaining space with random characters
                ch = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
            cube_data.append(ch)
        cubes.append(Cube(order, cube_data))
    return cubes


def cubeToString(cube):
    """
    Convert cube state to string representation.
    
    Args:
        cube (Cube): Cube object to convert
        
    Returns:
        str: String representation of cube state
    """
    return ''.join(cube.cube)


def generateRandomMoves(numMoves):
    """
    Generate random cube rotation moves for encryption.
    
    Args:
        numMoves (int): Number of random moves to generate
        
    Returns:
        list: List of move strings
    """
    moves = list(moveDict.keys())
    randomMoves = random.choices(moves, k=numMoves)
    return randomMoves


def applyMoves(cube, moves):
    """
    Apply a sequence of moves to a cube.
    
    Args:
        cube (Cube): Cube to rotate
        moves (list): List of move strings to apply
        
    Returns:
        Cube: Modified cube object
    """
    for move in moves:
        if move in moveDict:
            layer, direction = moveDict[move]
            if layer % 2 == 0:  # Left or Right moves
                which = layer // 2
                cube.rotate_LR(which, direction)
            else:  # Up or Down moves
                which = layer // 2
                cube.rotate_UD(which, direction)
    return cube


def decryptCube(cube, moves):
    """
    Decrypt a cube by reversing the encryption moves.
    
    Args:
        cube (Cube): Encrypted cube
        moves (list): List of moves used for encryption
        
    Returns:
        Cube: Decrypted cube
    """
    reverseMoves = []
    for move in reversed(moves):  # Reverse the order of moves
        if move.endswith("'"):
            # Counter-clockwise becomes clockwise
            reverseMove = move[:-1]
        else:
            # Clockwise becomes counter-clockwise
            reverseMove = move + "'"
        reverseMoves.append(reverseMove)
    
    # Apply the reversed moves to decrypt
    decryptedCube = applyMoves(copy.deepcopy(cube), reverseMoves)
    return decryptedCube


def encryptCube(cube, numMoves):
    """
    Encrypt a cube using random rotations.
    
    Args:
        cube (Cube): Cube to encrypt
        numMoves (int): Number of random moves for encryption
        
    Returns:
        tuple: (encrypted_cube, moves_used)
    """
    moves = generateRandomMoves(numMoves)
    encryptedCube = applyMoves(copy.deepcopy(cube), moves)
    return encryptedCube, moves


def main():
    """
    Main function handling command line interface.
    
    Usage examples:
        python CubeEncrypt.py -mode encrypt -s "text" -k keyfile.key -o output.msg
        python CubeEncrypt.py -mode decrypt -f input.msg -k keyfile.key -o output.txt
    """
    parser = argparse.ArgumentParser(description="Cube Encryption and Decryption Tool")
    parser.add_argument("-mode", choices=["encrypt", "decrypt"], required=True, 
                       help="Operation mode: encrypt or decrypt")
    parser.add_argument("-s", "--string", type=str, 
                       help="String to encrypt/decrypt")
    parser.add_argument("-f", "--file", type=str, 
                       help="File to read input string from")
    parser.add_argument("-k", "--key", type=str, required=True, 
                       help="Key file to save/load encryption keys")
    parser.add_argument("-o", "--output", type=str, required=True, 
                       help="Output file to save the result")
    parser.add_argument("-n", "--num_moves", type=int, default=20, 
                       help="Number of random moves for encryption (default: 20)")
    
    args = parser.parse_args()

    # Validate input arguments
    if not args.string and not args.file:
        print("Error: Either -s (string) or -f (file) must be provided.")
        exit(1)

    if args.string and args.file:
        print("Error: Only one of -s (string) or -f (file) should be provided.")
        exit(1)

    # Read input data
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            inputString = ''.join(line.strip() for line in lines)
    else:
        inputString = args.string

    # Initialize cubes
    order = 7  # Default cube order (7x7x7)
    cubes = initCube(inputString, order)

    if args.mode == "encrypt":
        allMoves = []
        print(f"Encrypting {len(cubes)} cube(s)...")
        
        for i, cube in enumerate(cubes):
            encryptedCube, moves = encryptCube(cube, args.num_moves)
            allMoves.append(moves)
            cube.cube = encryptedCube.cube
            print(f"Cube {i} encrypted with {len(moves)} moves")

        # Save keys and encrypted data
        with open(args.key, 'w') as kf:
            json.dump(allMoves, kf)

        with open(args.output, 'w') as of:
            for cube in cubes:
                of.write(cubeToString(cube) + "\n")

        print(f"Encryption complete. Output: {args.output}, Keys: {args.key}")

    elif args.mode == "decrypt":
        try:
            with open(args.key, 'r') as kf:
                allMoves = json.load(kf)
        except Exception as e:
            print(f"Error reading key file: {e}")
            exit(1)

        print(f"Decrypting {len(cubes)} cube(s) with {len(allMoves)} key(s)...")
        
        if len(allMoves) < len(cubes):
            print("Warning: Key file contains fewer keys than cubes. Some cubes may not be decrypted.")

        # Decrypt each cube with its corresponding key
        for i, cube in enumerate(cubes):
            if i < len(allMoves):
                moves = allMoves[i]
                decryptedCube = decryptCube(cube, moves)
                cube.cube = decryptedCube.cube
                print(f"Cube {i} decrypted with {len(moves)} moves")
            else:
                print(f"Skipping cube {i} - no key available")

        # Save decrypted data
        with open(args.output, 'w') as of:
            for cube in cubes:
                of.write(cubeToString(cube) + "\n")

        print(f"Decryption complete. Output: {args.output}")


if __name__ == "__main__":
    main()