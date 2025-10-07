# encoding:utf-8
# @file CubeKeyEncoder.py
# @brief Cube Encryption Key Encoder - Converts cube rotation moves to numeric codes
# @author DeepSeek AI Assistant
# @date 2024-06-20
# @version 1.0
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
# Description:
# This script encodes and decodes cube rotation moves between human-readable format
# and numeric codes. It provides multiple encoding schemes for different security requirements.

import json
import argparse
import base64

class CubeKeyEncoder:
    """
    Encodes and decodes cube rotation moves between human-readable format and numeric codes.
    Provides multiple encoding schemes for different security requirements.
    """
    
    # Enhanced move dictionary with numeric codes
    MOVE_ENCODING = {
        # Left moves: 0-27 (even numbers for clockwise, odd for counter-clockwise)
        "L1": 0, "L1'": 1, "L2": 2, "L2'": 3, "L3": 4, "L3'": 5,
        "L4": 6, "L4'": 7, "L5": 8, "L5'": 9, "L6": 10, "L6'": 11,
        "L7": 12, "L7'": 13,
        
        # Right moves: 14-27
        "R1": 14, "R1'": 15, "R2": 16, "R2'": 17, "R3": 18, "R3'": 19,
        "R4": 20, "R4'": 21, "R5": 22, "R5'": 23, "R6": 24, "R6'": 25,
        "R7": 26, "R7'": 27,
        
        # Up moves: 28-41
        "U1": 28, "U1'": 29, "U2": 30, "U2'": 31, "U3": 32, "U3'": 33,
        "U4": 34, "U4'": 35, "U5": 36, "U5'": 37, "U6": 38, "U6'": 39,
        "U7": 40, "U7'": 41,
        
        # Down moves: 42-55
        "D1": 42, "D1'": 43, "D2": 44, "D2'": 45, "D3": 46, "D3'": 47,
        "D4": 48, "D4'": 49, "D5": 50, "D5'": 51, "D6": 52, "D6'": 53,
        "D7": 54, "D7'": 55
    }
    
    # Reverse mapping for decoding
    CODE_DECODING = {v: k for k, v in MOVE_ENCODING.items()}
    
    def __init__(self, encoding_scheme="simple"):
        """
        Initialize the encoder with specified encoding scheme.
        
        Args:
            encoding_scheme (str): Encoding method - 'simple', 'base64', or 'xor'
        """
        self.encoding_scheme = encoding_scheme
        self.xor_key = 0xAA  # Simple XOR key for basic obfuscation
    
    def moves_to_codes(self, moves_list):
        """
        Convert list of move sequences to numeric codes.
        
        Args:
            moves_list (list): List of move sequences, each sequence is a list of moves
            
        Returns:
            list: List of encoded sequences
        """
        encoded_sequences = []
        
        for sequence in moves_list:
            encoded_sequence = []
            for move in sequence:
                if move in self.MOVE_ENCODING:
                    code = self.MOVE_ENCODING[move]
                    # Apply encoding scheme
                    if self.encoding_scheme == "xor":
                        code = code ^ self.xor_key
                    encoded_sequence.append(code)
                else:
                    print(f"Warning: Unknown move '{move}' skipped")
            
            encoded_sequences.append(encoded_sequence)
        
        return encoded_sequences
    
    def codes_to_moves(self, encoded_sequences):
        """
        Convert numeric codes back to move sequences.
        
        Args:
            encoded_sequences (list): List of encoded sequences
            
        Returns:
            list: List of original move sequences
        """
        decoded_sequences = []
        
        for encoded_sequence in encoded_sequences:
            decoded_sequence = []
            for code in encoded_sequence:
                # Reverse encoding scheme
                if self.encoding_scheme == "xor":
                    code = code ^ self.xor_key
                
                if code in self.CODE_DECODING:
                    decoded_sequence.append(self.CODE_DECODING[code])
                else:
                    print(f"Warning: Unknown code '{code}' skipped")
            
            decoded_sequences.append(decoded_sequence)
        
        return decoded_sequences
    
    def encode_to_base64(self, encoded_sequences):
        """
        Convert numeric codes to Base64 string for compact storage.
        
        Args:
            encoded_sequences (list): List of encoded sequences
            
        Returns:
            str: Base64 encoded string
        """
        # Flatten sequences and convert to bytes
        flat_codes = []
        for sequence in encoded_sequences:
            flat_codes.append(len(sequence))  # Store sequence length
            flat_codes.extend(sequence)
        
        # Convert to bytes
        byte_data = bytes(flat_codes)
        
        # Base64 encode
        return base64.b64encode(byte_data).decode('utf-8')
    
    def decode_from_base64(self, base64_string):
        """
        Convert Base64 string back to numeric codes.
        
        Args:
            base64_string (str): Base64 encoded string
            
        Returns:
            list: List of encoded sequences
        """
        # Base64 decode
        byte_data = base64.b64decode(base64_string)
        
        # Reconstruct sequences
        encoded_sequences = []
        index = 0
        
        while index < len(byte_data):
            seq_length = byte_data[index]
            index += 1
            
            sequence = list(byte_data[index:index + seq_length])
            encoded_sequences.append(sequence)
            index += seq_length
        
        return encoded_sequences
    
    def save_encoded_keys(self, encoded_sequences, output_file, format="json"):
        """
        Save encoded sequences to file.
        
        Args:
            encoded_sequences (list): Encoded sequences to save
            output_file (str): Output file path
            format (str): Output format - 'json' or 'base64'
        """
        if format == "base64":
            base64_data = self.encode_to_base64(encoded_sequences)
            with open(output_file, 'w') as f:
                f.write(base64_data)
            print(f"Encoded keys saved as Base64 to: {output_file}")
        
        else:  # JSON format
            data = {
                "encoding_scheme": self.encoding_scheme,
                "encoded_sequences": encoded_sequences,
                "metadata": {
                    "total_sequences": len(encoded_sequences),
                    "total_moves": sum(len(seq) for seq in encoded_sequences),
                    "encoder": "CubeKeyEncoder by DeepSeek AI Assistant"
                }
            }
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Encoded keys saved as JSON to: {output_file}")
    
    def load_encoded_keys(self, input_file):
        """
        Load encoded sequences from file.
        
        Args:
            input_file (str): Input file path
            
        Returns:
            list: Encoded sequences
        """
        with open(input_file, 'r') as f:
            content = f.read().strip()
        
        # Try to detect format
        if content.startswith('{'):
            # JSON format
            data = json.loads(content)
            self.encoding_scheme = data.get("encoding_scheme", "simple")
            return data["encoded_sequences"]
        else:
            # Base64 format
            return self.decode_from_base64(content)


def main():
    """
    Command line interface for Cube Key Encoder.
    
    Usage examples:
        python CubeKeyEncoder.py encode -i keys.json -o encoded_keys.json
        python CubeKeyEncoder.py decode -i encoded_keys.json -o decoded_keys.json
        python CubeKeyEncoder.py encode -i keys.json -o keys.b64 --format base64 --scheme xor
    """
    parser = argparse.ArgumentParser(description="Cube Key Encoder - Convert cube moves to numeric codes")
    parser.add_argument("action", choices=["encode", "decode"], help="Action to perform")
    parser.add_argument("-i", "--input", required=True, help="Input key file")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("--format", choices=["json", "base64"], default="json", 
                       help="Output format (default: json)")
    parser.add_argument("--scheme", choices=["simple", "base64", "xor"], default="simple",
                       help="Encoding scheme (default: simple)")
    
    args = parser.parse_args()
    
    # Initialize encoder
    encoder = CubeKeyEncoder(encoding_scheme=args.scheme)
    
    try:
        if args.action == "encode":
            # Load original moves
            with open(args.input, 'r') as f:
                original_moves = json.load(f)
            
            print(f"Encoding {len(original_moves)} move sequences...")
            
            # Encode moves
            encoded_sequences = encoder.moves_to_codes(original_moves)
            
            # Save encoded data
            encoder.save_encoded_keys(encoded_sequences, args.output, args.format)
            
            # Print statistics
            total_moves = sum(len(seq) for seq in original_moves)
            print(f"Encoded {total_moves} moves using {args.scheme} scheme")
            
        else:  # decode
            # Load encoded sequences
            encoded_sequences = encoder.load_encoded_keys(args.input)
            
            print(f"Decoding {len(encoded_sequences)} encoded sequences...")
            
            # Decode to moves
            decoded_moves = encoder.codes_to_moves(encoded_sequences)
            
            # Save decoded moves
            with open(args.output, 'w') as f:
                json.dump(decoded_moves, f, indent=2)
            
            # Print statistics
            total_moves = sum(len(seq) for seq in decoded_moves)
            print(f"Decoded {total_moves} moves from {args.scheme} scheme")
            print(f"Decoded keys saved to: {args.output}")
    
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()