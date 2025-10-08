# encoding:utf-8
# @file CubeEncryptUI_EN.py
# @brief User Interface for Cube Encryption and Decryption Tool (English Version)
# @author Assistant
# @date 2024-06-20
# @version 2.1

import os
import json
import random
import tempfile
import shutil
import subprocess
import sys
from datetime import datetime
import math

class CubeEncryptUI_EN:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.script_dir, "temp_cube_files")
        self.output_dir = os.path.join(self.script_dir, "cube_results")
        self.cube_utils_path = os.path.join(self.script_dir, "CubeUtils.py")
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories"""
        for directory in [self.temp_dir, self.output_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def _clean_temp_files(self):
        """Clean temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
    
    def _get_user_input(self, prompt, default=None, input_type=str):
        """Get user input with validation"""
        while True:
            try:
                if default is not None:
                    user_input = input(f"{prompt} [{default}]: ").strip()
                    if not user_input:
                        return default
                else:
                    user_input = input(f"{prompt}: ").strip()
                
                return input_type(user_input)
            except ValueError:
                print("Invalid input format, please try again.")
            except KeyboardInterrupt:
                print("\nProgram terminated by user.")
                sys.exit(0)
    
    def _generate_random_cube_orders(self, text_length, num_cubes=None):
        """Generate random cube orders with cryptographic security"""
        if num_cubes is None:
            # Automatically determine number of cubes based on text length
            avg_chars_per_cube = 2000  # Average characters per cube
            num_cubes = max(1, math.ceil(text_length / avg_chars_per_cube))
        
        cube_orders = []
        remaining_chars = text_length
        
        for i in range(num_cubes):
            if remaining_chars <= 0:
                break
                
            # Dynamically calculate appropriate cube order
            # Cube capacity = order^2 * 6
            # Target fill ratio: 60%-90%
            target_fill_ratio = random.uniform(0.6, 0.9)
            target_capacity = max(remaining_chars, 54)  # Minimum capacity for 3x3 cube (3*3*6=54)
            target_capacity = target_capacity / target_fill_ratio
            
            # Calculate cube order: order = sqrt(capacity/6)
            suggested_order = max(3, math.isqrt(int(target_capacity / 6)))
            
            # Add random variation ±30% around suggested order, but ensure min <= max
            min_order = max(3, int(suggested_order * 0.7))
            max_order = min(50, int(suggested_order * 1.3))  # Maximum 50th order
            
            # Ensure min_order is not greater than max_order
            if min_order > max_order:
                min_order, max_order = max_order, min_order
            # Ensure at least 3rd order
            min_order = max(3, min_order)
            max_order = max(min_order, max_order)
            
            cube_order = random.randint(min_order, max_order)
            cube_capacity = cube_order * cube_order * 6
            
            # Actual characters for this cube
            chars_for_this_cube = min(remaining_chars, cube_capacity)
            remaining_chars -= chars_for_this_cube
            
            cube_orders.append({
                'order': cube_order,
                'capacity': cube_capacity,
                'actual_chars': chars_for_this_cube,
                'fill_ratio': chars_for_this_cube / cube_capacity if cube_capacity > 0 else 0
            })
            
            print(f"  Generated cube {i+1}: order={cube_order}, capacity={cube_capacity}, "
                  f"chars={chars_for_this_cube}, fill_rate={cube_orders[-1]['fill_ratio']:.1%}")
        
        return cube_orders
    
    def _preprocess_string_variable_cubes(self, text, cube_orders):
        """Preprocess string and split according to different cube sizes"""
        chunks = []
        current_pos = 0
        
        for i, cube_info in enumerate(cube_orders):
            cube_order = cube_info['order']
            capacity = cube_info['capacity']
            actual_chars = cube_info['actual_chars']
            
            # Extract string segment for this cube
            chunk = text[current_pos:current_pos + actual_chars]
            current_pos += actual_chars
            
            # If string length is insufficient, leave empty spaces (handled by program)
            chunks.append({
                'text': chunk,
                'order': cube_order,
                'capacity': capacity,
                'actual_length': len(chunk)
            })
            
            if current_pos >= len(text):
                break
        
        return chunks
    
    def _preprocess_string_fixed_cube(self, text, cube_order):
        """Preprocess string using fixed cube size"""
        chunk_size = cube_order * cube_order * 6
        chunks = []
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            chunks.append({
                'text': chunk,
                'order': cube_order,
                'capacity': chunk_size,
                'actual_length': len(chunk)
            })
        
        return chunks
    
    def _generate_safe_cube_orders(self, text_length, num_cubes=None):
        """Safe fallback method for generating cube orders"""
        if num_cubes is None:
            num_cubes = max(1, math.ceil(text_length / 2000))
        
        cube_orders = []
        remaining_chars = text_length
        
        # Predefined safe order ranges
        safe_orders = [3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 20, 25, 30, 35, 40, 45, 50]
        
        for i in range(num_cubes):
            if remaining_chars <= 0:
                break
            
            # Choose an appropriate order based on remaining characters
            if remaining_chars > 10000:
                order = random.choice([o for o in safe_orders if o >= 20])
            elif remaining_chars > 5000:
                order = random.choice([o for o in safe_orders if o >= 15])
            elif remaining_chars > 1000:
                order = random.choice([o for o in safe_orders if o >= 10])
            elif remaining_chars > 500:
                order = random.choice([o for o in safe_orders if o >= 8])
            else:
                order = random.choice([o for o in safe_orders if o >= 3])
            
            capacity = order * order * 6
            chars_for_this_cube = min(remaining_chars, capacity)
            remaining_chars -= chars_for_this_cube
            
            cube_orders.append({
                'order': order,
                'capacity': capacity,
                'actual_chars': chars_for_this_cube,
                'fill_ratio': chars_for_this_cube / capacity if capacity > 0 else 0
            })
        
        return cube_orders
    
    def _generate_random_parameters(self):
        """Generate cryptographically random parameters"""
        # Number of moves: random between 50-500
        num_moves = random.randint(50, 500)
        
        # Key pool multiplier: random between 3-10
        key_pool_multiplier = random.randint(3, 10)
        
        return num_moves, key_pool_multiplier
    
    def _run_cube_utils(self, args):
        """Execute CubeUtils.py program"""
        try:
            cmd = [sys.executable, self.cube_utils_path] + args
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode != 0:
                print(f"Execution error: {result.stderr}")
                return False
            
            print(result.stdout)
            return True
        except Exception as e:
            print(f"Error executing program: {e}")
            return False
    
    def encrypt_ui(self):
        """Encryption user interface"""
        print("\n" + "="*50)
        print("Cube Encryption Tool - Variable Cube Size Support")
        print("="*50)
        
        # Get input method
        print("\nSelect input method:")
        print("1. Direct text input")
        print("2. Read from file")
        choice = self._get_user_input("Please choose (1/2)", "1", int)
        
        if choice == 1:
            text = self._get_user_input("Please enter the text to encrypt")
        else:
            file_path = self._get_user_input("Please enter file path")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                print(f"Failed to read file: {e}")
                return
        
        if not text:
            print("Input text is empty, cannot encrypt.")
            return
        
        text_length = len(text)
        print(f"\nInput text length: {text_length} characters")
        
        # Cube size selection
        print("\nSelect cube size strategy:")
        print("1. Cryptographic random sizes (Recommended) - Different sizes for each cube")
        print("2. Fixed size - All cubes use same order")
        print("3. Manual specification - Specify each cube size individually")
        print("4. Safe random sizes - Uses predefined safe orders")
        size_choice = self._get_user_input("Please choose (1/2/3/4)", "4", int)
        
        cube_orders = []
        
        if size_choice == 1:
            # Cryptographic random sizes
            print("\nGenerating random cube sizes...")
            try:
                cube_orders = self._generate_random_cube_orders(text_length)
            except Exception as e:
                print(f"Error generating random cube sizes: {e}")
                print("Falling back to safe cube size generation...")
                cube_orders = self._generate_safe_cube_orders(text_length)
            
        elif size_choice == 2:
            # Fixed size
            cube_order = self._get_user_input("Please enter cube order", "25", int)
            # Generate fixed-size cube list
            chunk_size = cube_order * cube_order * 6
            num_cubes = math.ceil(text_length / chunk_size)
            for i in range(num_cubes):
                actual_chars = min(chunk_size, text_length - i * chunk_size)
                cube_orders.append({
                    'order': cube_order,
                    'capacity': chunk_size,
                    'actual_chars': actual_chars,
                    'fill_ratio': actual_chars / chunk_size
                })
                
        elif size_choice == 3:
            # Manual specification
            num_cubes = self._get_user_input("How many cubes are needed", "1", int)
            for i in range(num_cubes):
                order = self._get_user_input(f"Please enter order for cube {i+1}", "25", int)
                capacity = order * order * 6
                # Distribute characters evenly
                avg_chars = text_length // num_cubes
                if i == num_cubes - 1:  # Last cube gets remaining characters
                    actual_chars = text_length - (avg_chars * (num_cubes - 1))
                else:
                    actual_chars = avg_chars
                
                cube_orders.append({
                    'order': order,
                    'capacity': capacity,
                    'actual_chars': min(actual_chars, capacity),
                    'fill_ratio': min(actual_chars, capacity) / capacity
                })
        
        elif size_choice == 4:
            # Safe random sizes
            print("\nGenerating safe random cube sizes...")
            cube_orders = self._generate_safe_cube_orders(text_length)
        
        # Display cube configuration
        print(f"\nCube Configuration:")
        total_capacity = 0
        total_actual = 0
        for i, cube_info in enumerate(cube_orders):
            print(f"  Cube {i+1}: Order={cube_info['order']}, Capacity={cube_info['capacity']}, "
                  f"Actual Chars={cube_info['actual_chars']}, Fill Rate={cube_info['fill_ratio']:.1%}")
            total_capacity += cube_info['capacity']
            total_actual += cube_info['actual_chars']
        
        print(f"  Total: {len(cube_orders)} cubes, Total Capacity={total_capacity}, "
              f"Total Characters={total_actual}, Overall Fill Rate={total_actual/total_capacity:.1%}")
        
        # Verify we can handle all text
        if total_actual < text_length:
            print(f"Warning: Only {total_actual} out of {text_length} characters will be encrypted!")
            proceed = self._get_user_input("Continue anyway? (y/n)", "y")
            if proceed.lower() != 'y':
                return
        
        # Other parameter selection
        print("\nSelect other encryption parameters:")
        print("1. Use random parameters (Recommended)")
        print("2. Manual parameter setting")
        param_choice = self._get_user_input("Please choose (1/2)", "1", int)
        
        if param_choice == 1:
            num_moves, key_pool_multiplier = self._generate_random_parameters()
            print(f"Generated random parameters:")
            print(f"  Number of moves: {num_moves}")
            print(f"  Key pool multiplier: {key_pool_multiplier}")
        else:
            num_moves = self._get_user_input("Please enter number of moves", "256", int)
            key_pool_multiplier = self._get_user_input("Please enter key pool multiplier", "6", int)
        
        # Key selection method
        print("\nSelect key selection method:")
        print("1. random - Random selection")
        print("2. sequential - Sequential selection")
        print("3. hash_based - Hash-based selection")
        selection_methods = {"1": "random", "2": "sequential", "3": "hash_based"}
        selection_choice = self._get_user_input("Please choose (1/2/3)", "1")
        selection_method = selection_methods.get(selection_choice, "random")
        
        # Preprocess string
        print("\nPreprocessing string...")
        if size_choice == 1 or size_choice == 3 or size_choice == 4:
            chunks = self._preprocess_string_variable_cubes(text, cube_orders)
        else:
            chunks = self._preprocess_string_fixed_cube(text, cube_orders[0]['order'])
        
        print(f"String split into {len(chunks)} cube chunks")
        
        # Clean temporary directory
        self._clean_temp_files()
        
        # Create temporary files and encrypt each chunk
        encrypted_chunks = []
        key_files = []
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, chunk_info in enumerate(chunks):
            chunk = chunk_info['text']
            cube_order = chunk_info['order']
            
            print(f"\nProcessing cube chunk {i+1}/{len(chunks)}...")
            print(f"  Cube order: {cube_order}, Characters: {len(chunk)}")
            
            # Create temporary input file
            input_file = os.path.join(self.temp_dir, f"chunk_{i}_input.txt")
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            
            # Create temporary output file
            output_file = os.path.join(self.temp_dir, f"chunk_{i}_encrypted.txt")
            
            # Create temporary key file
            key_file = os.path.join(self.temp_dir, f"chunk_{i}_key.json")
            
            # Build arguments
            args = [
                "-mode", "encrypt",
                "-f", input_file,
                "-k", key_file,
                "-l", str(cube_order),
                "-o", output_file,
                "-n", str(num_moves),
                "--key_pool_size", str(key_pool_multiplier),
                "--selection", selection_method
            ]
            
            # Execute encryption
            if self._run_cube_utils(args):
                # Read encryption result
                with open(output_file, 'r', encoding='utf-8') as f:
                    encrypted_text = f.read().strip()
                
                encrypted_chunks.append({
                    'encrypted_text': encrypted_text,
                    'cube_order': cube_order,
                    'original_length': len(chunk)
                })
                key_files.append(key_file)
                
                print(f"Cube chunk {i+1} encrypted successfully")
            else:
                print(f"Cube chunk {i+1} encryption failed")
                return
        
        # Merge encryption results and keys
        print("\nMerging encryption results...")
        
        # Create final output file
        final_output = {
            "metadata": {
                "timestamp": timestamp,
                "total_chunks": len(encrypted_chunks),
                "original_text_length": text_length,
                "encryption_parameters": {
                    "num_moves": num_moves,
                    "key_pool_multiplier": key_pool_multiplier,
                    "selection_method": selection_method
                },
                "cube_strategy": "variable" if size_choice in [1, 4] else "fixed"
            },
            "encrypted_data": encrypted_chunks,
            "key_data": []
        }
        
        # Merge key data
        for i, key_file in enumerate(key_files):
            with open(key_file, 'r', encoding='utf-8') as f:
                key_data = json.load(f)
            
            final_output["key_data"].append({
                "chunk_index": i,
                "cube_order": encrypted_chunks[i]['cube_order'],
                "key_info": key_data
            })
        
        # Save final file
        final_filename = f"encrypted_result_{timestamp}.cube"
        final_filepath = os.path.join(self.output_dir, final_filename)
        
        with open(final_filepath, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        # Clean temporary files
        self._clean_temp_files()
        
        print(f"\nEncryption completed!")
        print(f"Final file: {final_filepath}")
        print(f"Total cubes encrypted: {len(encrypted_chunks)}")
        print(f"Cube orders used: {[chunk['cube_order'] for chunk in encrypted_chunks]}")
    
    def decrypt_ui(self):
        """Decryption user interface"""
        print("\n" + "="*50)
        print("Cube Decryption Tool")
        print("="*50)
        
        # Get encrypted file
        encrypted_file = self._get_user_input("Please enter encrypted file path (.cube file)")
        
        try:
            with open(encrypted_file, 'r', encoding='utf-8') as f:
                encrypted_data = json.load(f)
        except Exception as e:
            print(f"Failed to read encrypted file: {e}")
            return
        
        # Display file information
        metadata = encrypted_data.get("metadata", {})
        print(f"\nFile Information:")
        print(f"  Timestamp: {metadata.get('timestamp', 'Unknown')}")
        print(f"  Original text length: {metadata.get('original_text_length', 'Unknown')}")
        print(f"  Number of cube chunks: {metadata.get('total_chunks', 0)}")
        print(f"  Cube strategy: {metadata.get('cube_strategy', 'Unknown')}")
        
        enc_params = metadata.get('encryption_parameters', {})
        print(f"  Number of moves: {enc_params.get('num_moves', 'Unknown')}")
        print(f"  Key selection: {enc_params.get('selection_method', 'Unknown')}")
        
        # Clean temporary directory
        self._clean_temp_files()
        
        # Decrypt each chunk
        decrypted_chunks = []
        encrypted_chunks = encrypted_data.get("encrypted_data", [])
        key_data_list = encrypted_data.get("key_data", [])
        
        print(f"\nStarting decryption of {len(encrypted_chunks)} cube chunks...")
        
        for i, encrypted_chunk_info in enumerate(encrypted_chunks):
            encrypted_chunk = encrypted_chunk_info['encrypted_text']
            cube_order = encrypted_chunk_info['cube_order']
            original_length = encrypted_chunk_info['original_length']
            
            print(f"Decrypting cube chunk {i+1}/{len(encrypted_chunks)}...")
            print(f"  Cube order: {cube_order}, Original characters: {original_length}")
            
            # Create temporary encrypted file
            encrypted_file_temp = os.path.join(self.temp_dir, f"chunk_{i}_encrypted.txt")
            with open(encrypted_file_temp, 'w', encoding='utf-8') as f:
                f.write(encrypted_chunk)
            
            # Create temporary key file
            key_file_temp = os.path.join(self.temp_dir, f"chunk_{i}_key.json")
            chunk_key_data = None
            
            # Find corresponding key data
            for key_item in key_data_list:
                if key_item.get("chunk_index") == i:
                    chunk_key_data = key_item.get("key_info")
                    break
            
            if not chunk_key_data:
                print(f"Warning: No key data found for cube chunk {i}")
                continue
            
            # Save key file
            with open(key_file_temp, 'w', encoding='utf-8') as f:
                json.dump(chunk_key_data, f, indent=2, ensure_ascii=False)
            
            # Create temporary output file
            decrypted_file_temp = os.path.join(self.temp_dir, f"chunk_{i}_decrypted.txt")
            
            # Build decryption arguments
            args = [
                "-mode", "decrypt",
                "-f", encrypted_file_temp,
                "-k", key_file_temp,
                "-l", str(cube_order),
                "-o", decrypted_file_temp
            ]
            
            # Execute decryption
            if self._run_cube_utils(args):
                # Read decryption result
                with open(decrypted_file_temp, 'r', encoding='utf-8') as f:
                    decrypted_text = f.read().strip()
                
                # Truncate based on original length (handle possible padding)
                if original_length < len(decrypted_text):
                    decrypted_text = decrypted_text[:original_length]
                
                decrypted_chunks.append(decrypted_text)
                print(f"Cube chunk {i+1} decrypted successfully")
            else:
                print(f"Cube chunk {i+1} decryption failed")
        
        # Merge decryption results
        final_decrypted_text = ''.join(decrypted_chunks)
        
        # Save decryption result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"decrypted_result_{timestamp}.txt"
        output_filepath = os.path.join(self.output_dir, output_filename)
        
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(final_decrypted_text)
        
        # Clean temporary files
        self._clean_temp_files()
        
        print(f"\nDecryption completed!")
        print(f"Decryption result: {output_filepath}")
        print(f"Decrypted text length: {len(final_decrypted_text)} characters")
        print(f"\nDecrypted content preview (first 500 characters):")
        print(final_decrypted_text[:500] + ("..." if len(final_decrypted_text) > 500 else ""))
    
    def brute_force_ui(self):
        """Brute force user interface"""
        print("\n" + "="*50)
        print("Cube Brute Force Tool")
        print("="*50)
        
        print("Note: Brute force requires key file and may take considerable time")
        print("For variable-size cubes, each cube's order must be specified")
        
        # Get input
        encrypted_file = self._get_user_input("Please enter encrypted file path (.cube file)")
        
        try:
            with open(encrypted_file, 'r', encoding='utf-8') as f:
                encrypted_data = json.load(f)
        except Exception as e:
            print(f"Failed to read encrypted file: {e}")
            return
        
        # Display cube information
        encrypted_chunks = encrypted_data.get("encrypted_data", [])
        print(f"File contains {len(encrypted_chunks)} cube chunks")
        
        for i, chunk in enumerate(encrypted_chunks):
            print(f"Cube {i+1}: Order={chunk['cube_order']}, Original Length={chunk['original_length']}")
        
        max_attempts = self._get_user_input("Please enter maximum attempts", "10", int)
        
        # Clean temporary directory
        self._clean_temp_files()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(self.output_dir, f"bruteforce_results_{timestamp}")
        
        # Perform brute force on each cube individually
        key_data_list = encrypted_data.get("key_data", [])
        
        for i, encrypted_chunk_info in enumerate(encrypted_chunks):
            print(f"\nBrute forcing cube chunk {i+1}/{len(encrypted_chunks)}...")
            
            encrypted_chunk = encrypted_chunk_info['encrypted_text']
            cube_order = encrypted_chunk_info['cube_order']
            
            # Create temporary encrypted file
            temp_encrypted = os.path.join(self.temp_dir, f"chunk_{i}_encrypted.txt")
            with open(temp_encrypted, 'w', encoding='utf-8') as f:
                f.write(encrypted_chunk)
            
            # Find corresponding key file
            key_file = None
            for key_item in key_data_list:
                if key_item.get("chunk_index") == i:
                    # Create temporary key file
                    key_file_temp = os.path.join(self.temp_dir, f"chunk_{i}_key.json")
                    with open(key_file_temp, 'w', encoding='utf-8') as f:
                        json.dump(key_item.get("key_info"), f, indent=2)
                    key_file = key_file_temp
                    break
            
            if not key_file:
                print(f"Warning: No key file found for cube chunk {i}, skipping")
                continue
            
            # Build arguments
            chunk_results_dir = os.path.join(results_dir, f"chunk_{i}")
            
            args = [
                "-mode", "bruteforce",
                "-f", temp_encrypted,
                "-k", key_file,
                "-l", str(cube_order),
                "--max_attempts", str(max_attempts),
                "--results_dir", chunk_results_dir
            ]
            
            # Execute brute force
            if self._run_cube_utils(args):
                print(f"Cube chunk {i+1} brute force completed")
            else:
                print(f"Cube chunk {i+1} brute force failed")
        
        # Clean temporary files
        self._clean_temp_files()
        
        print(f"\nBrute force completed!")
        print(f"Results saved to: {results_dir}")
    
    def main_menu(self):
        """Main menu interface"""
        while True:
            print("\n" + "="*50)
            print("Cube Encryption & Decryption Tool - Main Menu")
            print("="*50)
            print("1. Encrypt Text/File")
            print("2. Decrypt File")
            print("3. Brute Force")
            print("4. Exit")
            print("="*50)
            
            choice = self._get_user_input("Please select operation", "1")
            
            if choice == "1":
                self.encrypt_ui()
            elif choice == "2":
                self.decrypt_ui()
            elif choice == "3":
                self.brute_force_ui()
            elif choice == "4":
                print("Thank you for using Cube Encryption & Decryption Tool!")
                break
            else:
                print("Invalid selection, please try again.")

if __name__ == "__main__":
    ui = CubeEncryptUI_EN()
    ui.main_menu()